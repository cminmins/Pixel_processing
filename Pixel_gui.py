import sys, os, glob
import pydicom
import numpy as np
import skimage.io as sk
from skimage.transform import resize
from PyQt5 import QtCore, uic, QtWidgets, QtGui
gui = uic.loadUiType("untitled.ui")[0]

output_folder = ""

def apply_window_setting(mat, win_c, win_w):
    ymin = (win_c - 0.5 * win_w)
    ymax = (win_c + 0.5 * win_w)
    mat[mat <= ymin] = 0
    mat[mat > ymax] = 255
    mat[(mat > ymin) & (mat <= ymax)] = ((mat[(mat > ymin) & (mat <= ymax)] - ymin) / win_w) * 255
    return mat

class Pixel_gui(QtWidgets.QMainWindow, gui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dcmfilect = ''
        self.dcmfilemr = ''
        self.resizemr = ''
        self.save_ct = ''
        self.save_mr = ''
        self.ct_pos_x = ''
        self.ct_pos_y = ''
        self.mr_pos_x = ''
        self.mr_pos_y = ''
        self.name_count = 1
        self.change_width = 600
        self.change_height = 700

        ## 디렉토리 열고 dcm 리스트까지 추가    
        dir_name = ''
        self.Button_open.clicked.connect(self.opendirectory)
        self.List_directory.itemClicked.connect(self.choosedirectory)

        #이전 Ratio 불러오기
        self.beforexy.clicked.connect(self.save_ratio)

        #CT 방향버튼
        self.CT_up.clicked.connect(self.ct_up)
        self.CT_down.clicked.connect(self.ct_down)
        self.CT_left.clicked.connect(self.ct_left)
        self.CT_right.clicked.connect(self.ct_right)

        #MR 방향버튼
        self.MR_up.clicked.connect(self.mr_up)
        self.MR_down.clicked.connect(self.mr_down)
        self.MR_left.clicked.connect(self.mr_left)
        self.MR_right.clicked.connect(self.mr_right)


        ##save 버튼
        self.Button_save.clicked.connect(self.savetiff)

        ## dcm 파일 클릭하면 View에 이미지 띄우기
        self.List_CT.itemClicked.connect(self.selectimageCT)
        self.List_MR.itemClicked.connect(self.selectimageMR)

        self.qlabel_CT.mousePressEvent = self.ct_savepos
        self.qlabel_MR.mousePressEvent = self.mr_savepos
        # self.qlabel_overay.mouseGrabber = self.overlay

        self.mr_hor.valueChanged.connect(self.changeRatio)
        self.mr_ver.valueChanged.connect(self.changeRatio)

    def ct_savepos(self, event):
        self.ct_pos_x = int(event.pos().x()) * 4
        self.ct_pos_y = int(event.pos().y()) * 4
        self.cropCT()

    def mr_savepos(self, event):
        self.mr_pos_x = int(event.pos().x()) * 4
        self.mr_pos_y = int(event.pos().y()) * 4
        self.cropMR()

    def ct_up(self):
        self.ct_pos_y = self.ct_pos_y - 1
        self.cropCT()
        self.overlay()
    def ct_down(self):
        self.ct_pos_y = self.ct_pos_y + 1
        self.cropCT()
        self.overlay()
    def ct_left(self):
        self.ct_pos_x = self.ct_pos_x - 1
        self.cropCT()
        self.overlay()
    def ct_right(self):
        self.ct_pos_x = self.ct_pos_x + 1
        self.cropCT()
        self.overlay()

    def mr_up(self):
        self.mr_pos_y = self.mr_pos_y + 4
        self.cropMR()
    def mr_down(self):
        self.mr_pos_y = self.mr_pos_y - 4
        self.cropMR()
    def mr_left(self):
        self.mr_pos_x = self.mr_pos_x + 4
        self.cropMR()
    def mr_right(self):
        self.mr_pos_x = self.mr_pos_x - 4
        self.cropMR()

    def save_ratio(self):
        self.cropCT()
        self.cropMR()

    def resize_ratio(self):
        y = self.mr_pos_y
        x = self.mr_pos_x
        width = self.change_width
        height = self.change_height

        MRcrop_image = np.copy(self.resizemr[y:y + height, x:x + width])
        self.save_mr = resize(MRcrop_image, (700, 600), anti_aliasing=True, order=3)
        self.save_mr = (self.save_mr * 65535).astype(np.uint16)

    def overlay(self):
        CTover_image = resize(self.save_ct, (450, 400), anti_aliasing=True, order=3)
        CTover_image = (CTover_image * 65535).astype(np.uint16)
        MRover_image = resize(self.save_mr, (450, 400), anti_aliasing=True, order=3)
        MRover_image = (MRover_image * 65535).astype(np.uint16)

        over_image = CTover_image - MRover_image + 1024
        over_image = (over_image / 16).astype(np.uint8)
        over_image = np.require(over_image, np.uint8, 'C')
        h, w = over_image.shape
        over_result = QtGui.QImage(over_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        over_pixmap = QtGui.QPixmap(over_result)
        self.qlabel_overay.setPixmap(over_pixmap)

    def savetiff(self):
        selecteditem = self.List_directory.selectedItems()[0].text()
        current_dir = self.dir_name + '\\' + selecteditem
        over_dir = current_dir + "\\overlay"

        if not os.path.isdir(over_dir):
            os.mkdir(over_dir)
        if not os.path.isdir(over_dir + "\\CT"):
            os.mkdir(over_dir + "\\CT")
        if not os.path.isdir(over_dir + "\\MR"):
            os.mkdir(over_dir + "\\MR")

        ct_name = over_dir + "\\CT\\" + str(self.name_count) + ".tif"
        mr_name = over_dir + "\\MR\\" + str(self.name_count) + ".tif"
        sk.imsave(ct_name, self.save_ct, plugin='tifffile')
        sk.imsave(mr_name, self.save_mr, plugin='tifffile')
        self.name_count = self.name_count + 1

    def show_mr(self):
        MRcrop_image = self.save_mr
        MRcrop_image = (MRcrop_image / 16).astype(np.uint8)
        MRcrop_image = np.require(MRcrop_image, np.uint8, 'C')
        h, w = MRcrop_image.shape
        result = QtGui.QImage(MRcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        pixmap = pixmap.scaled(self.qlabel_CT_crop.height(), self.qlabel_CT_crop.width(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR_crop.setPixmap(pixmap)

    def changeRatio(self):
        x = self.mr_pos_x
        y = self.mr_pos_y
        self.change_width = 600 + self.mr_hor.value() * 2
        self.change_height = 700 + self.mr_ver.value() * 2
        self.resize_ratio()
        self.cropMR()

    def cropCT(self):
        ## 마우스 클릭한 곳의 좌표 256 -> 1024
        # self.ct_pos_x = int(event.pos().x()) * 4
        # self.ct_pos_y = int(event.pos().y()) * 4
        CTcrop_x = self.ct_pos_x
        CTcrop_y = self.ct_pos_y

        ## 원본 이미지 배열을 복사하고 저장할 변수에도 예비 저장
        CTcrop_image = np.copy(self.dcmfilect.pixel_array[CTcrop_y:CTcrop_y+700, CTcrop_x:CTcrop_x+600])
        self.save_ct = CTcrop_image.astype(np.uint16)

        ## 이미지를 화면에 띄우기 위해서 8비트로 낮춤
        CTcrop_image = (CTcrop_image / 16).astype(np.uint8)
        CTcrop_image = np.require(CTcrop_image, np.uint8, 'C')

        # CTcrop_image = apply_window_setting(CTcrop_image, 30, 200)

        h, w = CTcrop_image.shape
        result = QtGui.QImage(CTcrop_image.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        pixmap = pixmap.scaled(self.qlabel_CT_crop.height(), self.qlabel_CT_crop.width(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT_crop.setPixmap(pixmap)

    def cropMR(self):
        ## 마우스 클릭한 곳의 좌표 256 -> 256
        # self.mr_pos_x = int(event.pos().x()) * 4
        # self.mr_pos_y = int(event.pos().y()) * 4
        x = self.mr_pos_x
        y = self.mr_pos_y

        ## 리사이즈 1024 파일에서 불러와서 800 * 700으로 저장
        MRcrop_image = np.copy(self.resizemr)
        self.save_mr = np.copy(MRcrop_image[y:y+700, x:x+600])
        self.resize_ratio()
        self.show_mr()
        self.overlay()

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
        pixmap = pixmap.scaled(self.qlabel_CT.height(), self.qlabel_CT.width(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT.setPixmap(pixmap)

    def selectimageMR(self):
        dcmitem = self.List_MR.selectedItems()[0].text()
        self.dcmfilemr = pydicom.dcmread(dcmitem)

        self.resizemr = np.copy(self.dcmfilemr.pixel_array)
        self.resizemr = resize(self.resizemr, (1024, 1024), anti_aliasing=True, order=3)
        self.resizemr = (self.resizemr * 32767).astype(np.uint16)

        MRimage = np.copy(self.resizemr)
        MRimage = (MRimage / 16).astype(np.uint8)
        MRimage = np.require(MRimage, np.uint8, 'C')
        h, w = MRimage.shape
        result = QtGui.QImage(MRimage.data, w, h, QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap(result)
        pixmap = pixmap.scaled(self.qlabel_MR.height(), self.qlabel_MR.width(), QtCore.Qt.KeepAspectRatioByExpanding)
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

