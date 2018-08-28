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

        self.mr_hor.valueChanged.connect(self.changeRatio)
        self.mr_ver.valueChanged.connect(self.changeRatio)

    def keyPressEvent(self, e):
    #     # if e.key() == QtCore.Qt.Key_1:
    #     #     디렉토리 1 증가
    #     # elif e.key() == QtCore.Qt.Key_2:
    #     #     CT+MR 리스트 1 증가
    #     # elif e.key() == QtCore.Qt.Key_3:
    #     #     CT 리스트 1 증가
    #     # elif e.key() == QtCore.Qt.Key_4:
    #     #     MR 리스트 1 증가

        if e.key() == QtCore.Qt.Key_W:
            print('W')
            self.ct_up()
        elif e.key() == QtCore.Qt.Key_S:
            print('W')
            self.ct_down()
        elif e.key() == QtCore.Qt.Key_A:
            print('W')
            self.ct_left()
        elif e.key() == QtCore.Qt.Key_D:
            print('W')
            self.ct_right()


        elif e.key() == QtCore.Qt.Key_I:
            self.mr_up()
        elif e.key() == QtCore.Qt.Key_K:
            self.mr_down()
        elif e.key() == QtCore.Qt.Key_J:
            self.mr_left()
        elif e.key() == QtCore.Qt.Key_L:
            self.mr_right()


        elif e.key() == QtCore.Qt.Key_Enter:
            self.savetiff()
        elif e.key() == QtCore.Qt.Key_Backspace:
            self.save_ratio()
    #     # elif e.key() == QtCore.Qt.Key_9:
    #     #     가로 크기 -
    #     # elif e.key() == QtCore.Qt.Key_0:
    #     #     가로 크기 +
    #     # elif e.key() == QtCore.Qt.Key_Underscore:
    #     #     세로 크기 -
    #     # elif e.key() == QtCore.Qt.Key_Equal:
    #     #     세로 크기 +

    def ct_savepos(self, event):
        self.ct_pos_x = int(event.pos().x()) * 2
        self.ct_pos_y = int(event.pos().y()) * 2
        self.cropCT()

    def mr_savepos(self, event):
        self.mr_pos_x = int(event.pos().x()) * 2
        self.mr_pos_y = int(event.pos().y()) * 2
        self.cropMR()

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
        width = int(self.change_width/2)
        height = int(self.change_height)

        MRcrop_image = np.copy(self.resizemr[y:y+height, x-width:x+width])
        self.save_mr = resize(MRcrop_image, (700, 600), anti_aliasing=True, order=3)
        self.save_mr = (self.save_mr * 65535).astype(np.uint16)

        pixmap = self.display_qlabel(self.resizemr, 1, x, y)

    def overlay(self):
        CTover_image = resize(self.save_ct, (450, 400), anti_aliasing=True, order=3)
        CTover_image = (CTover_image * 65535).astype(np.uint16)
        MRover_image = resize(self.save_mr, (450, 400), anti_aliasing=True, order=3)
        MRover_image = (MRover_image * 65535).astype(np.uint16)

        over_image = (CTover_image - MRover_image) * 2
        over_pixmap = self.display_qlabel(over_image)
        self.qlabel_overay.setPixmap(over_pixmap)

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

    def changeRatio(self):
        x = self.mr_pos_x
        y = self.mr_pos_y
        self.change_width = 600 + self.mr_hor.value() * 4
        self.change_height = 700 + self.mr_ver.value() * 4
        self.resize_ratio()
        self.cropMR()

    def cropCT(self):
        CTcrop_x = self.ct_pos_x
        CTcrop_y = self.ct_pos_y

        ### ROI를 저장변수에 저장
        CTcrop_image = np.copy(self.dcmfilect.pixel_array[CTcrop_y:CTcrop_y+700, CTcrop_x-300:CTcrop_x+300])
        self.save_ct = CTcrop_image.astype(np.uint16)

        ### ROI를 CT_crop에 출력
        pixmap = self.display_qlabel(self.save_ct)
        pixmap = pixmap.scaled(self.qlabel_CT_crop.width(), self.qlabel_CT_crop.height(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT_crop.setPixmap(pixmap)

        ### 원본에서 ROI에 네모박스 출력
        pixmap = self.display_qlabel(self.dcmfilect.pixel_array, 1, self.ct_pos_x, self.ct_pos_y)
        pixmap = pixmap.scaled(self.qlabel_CT.width(), self.qlabel_CT.height(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT.setPixmap(pixmap)

    def cropMR(self):
        x = self.mr_pos_x
        y = self.mr_pos_y

        ### ROI를 저장변수에 저장
        self.save_mr = np.copy(self.resizemr[y:y+700, x-300:x+300])
        ## astype으로 uint16할 필요가 있을까?

        ### 현재 비율대로 사진 조정
        self.resize_ratio()

        ### ROI를 MR_crop에 출력
        pixmap = self.display_qlabel(self.save_mr)
        pixmap = pixmap.scaled(self.qlabel_MR_crop.width(), self.qlabel_MR_crop.height(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR_crop.setPixmap(pixmap)

        ### 오버레이 이미지 출력
        self.overlay()

        ### 원본에서 ROI에 네모박스 출력
        pixmap = self.display_qlabel(self.resizemr, 1, self.mr_pos_x, self.mr_pos_y)
        pixmap = pixmap.scaled(self.qlabel_MR.width(), self.qlabel_MR.height(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR.setPixmap(pixmap)

    def selectimageCT(self):
        ### List_CT에서 선택파일명을 가져온 다음에 pydicom으로 열기
        dcmitem = self.List_CT.selectedItems()[0].text()
        self.dcmfilect = pydicom.dcmread(dcmitem)

        ### 선택한 파일이미지를 CT에 출력
        pixmap = self.display_qlabel(self.dcmfilect.pixel_array)
        pixmap = pixmap.scaled(self.qlabel_CT.width(), self.qlabel_CT.height(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_CT.setPixmap(pixmap)

    def selectimageMR(self):
        ### List MR에서 선택파일명을 가져온 다음에 pydicom으로 열기
        dcmitem = self.List_MR.selectedItems()[0].text()
        self.dcmfilemr = pydicom.dcmread(dcmitem)

        ### 256 * 256 -> 1024 * 1024로 변환
        self.resizemr = np.copy(self.dcmfilemr.pixel_array)
        self.resizemr = resize(self.resizemr, (1024, 1024), anti_aliasing=True, order=3)
        self.resizemr = (self.resizemr * 32767).astype(np.uint16)
        ### 65535가 아니라 32767??

        ### 선택한 파일이미지를 MR에 출력
        pixmap = self.display_qlabel(self.resizemr)
        pixmap = pixmap.scaled(self.qlabel_MR.width(), self.qlabel_MR.height(), QtCore.Qt.KeepAspectRatioByExpanding)
        self.qlabel_MR.setPixmap(pixmap)

    def display_qlabel(self, base, drawRect=0, x=0, y=0):
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
            painter.setPen(QtCore.Qt.white)
            width = int(self.change_width/2)
            height = int(self.change_height)
            painter.drawRect(x-width, y, width * 2, height)
            painter.end()
            pixmap = QtGui.QPixmap(result)
        return pixmap

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

# medcon -f *.nii -split3d -c dicom -b16
# medcon -f *.dcm -stack3d -c nifty -b16

