import nibabel as nib
import pydicom
import cv2
import matplotlib.pyplot as plt
import skimage.io as skimage
from skimage import data, io, filters
import numpy as np

# org = pydicom.dcmread('origin.dcm')
# niidcm = pydicom.dcmread('res.dcm')
# cmd = pydicom.dcmread('m000-ori.dcm')
program = pydicom.dcmread('program.dcm')
# nii = nib.load('ori.nii')
# nii_data= nii.get_data()
# nii2 = nib.load('ori2.nii')
# nii2_data= nii.get_data()

# a = np.array((org.pixel_array.shap[0], org.pixel_array.shape[1]), dtype=np.uint16)

# c = Image.open('origin.bmp')
# pixel = np.array(c)
# print("PIL : ", pixel.dtype)
# print(max(max(row) for row in pixel))


testimg = plt.imread('program.png')
testimg2 = plt.imread('programori.png')



# t1 = testimg[500:700]
# t2 = testimg2[500:700]
# for i in range(len(t1)):
#    print(t1[i] - t2[i])



# matlab.imsave('program.png', program.pixel_array)
# matlab.imsave('origin.png', org.pixel_array)


skimage.imsave('test.tif', program.pixel_array, plugin="freeimage")
tt = skimage.imread('test.tif', as_gray=True)

# ## 원본데이터
# tttt = cv2.imread('test.tif', cv2.IMREAD_UNCHANGED)
# ## cv2.imwrite로 저장한 파일
# ttttt = cv2.imread('tttt.tif', cv2.IMREAD_UNCHANGED)
# ## 차이 빼보면 큰 차이가 없는듯
# # for i in range(len(tttt)):
# #     print(tttt[i] - ttttt[i])

# io.imshow(tt)
# io.show()

testtt = io.imread('programori.tif')
io.imshow(testtt)
io.show()

print()

# readpng = cv2.imread('test.png', cv2.IMREAD_ANYCOLOR)
# print("Max : ", nii_data.max(), " // Min : ", nii_data.min())
# print("Max : ", nii2_data.max(), " // Min : ", nii2_data.min())



# medcon -f ori.nii -c dicom -b16 
# -fv랑 -rs를 해서 뒤집어는 줘야됨 시리즈로 하면 순서가 바뀌룻있으니까 그거 고려해야함
#일단은 skimage.imsave를 이용해서 tif형식으로 원본을 저장가능