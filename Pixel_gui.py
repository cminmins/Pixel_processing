import sys, os, glob
import pydicom
import numpy as np
import skimage.io as sk
from skimage.transform import resize
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, uic, QtWidgets, QtGui
gui = uic.loadUiType("pixel_gui.ui")[0]

## windowing 조절 함수인데 성능이 별로인듯?
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
        self.ROI_width = 700
        self.ROI_height = 800
        ## MRI ROI 사이즈
        self.MR_width = 700
        self.MR_height = 800

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

        ## save 버튼
        self.Button_save.clicked.connect(self.savetiff)

        ## ROI 해상도 버튼
        self.pix600x700.clicked.connect(self.setPix600x700)
        self.pix700x800.clicked.connect(self.setPix700x800)
        self.pix800x900.clicked.connect(self.setPix800x900)

        ## dcm 파일 클릭하면 View에 이미지 띄우기
        self.List_CT.clicked.connect(self.selectimageCT)
        self.List_MR.clicked.connect(self.selectimageMR)

        ## CT/MR 이미지 클릭하면 crop 실행
        self.qlabel_CT.mousePressEvent = self.ct_savepos
        self.qlabel_MR.mousePressEvent = self.mr_savepos

        ## MR 비율 조정
        self.mr_hor.valueChanged.connect(self.changeRatio)
        self.mr_ver.valueChanged.connect(self.changeRatio)

        ## 리스트 관리
        self.Button_CTMR.clicked.connect(self.add_list_ctmr)
        self.Button_CT1.clicked.connect(self.add_list_ct)
        self.Button_MR1.clicked.connect(self.add_list_mr)

    ############## 키보드 세팅##############
    ## 키셋팅 설정
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
            self.ct_down()
        elif e.key() == Qt.Key_K:
            self.ct_up()
        elif e.key() == Qt.Key_J:
            self.ct_right()
        elif e.key() == Qt.Key_L:
            self.ct_left()
        elif e.key() == Qt.Key_W:
            self.mr_down()
        elif e.key() == Qt.Key_S:
            self.mr_up()
        elif e.key() == Qt.Key_A:
            self.mr_right()
        elif e.key() == Qt.Key_D:
            self.mr_left()
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

    ## 스크롤바 조정
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

    ## 리스트 목록
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



