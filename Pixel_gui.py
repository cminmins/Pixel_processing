import sys, os, glob
import pydicom
import numpy as np
import skimage.io as sk
from skimage.transform import resize

from skimage import data, io, filters, color

from PyQt5 import QtCore, uic, QtWidgets, QtGui
gui = uic.loadUiType("untitled.ui")[0]

class Pixel_gui(QtWidgets.QMainWindow, gui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dcmfilect = ''
        self.dcmfilemr = ''
        self.resizemr = ''
        self.save_ct = ''
        self.save_mr = ''
        self.mr_pos_x = ''
        self.mr_pos_y = ''
        self.name_count = 1

        ## 디렉토리 열고 dcm 리스트까지 추가    
        dir_name = ''
        self.Button_open.clicked.connect(self.opendirectory)
        self.List_directory.itemClicked.connect(self.choosedirectory)

        ##save 버튼
        self.Button_save.clicked.connect(self.savetiff)

        ## dcm 파일 클릭하면 View에 이미지 띄우기
        self.List_CT.itemClicked.connect(self.selectimageCT)
        self.List_MR.itemClicked.connect(self.selectimageMR)

        self.qlabel_CT.mousePressEvent = self.cropCT
        self.qlabel_MR.mousePressEvent = self.cropMR
        self.qlabel_overay.mousePressEvent = self.overlay

        self.mr_hor.valueChanged.connect(self.changeRatio)
        self.mr_ver.valueChanged.connect(self.changeRatio)

    def overlay(self, event):
        CTover_image = (self.save_ct / 16).astype(np.uint8)
        CTover_image = np.require(CTover_image, np.uint8, 'C')
        h, w = CTover_image.shape
        ct_result = QtGui.QImage(CTover_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        ct_pixmap = QtGui.QPixmap(ct_result)

        MRover_image = (self.save_mr / 16).astype(np.uint8)
        MRover_image = np.require(MRover_image, np.uint8, 'C')
        h, w = MRover_image.shape
        mr_result = QtGui.QImage(MRover_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        mr_pixmap = QtGui.QPixmap(mr_result)


        painter = QtGui.QPainter()
        painter.begin(ct_result)
        painter.drawImage(0, 0, mr_result)
        painter.end()

        self.qlabel_overay.setPixmap(QtGui.QPixmap.fromImage(ct_result))



    def savetiff(self):
        ct_name = str(self.name_count) + "_ct.tif"
        mr_name = str(self.name_count) + "_mr.tif"
        sk.imsave(ct_name, self.save_ct, plugin='tifffile')
        sk.imsave(mr_name, self.save_mr, plugin='tifffile')
        self.name_count = self.name_count + 1

    def changeRatio(self):
        x = self.mr_pos_x
        y = self.mr_pos_y
        change_width = 700 + self.mr_hor.value()
        change_height = 800 + self.mr_ver.value()

        MRcrop_image = np.copy(self.resizemr[y:y+change_height, x:x+change_width])
        self.save_mr = resize(MRcrop_image, (800, 700), anti_aliasing=True, order=3)
        self.save_mr = (self.save_mr * 65535).astype(np.uint16)
        MRcrop_image = self.save_mr

        ## 이미지를 화면에 띄위기 위해서 8비트로 낮춤
        MRcrop_image = (MRcrop_image / 16).astype(np.uint8)
        MRcrop_image = np.require(MRcrop_image, np.uint8, 'C')
        h, w = MRcrop_image.shape
        result = QtGui.QImage(MRcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        self.qlabel_MR_crop.setPixmap(pixmap)

    def cropCT(self, event):
        ## 마우스 클릭한 곳의 좌표 256 -> 1024
        x = event.pos().x()
        y = event.pos().y()
        CTcrop_x = int(x * 4)
        CTcrop_y = int(y * 4)

        ## 원본 이미지 배열을 복사하고 저장할 변수에도 예비 저장
        CTcrop_image = np.copy(self.dcmfilect.pixel_array[CTcrop_y:CTcrop_y+800, CTcrop_x:CTcrop_x+700])
        self.save_ct = CTcrop_image.astype(np.uint16)
        print((CTcrop_image == self.save_ct).all())

        ## 이미지를 화면에 띄우기 위해서 8비트로 낮춤
        CTcrop_image = (CTcrop_image / 16).astype(np.uint8)
        CTcrop_image = np.require(CTcrop_image, np.uint8, 'C')
        h, w = CTcrop_image.shape
        result = QtGui.QImage(CTcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        self.qlabel_CT_crop.setPixmap(pixmap)

    def cropMR(self, event):
        ## 마우스 클릭한 곳의 좌표 256 -> 256
        self.mr_pos_x = event.pos().x() * 4
        self.mr_pos_y = event.pos().y() * 4
        x = self.mr_pos_x
        y = self.mr_pos_y

        ## 원본 256 -> 1024로 변환 후 Crop해서 저장변수에 저장
        MRcrop_image = np.copy(self.resizemr)
        self.save_mr = np.copy(MRcrop_image[y:y+800, x:x+700])

        # self.save_mr = resize(MRcrop_image, (800, 700), anti_aliasing=True, order=3)
        # self.save_mr = (self.save_mr * 32767).astype(np.uint16)
        # self.save_mr = self.save_mr.astype(np.uint16)
        MRcrop_image = self.save_mr

        ## 이미지를 화면에 띄위기 위해서 8비트로 낮춤
        MRcrop_image = (MRcrop_image / 16).astype(np.uint8)
        MRcrop_image = np.require(MRcrop_image, np.uint8, 'C')
        h, w = MRcrop_image.shape
        result = QtGui.QImage(MRcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        # pixmap = pixmap.scaled(self.qlabel_MR_crop.width(), self.qlabel_MR_crop.height(), QtCore.Qt.KeepAspectRatio)
        self.qlabel_MR_crop.setPixmap(pixmap)

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

        self.resizemr = np.copy(self.dcmfilemr.pixel_array)
        self.resizemr = resize(self.resizemr, (1024, 1024), anti_aliasing=True, order=3)
        self.resizemr = (self.resizemr * 32767).astype(np.uint16)

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
        self.name_count = 1

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



# medcon -f *.nii -split3d -c dicom -b16
# medcon -f *.dcm -stack3d -c nifty -b16

