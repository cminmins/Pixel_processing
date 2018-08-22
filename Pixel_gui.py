import sys, os, glob
import pydicom
import numpy as np
import skimage.io as sk
from skimage import data, io, filters, color

from PyQt5 import QtCore, uic, QtWidgets, QtGui
gui = uic.loadUiType("untitled.ui")[0]


class Pixel_gui(QtWidgets.QMainWindow, gui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dcmfilect = ''
        self.dcmfilemr = ''
        self.ct_pix = ''
        self.mr_pix = ''

        ## 디렉토리 열고 dcm 리스트까지 추가    
        dir_name = ''
        self.Button_open.clicked.connect(self.opendirectory)
        self.List_directory.itemClicked.connect(self.choosedirectory)

        ## dcm 파일 클릭하면 View에 이미지 띄우기
        self.List_CT.itemClicked.connect(self.selectimageCT)
        self.List_MR.itemClicked.connect(self.selectimageMR)

        self.qlabel_CT.mousePressEvent = self.cropCT
        self.qlabel_MR.mousePressEvent = self.cropMR
        self.qlabel_overay.mousePressEvent = self.overlay

    def cropCT(self, event):
        x = event.pos().x()
        y = event.pos().y()
        CTcrop_x = int(x * 4)
        CTcrop_y = int(y * 4)

        CTcrop_image = np.copy(self.dcmfilect.pixel_array[CTcrop_y:CTcrop_y+800, CTcrop_x:CTcrop_x+700])
        CTcrop_image = (CTcrop_image / 16).astype(np.uint8)
        CTcrop_image = np.require(CTcrop_image, np.uint8, 'C')
        h, w = CTcrop_image.shape
        result = QtGui.QImage(CTcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        self.ct_pix = pixmap
        self.qlabel_CT_crop.setPixmap(pixmap)

    def cropMR(self, event):
        x = event.pos().x()
        y = event.pos().y()

        MRcrop_image = np.copy(self.dcmfilemr.pixel_array[y:y+200, x:x+180])
        MRcrop_image = (MRcrop_image / 16).astype(np.uint8)
        MRcrop_image = np.require(MRcrop_image, np.uint8, 'C')
        h, w = MRcrop_image.shape
        result = QtGui.QImage(MRcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        pixmap = pixmap.scaled(self.qlabel_MR_crop.width(), self.qlabel_MR_crop.height(), QtCore.Qt.KeepAspectRatio)
        self.mr_pix = pixmap
        self.qlabel_MR_crop.setPixmap(pixmap)

    def overlay(self, event):
        over_pix = self.mr_pix - self.ct_pix + 1024
        self.qlabel_overay.setPixmap(over_pix)

    def selectimageCT(self):
        dcmitem = self.List_CT.selectedItems()[0].text()
        self.dcmfilect = pydicom.dcmread(dcmitem)
        CTimage = np.copy(self.dcmfilect.pixel_array)

        ## Qlabel
        CTimage = (CTimage / 16).astype(np.uint8)
        CTimage = np.require(CTimage, np.uint8, 'C')
        h, w = CTimage.shape
        result = QtGui.QImage(CTimage.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        pixmap = pixmap.scaled(256, 256, QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT.setPixmap(pixmap)

    def selectimageMR(self):
        dcmitem = self.List_MR.selectedItems()[0].text()
        self.dcmfilemr = pydicom.dcmread(dcmitem)
        MRimage = np.copy(self.dcmfilemr.pixel_array)

        MRimage = (MRimage / 16).astype(np.uint8)
        MRimage = np.require(MRimage, np.uint8, 'C')
        h, w = MRimage.shape
        result = QtGui.QImage(MRimage.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        self.qlabel_MR.setPixmap(pixmap)

    def opendirectory(self):
        self.List_directory.clear()
        ## C:\\를 베이스로 디렉토리 열기 실행
        # self.dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Folder', 'C:\\')
        self.dir_name = "C:\\demo_after"

        ## 해당 경로에 있는 num 폴더들 List_directory에 추가
        dir_list = os.listdir(self.dir_name)
        for i in dir_list:
            dir_i = QtWidgets.QListWidgetItem(i)
            self.List_directory.addItem(dir_i)

    def choosedirectory(self):
        ## 아이템 선택 할때 먼저 초기화
        self.List_CT.clear()
        self.List_MR.clear()

        ## 선택한 아이템 텍스트 저장
        selecteditem = self.List_directory.selectedItems()[0].text()
        current_dir = self.dir_name + '\\' + selecteditem
        path_ct = current_dir + "\\CT"
        path_t2 = current_dir + "\\MRI"

        ## 각각 폴더안에서 dcm 파일 찾기
        ct_default = glob.glob(os.path.join(path_ct, "*.dcm"))
        mr_default = glob.glob(os.path.join(path_t2, "*.dcm"))

        ## List CT/MRI에 dcm 아이템 추가
        for item in ct_default:
            dcmitem = QtWidgets.QListWidgetItem(item)
            self.List_CT.addItem(dcmitem)
        for item in mr_default:
            dcmitem = QtWidgets.QListWidgetItem(item)
            self.List_MR.addItem(dcmitem)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Pixel_gui()
    ex.show()
    sys.exit(app.exec_())

###Qlabel이 아닌 Qgraphics로 하는법
# CTcrop_image = (CTcrop_image / 16).astype(np.uint8)
# CTcrop_image = np.require(CTcrop_image, np.uint8, 'C')
# h, w = CTcrop_image.shape
# result = QtGui.QImage(CTcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
# pixmap = QtGui.QPixmap(result)
# # pixmap = pixmap.scaled(self.graphics_CT.width(), self.graphics_CT.height(), QtCore.Qt.KeepAspectRatio)
# scene = QtWidgets.QGraphicsScene(self)
# scene.addPixmap(pixmap)
# self.graphics_CT.setScene(scene)