############## 내부 구현 함수 ################
    ## ROI 해상도 설정
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
    def setPix700x800(self):
        if self.ct_shape == (1024, 1024):
            self.ROI_width = 700
            self.ROI_height = 800
            self.MR_width = 700
            self.MR_height = 800
        elif self.ct_shape == (512, 512):
            self.ROI_width = 360
            self.ROI_height = 400
            self.MR_width = 360
            self.MR_height = 400
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

        ## Qlabel에서 찍히는 x, y좌표
        self.ct_pos_x = -1
        self.ct_pos_y = -1
        self.mr_pos_x = -1
        self.mr_pos_y = -1

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

        ## 위에 실행하면 dcmfilect -> ct_shape에 해상도가 저장됨
        self.List_CT.setCurrentRow(0)
        self.selectimageCT()
        self.List_MR.setCurrentRow(0)
        self.selectimageMR()

        ## Default ROI 사이즈를 정하기
        if self.ct_shape == (1024, 1024):
            self.ROI_width = 700
            self.ROI_height = 800
            self.MR_width = 700
            self.MR_height = 800
        elif self.ct_shape == (512, 512):
            self.ROI_width = 360
            self.ROI_height = 400
            self.MR_width = 360
            self.MR_height = 400


    ## CT파일 클릭시 화면에 출력
    def selectimageCT(self):
        self.save_ct = ''

        ## List_CT에서 선택파일명을 가져온 다음에 pydicom으로 열기
        dcmitem = self.List_CT.selectedItems()[0].text()
        self.dcmfilect = pydicom.dcmread(dcmitem)
        self.ct_shape = self.dcmfilect.pixel_array.shape

        ## 선택한 파일이미지를 CT에 출력
        pixmap = self.display_qlabel(self.dcmfilect.pixel_array)
        pixmap = pixmap.scaled(self.qlabel_CT.width(), self.qlabel_CT.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT.setPixmap(pixmap)
    ## MR파일 클릭시 화면에 출력
    def selectimageMR(self):
        self.save_mr = ''
        ### List MR에서 선택파일명을 가져온 다음에 pydicom으로 열기
        dcmitem = self.List_MR.selectedItems()[0].text()
        self.dcmfilemr = pydicom.dcmread(dcmitem)

        ### MR의 사이즈 -> 1024 * 1024로 변환
        self.resizemr = np.copy(self.dcmfilemr.pixel_array)
        self.resizemr = resize(self.resizemr, (self.ct_shape[0], self.ct_shape[1]), anti_aliasing=True, order=1)
        self.resizemr = (self.resizemr * 32767).astype(np.uint16)
        ### 65535가 아니라 32767??

        ### 선택한 파일이미지를 MR에 출력
        pixmap = self.display_qlabel(self.resizemr)
        pixmap = pixmap.scaled(self.qlabel_MR.width(), self.qlabel_MR.height(), Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR.setPixmap(pixmap)


    ## CT 이미지 클릭하면 좌표 저장
    def ct_savepos(self, event):
        if self.ct_shape == (1024, 1024):
            self.ct_pos_x = int(event.pos().x()) * 2
            self.ct_pos_y = int(event.pos().y()) * 2
        elif self.ct_shape == (512, 512):
            self.ct_pos_x = int(event.pos().x())
            self.ct_pos_y = int(event.pos().y())
        self.cropCT()
    ## MR 이미지 클릭하면 좌표 저장
    def mr_savepos(self, event):
        if self.ct_shape == (1024, 1024):
            self.mr_pos_x = int(event.pos().x()) * 2
            self.mr_pos_y = int(event.pos().y()) * 2
        elif self.ct_shape == (512, 512):
            self.mr_pos_x = int(event.pos().x())
            self.mr_pos_y = int(event.pos().y())
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


    ## 이전 파일에서 지정했던 x,y / x,y로 이번 파일에서 crop
    def save_ratio(self):
        self.cropCT()
        self.cropMR()
    ## 스크롤바 움직이면 실행
    def changeRatio(self):
        x = self.mr_pos_x
        y = self.mr_pos_y
        self.MR_width = self.ROI_width + self.mr_hor.value() * 4
        self.MR_height = self.ROI_height + self.mr_ver.value() * 4
        self.resize_ratio()
        self.cropMR()
    ## 스크롤바에 따라서 MR의 ROI 범위 조정 -> resize
    def resize_ratio(self):
        y = self.mr_pos_y
        x = self.mr_pos_x
        width = int(self.MR_width/2)
        height = int(self.MR_height)

        MRcrop_image = np.copy(self.resizemr[y:y+height, x-width:x+width])
        self.save_mr = resize(MRcrop_image, (self.ROI_height, self.ROI_width), anti_aliasing=True, order=1)
        self.save_mr = (self.save_mr * 65535).astype(np.uint16)

        pixmap = self.display_qlabel(self.resizemr, 1, x, y, ctormr=1)


    ## 저장예정인 파일을 오버레이로 나타냄, 화면 안보이면 여기서 조정하면됨
    def overlay(self):
        CTover_image = resize(self.save_ct, (450, 400), anti_aliasing=True, order=1)
        CTover_image = (CTover_image * 65535).astype(np.uint16)
        MRover_image = resize(self.save_mr, (450, 400), anti_aliasing=True, order=1)
        MRover_image = (MRover_image * 65535).astype(np.uint16)

        over_image = (CTover_image - MRover_image) * 2
        over_pixmap = self.display_qlabel(over_image)
        self.qlabel_overay.setPixmap(over_pixmap)
    ## ROI 저장
    def savetiff(self):
        try:
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

            mb = QtWidgets.QMessageBox()
            mb.setIcon(QtWidgets.QMessageBox.Information)
            mb.setWindowTitle('OK')
            mb.setText('save tiff image success')
            mb.setStandardButtons(QtWidgets.QMessageBox.Ok)
            mb.exec()
            mb.show()

            # #### 테스트
            # test = sk.imread(ct_name)
            # print("저장 전 파일과 저장 후 파일의 픽셀 비교 : ", (test == self.save_ct).all())
            # test2 = sk.imread(mr_name)
            # print("저장 전 파일과 저장 후 파일의 픽셀 비교 : ", (test2 == self.save_mr).all())
            #
            # CTcrop_x = self.ct_pos_x
            # CTcrop_y = self.ct_pos_y
            #
            # ## ROI 범위 지정
            # height = int(self.ROI_height)
            # width = int(self.ROI_width / 2)
            #
            # ### ROI를 저장변수에 저장
            # CTcrop_image = np.copy(self.dcmfilect.pixel_array[CTcrop_y:CTcrop_y + height, CTcrop_x - width:CTcrop_x + width])
            # tempct = CTcrop_image.astype(np.uint16)
            # print("저장 후 파일과 dcm 파일의 픽셀 비교 : ", (test == tempct).all())
            # print("저장 전 파일과 dcm 파일의 픽셀 비교 : ", (tempct == self.save_ct).all())
            #
            # x = self.mr_pos_x
            # y = self.mr_pos_y
            # ## ROI 범위 지정
            # height = int(self.ROI_height)
            # width = int(self.ROI_width / 2)
            # ### ROI를 저장변수에 저장
            # tempmr = np.copy(self.resizemr[y:y + height, x - width:x + width])
            #
            # ## 픽셀 얼만큼 차이나는지 테스트
            # minus = tempmr - test2
            # one = 0
            # zero = 0
            # for i in range(height):
            #     for j in range(width*2):
            #         if minus[i, j] == 0:
            #             zero += 1
            #         elif minus[i,j] == 1:
            #             one += 1
            #
            # print("저장 후 파일과 dcm 파일의 픽셀 비교 : ", (test2 == tempmr).all())
            # print("저장 전 파일과 dcm 파일의 픽셀 비교 : ", (tempmr == self.save_mr).all())
        except:
            mb = QtWidgets.QMessageBox()
            mb.setIcon(QtWidgets.QMessageBox.Information)
            mb.setWindowTitle('Error!!!')
            mb.setText('차례대로 다시 실행해주세요')
            mb.setStandardButtons(QtWidgets.QMessageBox.Ok)
            mb.exec()
            mb.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Pixel_gui()
    ex.show()
    sys.exit(app.exec_())

