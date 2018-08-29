import sys, os, glob
import pydicom
import numpy as np
import skimage.io as sk
from skimage.transform import resize
from PyQt5.QtCore import Qt
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
        ## CT dicom 파일변수, 해상도 변수
        self.dcmfilect = ''
        self.ct_shape = ''
        ## MR dicom 파일 변수, CT 해상도로 변환한 픽셀변수
        self.dcmfilemr = ''
        self.resizemr = ''
        ## 실제로 저장될 변수
        self.save_ct = ''
        self.save_mr = ''
        ## Qlabel에서 찍히는 x, y좌표
        self.ct_pos_x = ''
        self.ct_pos_y = ''
        self.mr_pos_x = ''
        self.mr_pos_y = ''
        ## 파일저장 할때 쓰는 번호
        self.name_count = 1
        ## CT ROI 사이즈(표준)
        self.ROI_width = 600
        self.ROI_height = 700
        ## MRI ROI 사이즈
        self.MR_width = 600
        self.MR_height = 700


        ## 디렉토리 열고 dcm 리스트까지 추가
        self.Button_open.clicked.connect(self.opendirectory)
        self.List_directory.clicked.connect(self.choosedirectory)

        ## 이전 Ratio 불러오기
        self.beforexy.clicked.connect(self.save_ratio)

        ## CT 방향버튼
        self.CT_up.clicked.connect(self.ct_up)
        self.CT_down.clicked.connect(self.ct_down)
        self.CT_left.clicked.connect(self.ct_left)
        self.CT_right.clicked.connect(self.ct_right)

        ## MR 방향버튼
        self.MR_up.clicked.connect(self.mr_up)
        self.MR_down.clicked.connect(self.mr_down)
        self.MR_left.clicked.connect(self.mr_left)
        self.MR_right.clicked.connect(self.mr_right)

        ##save 버튼
        self.Button_save.clicked.connect(self.savetiff)

        self.pix600x700.clicked.connect(self.setPix600x700)
        self.pix800x900.clicked.connect(self.setPix800x900)

        ## dcm 파일 클릭하면 View에 이미지 띄우기
        self.List_CT.clicked.connect(self.selectimageCT)
        self.List_MR.clicked.connect(self.selectimageMR)

        self.qlabel_CT.mousePressEvent = self.ct_savepos
        self.qlabel_MR.mousePressEvent = self.mr_savepos

        self.mr_hor.valueChanged.connect(self.changeRatio)
        self.mr_ver.valueChanged.connect(self.changeRatio)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_F7:
            self.add_list_ct()
        elif e.key() == QtCore.Qt.Key_F8:
            self.add_list_ct(-1)
        elif e.key() == QtCore.Qt.Key_F9:
            self.add_list_mr()
        elif e.key() == QtCore.Qt.Key_F10:
            self.add_list_mr(-1)
        elif e.key() == QtCore.Qt.Key_F11:
            self.add_list_ctmr()
        elif e.key() == QtCore.Qt.Key_F12:
            self.add_list_dir()
        elif e.key() == Qt.Key_I:
            self.ct_up()
        elif e.key() == Qt.Key_K:
            self.ct_down()
        elif e.key() == Qt.Key_J:
            self.ct_left()
        elif e.key() == Qt.Key_L:
            self.ct_right()
        elif e.key() == Qt.Key_W:
            self.mr_up()
        elif e.key() == Qt.Key_S:
            self.mr_down()
        elif e.key() == Qt.Key_A:
            self.mr_left()
        elif e.key() == Qt.Key_D:
            self.mr_right()
        elif e.key() == Qt.Key_Return:
            self.savetiff()
        elif e.key() == Qt.Key_Backspace:
            self.save_ratio()
        elif e.key() == QtCore.Qt.Key_F1:
            self.adjust_hor(2)
        elif e.key() == QtCore.Qt.Key_F2:
            self.adjust_hor(-2)
        elif e.key() == QtCore.Qt.Key_F3:
            self.adjust_ver(2)
        elif e.key() == QtCore.Qt.Key_F4:
            self.adjust_ver(-2)

    def setPix600x700(self):
        if self.ct_shape == (1024, 1024):
            self.ROI_width = 600
            self.ROI_height = 700
            self.MR_width = 600
            self.MR_height = 700
        elif self.ct_shape == (512, 512):
            self.ROI_width = 300
            self.ROI_height = 350
            self.MR_width = 300
            self.MR_height = 350

    def setPix800x900(self):
        if self.ct_shape == (1024, 1024):
            self.ROI_width = 800
            self.ROI_height = 900
            self.MR_width = 800
            self.MR_height = 900
        elif self.ct_shape == (512, 512):
            self.ROI_width = 400
            self.ROI_height = 450
            self.MR_width = 400
            self.MR_height = 450

    def adjust_ver(self, count):
        ad = self.mr_ver.value() + count
        if count > 0:
            if ad < self.mr_ver.maximum():
                self.mr_ver.setValue(ad)
        elif count < 0:
            if ad > self.mr_ver.minimum():
                self.mr_ver.setValue(ad)

    def adjust_hor(self, count):
        ad = self.mr_hor.value() + count
        if count > 0:
            if ad < self.mr_hor.maximum():
                self.mr_hor.setValue(ad)
        elif count < 0:
            if ad > self.mr_hor.minimum():
                self.mr_hor.setValue(ad)

    def add_list_ctmr(self, count=1):
        self.add_list_ct(count)
        self.add_list_mr(count)

    def add_list_ct(self, count=1):
        row = self.List_CT.currentRow() + count
        if count == 1:
            if row < self.List_CT.count():
                self.List_CT.setCurrentRow(row)
                self.selectimageCT()
        elif count == -1:
            if row > 0:
                self.List_CT.setCurrentRow(row)
                self.selectimageCT()

    def add_list_mr(self, count=1):
        row = self.List_MR.currentRow() + count
        if count == 1:
            if row < self.List_MR.count():
                self.List_MR.setCurrentRow(row)
                self.selectimageMR()
        elif count == -1:
            if row > 0:
                self.List_MR.setCurrentRow(row)
                self.selectimageMR()

    def add_list_dir(self):
        row = self.List_directory.currentRow() + 1
        if row < self.List_directory.count():
            self.List_directory.setCurrentRow(row)
            self.choosedirectory()

    def ct_savepos(self, event):
        if self.ct_shape == (1024, 1024):
            self.ct_pos_x = int(event.pos().x()) * 2
            self.ct_pos_y = int(event.pos().y()) * 2
        elif self.ct_shape == (512, 512):
            self.ct_pos_x = int(event.pos().x())
            self.ct_pos_y = int(event.pos().y())
        self.cropCT()

    def mr_savepos(self, event):
        if self.ct_shape == (1024, 1024):
            self.mr_pos_x = int(event.pos().x()) * 2
            self.mr_pos_y = int(event.pos().y()) * 2
        elif self.ct_shape == (512, 512):
            self.mr_pos_x = int(event.pos().x())
            self.mr_pos_y = int(event.pos().y())
        self.cropMR()

    ## crop 이미지 이동
    def ct_up(self):
        self.ct_pos_y = self.ct_pos_y + 4
        self.cropCT()
        self.overlay()
    def ct_down(self):
        self.ct_pos_y = self.ct_pos_y - 4
        self.cropCT()
        self.overlay()
    def ct_left(self):
        self.ct_pos_x = self.ct_pos_x + 4
        self.cropCT()
        self.overlay()
    def ct_right(self):
        self.ct_pos_x = self.ct_pos_x - 4
        self.cropCT()
        self.overlay()

    ## crop 이미지 이동
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


    ## 이전 파일에서 지정했던 x,y / x,y로 이번 파일에서 crop
    def save_ratio(self):
        self.cropCT()
        self.cropMR()

    ## 스크롤바에 따라서 MR의 ROI 범위 조정 -> resize
    def resize_ratio(self):
        y = self.mr_pos_y
        x = self.mr_pos_x
        width = int(self.MR_width/2)
        height = int(self.MR_height)

        MRcrop_image = np.copy(self.resizemr[y:y+height, x-width:x+width])
        self.save_mr = resize(MRcrop_image, (self.ROI_height, self.ROI_width), anti_aliasing=True, order=3)
        self.save_mr = (self.save_mr * 65535).astype(np.uint16)

        pixmap = self.display_qlabel(self.resizemr, 1, x, y, ctormr=1)

    ## 저장예정인 파일을 오버레이로 나타냄, 화면 안보이면 여기서 조정하면됨
    def overlay(self):
        CTover_image = resize(self.save_ct, (450, 400), anti_aliasing=True, order=3)
        CTover_image = (CTover_image * 65535).astype(np.uint16)
        MRover_image = resize(self.save_mr, (450, 400), anti_aliasing=True, order=3)
        MRover_image = (MRover_image * 65535).astype(np.uint16)

        over_image = (CTover_image - MRover_image) * 2
        over_pixmap = self.display_qlabel(over_image)
        self.qlabel_overay.setPixmap(over_pixmap)

    ## ROI 저장
    def savetiff(self):
        ### 디렉토리명 폴더 안에 overlay 폴더를 만들기
        selecteditem = self.List_directory.selectedItems()[0].text()
        current_dir = self.dir_name + '\\' + selecteditem
        over_dir = current_dir + "\\overlay"

        ### overlay 폴더, CT, MR 없을 경우 생성
        if not os.path.isdir(over_dir):
            os.mkdir(over_dir)
        if not os.path.isdir(over_dir + "\\CT"):
            os.mkdir(over_dir + "\\CT")
        if not os.path.isdir(over_dir + "\\MR"):
            os.mkdir(over_dir + "\\MR")

        ### 각각의 경로에 순번 + tif 이름으로 저장
        ct_name = over_dir + "\\CT\\" + str(self.name_count) + ".tif"
        mr_name = over_dir + "\\MR\\" + str(self.name_count) + ".tif"
        sk.imsave(ct_name, self.save_ct, plugin='tifffile')
        sk.imsave(mr_name, self.save_mr, plugin='tifffile')
        self.name_count = self.name_count + 1

    ## 스크롤바 움직이면 실행
    def changeRatio(self):
        x = self.mr_pos_x
        y = self.mr_pos_y
        self.MR_width = self.ROI_width + self.mr_hor.value() * 4
        self.MR_height = self.ROI_height + self.mr_ver.value() * 4
        self.resize_ratio()
        self.cropMR()

    ## CT 이미지를 클릭하면 ROI crop
    def cropCT(self):
        CTcrop_x = self.ct_pos_x
        CTcrop_y = self.ct_pos_y

        ## ROI 범위 지정
        height = int(self.ROI_height)
        width = int(self.ROI_width/2)

        ### ROI를 저장변수에 저장
        CTcrop_image = np.copy(self.dcmfilect.pixel_array[CTcrop_y:CTcrop_y+height, CTcrop_x-width:CTcrop_x+width])
        self.save_ct = CTcrop_image.astype(np.uint16)

        ### ROI를 CT_crop에 출력
        pixmap = self.display_qlabel(self.save_ct)
        pixmap = pixmap.scaled(self.qlabel_CT_crop.width(), self.qlabel_CT_crop.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT_crop.setPixmap(pixmap)

        ### 원본에서 ROI에 네모박스 출력
        pixmap = self.display_qlabel(self.dcmfilect.pixel_array, 1, self.ct_pos_x, self.ct_pos_y)
        pixmap = pixmap.scaled(self.qlabel_CT.width(), self.qlabel_CT.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT.setPixmap(pixmap)

    ## MR 이미지를 클릭하면 ROI crop
    def cropMR(self):
        x = self.mr_pos_x
        y = self.mr_pos_y

        ## ROI 범위 지정
        height = int(self.ROI_height)
        width = int(self.ROI_width/2)

        ### ROI를 저장변수에 저장
        self.save_mr = np.copy(self.resizemr[y:y+height, x-width:x+width])
        ## astype으로 uint16할 필요가 있을까?

        ### 현재 비율대로 사진 조정
        self.resize_ratio()

        ### ROI를 MR_crop에 출력
        pixmap = self.display_qlabel(self.save_mr)
        pixmap = pixmap.scaled(self.qlabel_MR_crop.width(), self.qlabel_MR_crop.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR_crop.setPixmap(pixmap)

        ### 오버레이 이미지 출력
        self.overlay()

        ### 원본에서 ROI에 네모박스 출력
        pixmap = self.display_qlabel(self.resizemr, 1, self.mr_pos_x, self.mr_pos_y, ctormr=1)
        pixmap = pixmap.scaled(self.qlabel_MR.width(), self.qlabel_MR.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR.setPixmap(pixmap)
        
    ## CT파일 클릭시 화면에 출력
    def selectimageCT(self):
        ## List_CT에서 선택파일명을 가져온 다음에 pydicom으로 열기
        dcmitem = self.List_CT.selectedItems()[0].text()
        self.dcmfilect = pydicom.dcmread(dcmitem)
        self.ct_shape = self.dcmfilect.pixel_array.shape

        if self.ct_shape == (1024, 1024):
            self.ROI_height = 700
            self.ROI_width = 600
            self.MR_height = 700
            self.MR_width = 600
        elif self.ct_shape == (512, 512):
            self.ROI_height = 350
            self.ROI_width = 300
            self.MR_height = 350
            self.MR_width = 300

        ## 선택한 파일이미지를 CT에 출력
        pixmap = self.display_qlabel(self.dcmfilect.pixel_array)
        pixmap = pixmap.scaled(self.qlabel_CT.width(), self.qlabel_CT.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT.setPixmap(pixmap)

    ## MR파일 클릭시 화면에 출력
    def selectimageMR(self):
        ### List MR에서 선택파일명을 가져온 다음에 pydicom으로 열기
        dcmitem = self.List_MR.selectedItems()[0].text()
        self.dcmfilemr = pydicom.dcmread(dcmitem)

        ### MR의 사이즈 -> 1024 * 1024로 변환
        self.resizemr = np.copy(self.dcmfilemr.pixel_array)
        self.resizemr = resize(self.resizemr, (self.ct_shape[0], self.ct_shape[1]), anti_aliasing=True, order=3)
        self.resizemr = (self.resizemr * 32767).astype(np.uint16)
        ### 65535가 아니라 32767??

        ### 선택한 파일이미지를 MR에 출력
        pixmap = self.display_qlabel(self.resizemr)
        pixmap = pixmap.scaled(self.qlabel_MR.width(), self.qlabel_MR.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR.setPixmap(pixmap)

    ## 각 라벨에 출력해주는 함수
    def display_qlabel(self, base, drawRect=0, x=0, y=0, ctormr=0):
        if drawRect == 0:
            image = np.copy(base)
            image = (image / 16).astype(np.uint8)
            image = np.require(image, np.uint8, 'C')
            h, w = image.shape
            result = QtGui.QImage(image.data, w, h, QtGui.QImage.Format_Grayscale8)
            pixmap = QtGui.QPixmap(result)
        elif drawRect == 1:
            image = np.copy(base)
            image = (image / 16).astype(np.uint8)
            image = np.require(image, np.uint8, 'C')
            h, w = image.shape
            result = QtGui.QImage(image.data, w, h, QtGui.QImage.Format_Grayscale8)
            painter = QtGui.QPainter()
            painter.begin(result)
            painter.setPen(Qt.white)
            if ctormr == 0:
                width = int(self.ROI_width/2)
                height = int(self.ROI_height)
            elif ctormr == 1:
                width = int(self.MR_width/2)
                height = int(self.MR_height)
            painter.drawRect(x-width, y, width * 2, height)
            painter.end()
            pixmap = QtGui.QPixmap(result)
        return pixmap

    ## 디렉토리 오픈 함수
    def opendirectory(self):
        self.List_directory.clear()
        ## C:\\를 베이스로 디렉토리 열기 실행
        self.dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Folder', 'C:\\')
        # self.dir_name = "C:\\demo_after"

        ## 해당 경로에 있는 num 폴더들 List_directory에 추가
        dir_list = os.listdir(self.dir_name)
        for i in dir_list:
            dir_i = QtWidgets.QListWidgetItem(i)
            self.List_directory.addItem(dir_i)

    ## 디렉토리 선택하면 해당 폴더에서 dicom 파일 불러오기
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

#     def setupUi(self, MainWindow):
#         MainWindow.setObjectName("MainWindow")
#         MainWindow.resize(1920, 1080)
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
#         MainWindow.setSizePolicy(sizePolicy)
#         self.centralwidget = QtWidgets.QWidget(MainWindow)
#         self.centralwidget.setObjectName("centralwidget")
#         self.Button_open = QtWidgets.QPushButton(self.centralwidget)
#         self.Button_open.setGeometry(QtCore.QRect(1260, 40, 81, 51))
#         self.Button_open.setObjectName("Button_open")
#         self.List_directory = QtWidgets.QListWidget(self.centralwidget)
#         self.List_directory.setGeometry(QtCore.QRect(950, 520, 61, 451))
#         self.List_directory.setObjectName("List_directory")
#         self.qlabel_MR = QtWidgets.QLabel(self.centralwidget)
#         self.qlabel_MR.setGeometry(QtCore.QRect(10, 510, 512, 512))
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.qlabel_MR.sizePolicy().hasHeightForWidth())
#         self.qlabel_MR.setSizePolicy(sizePolicy)
#         self.qlabel_MR.setStyleSheet("background-color:white\n"
# "")
#         self.qlabel_MR.setFrameShape(QtWidgets.QFrame.Box)
#         self.qlabel_MR.setFrameShadow(QtWidgets.QFrame.Plain)
#         self.qlabel_MR.setLineWidth(1)
#         self.qlabel_MR.setMidLineWidth(0)
#         self.qlabel_MR.setText("")
#         self.qlabel_MR.setObjectName("qlabel_MR")
#         self.qlabel_MR_crop = QtWidgets.QLabel(self.centralwidget)
#         self.qlabel_MR_crop.setGeometry(QtCore.QRect(900, 40, 300, 350))
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.qlabel_MR_crop.sizePolicy().hasHeightForWidth())
#         self.qlabel_MR_crop.setSizePolicy(sizePolicy)
#         self.qlabel_MR_crop.setStyleSheet("background-color:white\n"
# "")
#         self.qlabel_MR_crop.setFrameShape(QtWidgets.QFrame.Box)
#         self.qlabel_MR_crop.setFrameShadow(QtWidgets.QFrame.Plain)
#         self.qlabel_MR_crop.setLineWidth(1)
#         self.qlabel_MR_crop.setMidLineWidth(0)
#         self.qlabel_MR_crop.setText("")
#         self.qlabel_MR_crop.setObjectName("qlabel_MR_crop")
#         self.qlabel_overay = QtWidgets.QLabel(self.centralwidget)
#         self.qlabel_overay.setGeometry(QtCore.QRect(530, 520, 400, 450))
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.qlabel_overay.sizePolicy().hasHeightForWidth())
#         self.qlabel_overay.setSizePolicy(sizePolicy)
#         self.qlabel_overay.setStyleSheet("background-color:white\n"
# "")
#         self.qlabel_overay.setFrameShape(QtWidgets.QFrame.Box)
#         self.qlabel_overay.setFrameShadow(QtWidgets.QFrame.Plain)
#         self.qlabel_overay.setLineWidth(1)
#         self.qlabel_overay.setMidLineWidth(0)
#         self.qlabel_overay.setText("")
#         self.qlabel_overay.setObjectName("qlabel_overay")
#         self.mr_hor = QtWidgets.QSlider(self.centralwidget)
#         self.mr_hor.setGeometry(QtCore.QRect(910, 10, 251, 22))
#         self.mr_hor.setMinimum(-50)
#         self.mr_hor.setMaximum(100)
#         self.mr_hor.setProperty("value", 0)
#         self.mr_hor.setSliderPosition(0)
#         self.mr_hor.setOrientation(QtCore.Qt.Horizontal)
#         self.mr_hor.setObjectName("mr_hor")
#         self.mr_ver = QtWidgets.QSlider(self.centralwidget)
#         self.mr_ver.setGeometry(QtCore.QRect(1220, 80, 22, 251))
#         self.mr_ver.setMinimum(-50)
#         self.mr_ver.setMaximum(100)
#         self.mr_ver.setProperty("value", 0)
#         self.mr_ver.setOrientation(QtCore.Qt.Vertical)
#         self.mr_ver.setObjectName("mr_ver")
#         self.qlabel_CT = QtWidgets.QLabel(self.centralwidget)
#         self.qlabel_CT.setGeometry(QtCore.QRect(10, 0, 512, 512))
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.qlabel_CT.sizePolicy().hasHeightForWidth())
#         self.qlabel_CT.setSizePolicy(sizePolicy)
#         self.qlabel_CT.setStyleSheet("background-color:white\n"
# "")
#         self.qlabel_CT.setFrameShape(QtWidgets.QFrame.Box)
#         self.qlabel_CT.setFrameShadow(QtWidgets.QFrame.Plain)
#         self.qlabel_CT.setLineWidth(1)
#         self.qlabel_CT.setMidLineWidth(0)
#         self.qlabel_CT.setText("")
#         self.qlabel_CT.setObjectName("qlabel_CT")
#         self.qlabel_CT_crop = QtWidgets.QLabel(self.centralwidget)
#         self.qlabel_CT_crop.setGeometry(QtCore.QRect(550, 40, 300, 350))
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.qlabel_CT_crop.sizePolicy().hasHeightForWidth())
#         self.qlabel_CT_crop.setSizePolicy(sizePolicy)
#         self.qlabel_CT_crop.setStyleSheet("background-color:white\n"
# "")
#         self.qlabel_CT_crop.setFrameShape(QtWidgets.QFrame.Box)
#         self.qlabel_CT_crop.setFrameShadow(QtWidgets.QFrame.Plain)
#         self.qlabel_CT_crop.setLineWidth(1)
#         self.qlabel_CT_crop.setMidLineWidth(0)
#         self.qlabel_CT_crop.setText("")
#         self.qlabel_CT_crop.setObjectName("qlabel_CT_crop")
#         self.List_MR = QtWidgets.QListWidget(self.centralwidget)
#         self.List_MR.setGeometry(QtCore.QRect(1030, 760, 321, 211))
#         self.List_MR.setObjectName("List_MR")
#         self.Button_MR1 = QtWidgets.QPushButton(self.centralwidget)
#         self.Button_MR1.setGeometry(QtCore.QRect(1190, 470, 101, 31))
#         self.Button_MR1.setObjectName("Button_MR1")
#         self.Button_save = QtWidgets.QPushButton(self.centralwidget)
#         self.Button_save.setGeometry(QtCore.QRect(1060, 430, 101, 31))
#         self.Button_save.setObjectName("Button_save")
#         self.List_CT = QtWidgets.QListWidget(self.centralwidget)
#         self.List_CT.setGeometry(QtCore.QRect(1030, 520, 321, 211))
#         self.List_CT.setObjectName("List_CT")
#         self.Button_CT1 = QtWidgets.QPushButton(self.centralwidget)
#         self.Button_CT1.setGeometry(QtCore.QRect(1060, 470, 101, 31))
#         self.Button_CT1.setObjectName("Button_CT1")
#         self.Button_CTMR = QtWidgets.QPushButton(self.centralwidget)
#         self.Button_CTMR.setGeometry(QtCore.QRect(1190, 430, 101, 31))
#         self.Button_CTMR.setObjectName("Button_CTMR")
#         self.CT_up = QtWidgets.QPushButton(self.centralwidget)
#         self.CT_up.setGeometry(QtCore.QRect(740, 400, 25, 25))
#         self.CT_up.setObjectName("CT_up")
#         self.CT_left = QtWidgets.QPushButton(self.centralwidget)
#         self.CT_left.setGeometry(QtCore.QRect(710, 430, 25, 25))
#         self.CT_left.setObjectName("CT_left")
#         self.CT_right = QtWidgets.QPushButton(self.centralwidget)
#         self.CT_right.setGeometry(QtCore.QRect(770, 430, 25, 25))
#         self.CT_right.setObjectName("CT_right")
#         self.CT_down = QtWidgets.QPushButton(self.centralwidget)
#         self.CT_down.setGeometry(QtCore.QRect(740, 460, 25, 25))
#         self.CT_down.setObjectName("CT_down")
#         self.MR_right = QtWidgets.QPushButton(self.centralwidget)
#         self.MR_right.setGeometry(QtCore.QRect(1000, 430, 25, 25))
#         self.MR_right.setObjectName("MR_right")
#         self.MR_left = QtWidgets.QPushButton(self.centralwidget)
#         self.MR_left.setGeometry(QtCore.QRect(940, 430, 25, 25))
#         self.MR_left.setObjectName("MR_left")
#         self.MR_down = QtWidgets.QPushButton(self.centralwidget)
#         self.MR_down.setGeometry(QtCore.QRect(970, 460, 25, 25))
#         self.MR_down.setObjectName("MR_down")
#         self.MR_up = QtWidgets.QPushButton(self.centralwidget)
#         self.MR_up.setGeometry(QtCore.QRect(970, 400, 25, 25))
#         self.MR_up.setObjectName("MR_up")
#         self.beforexy = QtWidgets.QPushButton(self.centralwidget)
#         self.beforexy.setGeometry(QtCore.QRect(1150, 400, 41, 23))
#         self.beforexy.setObjectName("beforexy")
#         self.pix600x700 = QtWidgets.QPushButton(self.centralwidget)
#         self.pix600x700.setGeometry(QtCore.QRect(1270, 130, 71, 31))
#         self.pix600x700.setObjectName("pix600x700")
#         self.pix800x900 = QtWidgets.QPushButton(self.centralwidget)
#         self.pix800x900.setGeometry(QtCore.QRect(1270, 210, 71, 31))
#         self.pix800x900.setObjectName("pix800x900")
#         self.qlabel_MR.raise_()
#         self.qlabel_CT.raise_()
#         self.Button_open.raise_()
#         self.qlabel_MR_crop.raise_()
#         self.mr_hor.raise_()
#         self.mr_ver.raise_()
#         self.qlabel_CT_crop.raise_()
#         self.qlabel_overay.raise_()
#         self.List_directory.raise_()
#         self.List_MR.raise_()
#         self.Button_MR1.raise_()
#         self.Button_save.raise_()
#         self.List_CT.raise_()
#         self.Button_CT1.raise_()
#         self.Button_CTMR.raise_()
#         self.CT_up.raise_()
#         self.CT_left.raise_()
#         self.CT_right.raise_()
#         self.CT_down.raise_()
#         self.MR_right.raise_()
#         self.MR_left.raise_()
#         self.MR_down.raise_()
#         self.MR_up.raise_()
#         self.beforexy.raise_()
#         self.pix600x700.raise_()
#         self.pix800x900.raise_()
#         MainWindow.setCentralWidget(self.centralwidget)
#         self.menubar = QtWidgets.QMenuBar(MainWindow)
#         self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 21))
#         self.menubar.setObjectName("menubar")
#         MainWindow.setMenuBar(self.menubar)
#         self.statusbar = QtWidgets.QStatusBar(MainWindow)
#         self.statusbar.setObjectName("statusbar")
#         MainWindow.setStatusBar(self.statusbar)
#
#         self.retranslateUi(MainWindow)
#         QtCore.QMetaObject.connectSlotsByName(MainWindow)
#
#     def retranslateUi(self, MainWindow):
#         _translate = QtCore.QCoreApplication.translate
#         MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
#         self.Button_open.setText(_translate("MainWindow", "Open"))
#         self.Button_MR1.setText(_translate("MainWindow", "MR + 1"))
#         self.Button_save.setText(_translate("MainWindow", "Save"))
#         self.Button_CT1.setText(_translate("MainWindow", "CT + 1"))
#         self.Button_CTMR.setText(_translate("MainWindow", "CT + MR"))
#         self.CT_up.setText(_translate("MainWindow", "↑"))
#         self.CT_left.setText(_translate("MainWindow", "←"))
#         self.CT_right.setText(_translate("MainWindow", "→"))
#         self.CT_down.setText(_translate("MainWindow", "↓"))
#         self.MR_right.setText(_translate("MainWindow", "→"))
#         self.MR_left.setText(_translate("MainWindow", "←"))
#         self.MR_down.setText(_translate("MainWindow", "↓"))
#         self.MR_up.setText(_translate("MainWindow", "↑"))
#         self.beforexy.setText(_translate("MainWindow", "X, Y"))
#         self.pix600x700.setText(_translate("MainWindow", "600 * 700"))
#         self.pix800x900.setText(_translate("MainWindow", "800 * 900"))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Pixel_gui()
    ex.show()
    sys.exit(app.exec_())

