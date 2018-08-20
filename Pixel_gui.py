import sys, os, glob
import pydicom
import numpy as np
import skimage.io as sk
from skimage import data, io, filters, color

from PyQt5 import QtCore, uic, QtWidgets, QtGui
# gui = uic.loadUiType("untitled.ui")[0]

class Pixel_gui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    
        ## 디렉토리 열고 dcm 리스트까지 추가    
        dir_name = ''
        self.Button_open.clicked.connect(self.opendirectory)
        self.List_directory.itemClicked.connect(self.choosedirectory)

        ## dcm 파일 클릭하면 View에 이미지 띄우기
        self.List_CT.itemClicked.connect(self.selectimageCT)
        self.List_MR.itemClicked.connect(self.selectimageMR)

        

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2001, 965)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        ## 디렉토리 오픈 버튼
        self.Button_open = QtWidgets.QPushButton(self.centralwidget)
        self.Button_open.setGeometry(QtCore.QRect(1870, 20, 51, 23))
        self.Button_open.setObjectName("Button_open")
        ## 디렉토리 리스트
        self.List_directory = QtWidgets.QListWidget(self.centralwidget)
        self.List_directory.setGeometry(QtCore.QRect(1870, 50, 51, 401))
        self.List_directory.setObjectName("List_directory")

        self.qlabel_CT = QtWidgets.QLabel(self.centralwidget)
        self.qlabel_CT.setGeometry(QtCore.QRect(20, 30, 500, 500))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlabel_CT.sizePolicy().hasHeightForWidth())
        self.qlabel_CT.setSizePolicy(sizePolicy)
        self.qlabel_CT.setStyleSheet("background-color:white\n"
                                     "")
        self.qlabel_CT.setFrameShape(QtWidgets.QFrame.Box)
        self.qlabel_CT.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlabel_CT.setLineWidth(1)
        self.qlabel_CT.setMidLineWidth(0)
        self.qlabel_CT.setText("")
        self.qlabel_CT.setObjectName("qlabel_CT")
        self.qlabel_CT_crop = QtWidgets.QLabel(self.centralwidget)
        self.qlabel_CT_crop.setGeometry(QtCore.QRect(630, 40, 200, 300))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlabel_CT_crop.sizePolicy().hasHeightForWidth())
        self.qlabel_CT_crop.setSizePolicy(sizePolicy)
        self.qlabel_CT_crop.setStyleSheet("background-color:white\n"
                                          "")
        self.qlabel_CT_crop.setFrameShape(QtWidgets.QFrame.Box)
        self.qlabel_CT_crop.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlabel_CT_crop.setLineWidth(1)
        self.qlabel_CT_crop.setMidLineWidth(0)
        self.qlabel_CT_crop.setText("")
        self.qlabel_CT_crop.setObjectName("qlabel_CT_crop")
        self.qlabel_MR = QtWidgets.QLabel(self.centralwidget)
        self.qlabel_MR.setGeometry(QtCore.QRect(1230, 30, 500, 500))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlabel_MR.sizePolicy().hasHeightForWidth())
        self.qlabel_MR.setSizePolicy(sizePolicy)
        self.qlabel_MR.setStyleSheet("background-color:white\n"
                                     "")
        self.qlabel_MR.setFrameShape(QtWidgets.QFrame.Box)
        self.qlabel_MR.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlabel_MR.setLineWidth(1)
        self.qlabel_MR.setMidLineWidth(0)
        self.qlabel_MR.setText("")
        self.qlabel_MR.setObjectName("qlabel_MR")
        self.qlabel_MR_crop = QtWidgets.QLabel(self.centralwidget)
        self.qlabel_MR_crop.setGeometry(QtCore.QRect(900, 40, 200, 300))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlabel_MR_crop.sizePolicy().hasHeightForWidth())
        self.qlabel_MR_crop.setSizePolicy(sizePolicy)
        self.qlabel_MR_crop.setStyleSheet("background-color:white\n"
                                          "")
        self.qlabel_MR_crop.setFrameShape(QtWidgets.QFrame.Box)
        self.qlabel_MR_crop.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlabel_MR_crop.setLineWidth(1)
        self.qlabel_MR_crop.setMidLineWidth(0)
        self.qlabel_MR_crop.setText("")
        self.qlabel_MR_crop.setObjectName("qlabel_MR_crop")
        self.qlabel_overay = QtWidgets.QLabel(self.centralwidget)
        self.qlabel_overay.setGeometry(QtCore.QRect(770, 370, 200, 300))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qlabel_overay.sizePolicy().hasHeightForWidth())
        self.qlabel_overay.setSizePolicy(sizePolicy)
        self.qlabel_overay.setStyleSheet("background-color:white\n"
                                         "")
        self.qlabel_overay.setFrameShape(QtWidgets.QFrame.Box)
        self.qlabel_overay.setFrameShadow(QtWidgets.QFrame.Plain)
        self.qlabel_overay.setLineWidth(1)
        self.qlabel_overay.setMidLineWidth(0)
        self.qlabel_overay.setText("")
        self.qlabel_overay.setObjectName("qlabel_overay")
        self.List_CT = QtWidgets.QListWidget(self.centralwidget)
        self.List_CT.setGeometry(QtCore.QRect(20, 560, 501, 191))
        self.List_CT.setObjectName("List_CT")
        self.List_MR = QtWidgets.QListWidget(self.centralwidget)
        self.List_MR.setGeometry(QtCore.QRect(1230, 560, 501, 191))
        self.List_MR.setObjectName("List_MR")
        self.Button_save = QtWidgets.QPushButton(self.centralwidget)
        self.Button_save.setGeometry(QtCore.QRect(830, 700, 101, 31))
        self.Button_save.setObjectName("Button_save")
        self.Button_CT1 = QtWidgets.QPushButton(self.centralwidget)
        self.Button_CT1.setGeometry(QtCore.QRect(690, 750, 101, 31))
        self.Button_CT1.setObjectName("Button_CT1")
        self.Button_CTMR = QtWidgets.QPushButton(self.centralwidget)
        self.Button_CTMR.setGeometry(QtCore.QRect(830, 750, 101, 31))
        self.Button_CTMR.setObjectName("Button_CTMR")
        self.Button_MR1 = QtWidgets.QPushButton(self.centralwidget)
        self.Button_MR1.setGeometry(QtCore.QRect(970, 750, 101, 31))
        self.Button_MR1.setObjectName("Button_MR1")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(650, 10, 160, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider.setGeometry(QtCore.QRect(570, 80, 22, 160))
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.horizontalSlider_2 = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_2.setGeometry(QtCore.QRect(920, 10, 160, 22))
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.verticalSlider_2 = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider_2.setGeometry(QtCore.QRect(1150, 80, 22, 160))
        self.verticalSlider_2.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_2.setObjectName("verticalSlider_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2001, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Button_open.setText(_translate("MainWindow", "Open"))
        self.Button_save.setText(_translate("MainWindow", "Save"))
        self.Button_CT1.setText(_translate("MainWindow", "CT + 1"))
        self.Button_CTMR.setText(_translate("MainWindow", "CT + MR"))
        self.Button_MR1.setText(_translate("MainWindow", "MR + 1"))

    def selectimageCT(self):
        dcmitem = self.List_CT.selectedItems()[0].text()
        dcmimage = pydicom.dcmread(dcmitem).pixel_array

        # dcmimage_tif = sk.imsave('test.tif', dcmimage)
        # dcmimage_tif = sk.imread('test.tif')
        # self.qlabel_CT.setPixmap(dcmimage_tif)

        dcmimage = (dcmimage / 16).astype(np.uint8)
        dcmimage = np.require(dcmimage, np.uint8, 'C')
        h, w = dcmimage.shape
        result = QtGui.QImage(dcmimage.data, w, h, QtGui.QImage.Format_Grayscale8)
        self.qlabel_CT.setPixmap(QtGui.QPixmap.fromImage(result))

    def selectimageMR(self):
        dcmitem = ''

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

