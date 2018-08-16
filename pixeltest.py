import nibabel as nib
import pydicom
import cv2
import skimage.io as skimage
from skimage import data, io, filters, color
import numpy as np

org = pydicom.dcmread('origin.dcm')
# niidcm = pydicom.dcmread('res.dcm')
# cmd = pydicom.dcmread('m000-ori.dcm')
# program = pydicom.dcmread('program.dcm')
# nii = nib.load('ori.nii')
# nii_data= nii.get_data()
# nii2 = nib.load('ori2.nii')
# nii2_data= nii.get_data()

# skimage.imsave('test.tif', program.pixel_array, plugin="tifffile")
ski_prog = skimage.imread('test.tif')
ski_prog_gray = skimage.imread('test.tif', as_gray=True)

#### skimage로 저장하면 무압축
#### cv2로 저장하면 LZW로 압축
# # ## 원본데이터
# cv_prog = cv2.imread('test.tif', cv2.IMREAD_UNCHANGED)
# # ## cv2.imwrite로 저장한 파일
# cv2.imwrite('cv2_prog.tif', cv_prog)
# cv_prog_sec  = cv2.imread('cv2_prog.tif', cv2.IMREAD_UNCHANGED)
# # ## 차이 빼보면 큰 차이가 없는듯
# # # for i in range(len(tttt)):
# # #     print(tttt[i] - ttttt[i])

io.imshow(org.pixel_array)
io.show()

print()





# medcon -f ori.nii -c dicom -b16 
# -fv랑 -rs를 해서 뒤집어는 줘야됨 시리즈로 하면 순서가 바뀌룻있으니까 그거 고려해야함
#일단은 skimage.imsave를 이용해서 tif형식으로 원본을 저장가능 무압축으로