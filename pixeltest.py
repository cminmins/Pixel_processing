import nibabel as nib
import pydicom
from dipy.align.reslice import reslice
import cv2
import skimage.io as skimage
from skimage import data, io, filters, color
import numpy as np

org = pydicom.dcmread('origin.dcm')
org_pix = org.pixel_array
after_org = pydicom.dcmread('m000-s0001-s000a001.dcm')
after_org_pix = after_org.pixel_array
res_dcm = pydicom.dcmread('m000-after.dcm')
res_dcm_pix = res_dcm.pixel_array

nii_file = nib.load('s000a001.nii')
nii_array = nii_file.get_data()
nii_affine = nii_file.affine
nii_zooms = nii_file.header.get_zooms()

new_nii, new_affine = reslice(nii_array, nii_affine, nii_zooms, nii_zooms)
print(new_nii.dtype)

# new_nii = np.array(new_nii, dtype='int16')
# new_nii.astype('uint16')
print(new_nii.dtype)

new_nii_image = nib.Nifti1Image(new_nii, new_affine)
nib.save(new_nii_image,'after.nii')

# org = pydicom.dcmread('60002.dcm')
# org_pix = org.pixel_array
# after_org = pydicom.dcmread('m001-s0001-s000a1001.dcm')
# after_org_pix = after_org.pixel_array
# res_dcm = pydicom.dcmread('m000-s0001-Reslice_mri_1.dcm')
# res_dcm_pix = res_dcm.pixel_array

#
# nii = nib.load('30005.nii')
# nii_data = nii.get_data()
# res_nii = nib.load('Reslice_ct_1.nii')
# res_nii_data = res_nii.get_data()
#
#
# # skimage.imsave('test.tif', program.pixel_array, plugin="tifffile")
# ski_prog = skimage.imread('test.tif')
# ski_prog_gray = skimage.imread('test.tif', as_gray=True)

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

# io.imshow(org.pixel_array)
# io.show()

print()





# medcon -f ori.nii -c dicom -b16 
# -fv랑 -rs를 해서 뒤집어는 줘야됨 시리즈로 하면 순서가 바뀌룻있으니까 그거 고려해야함
#일단은 skimage.imsave를 이용해서 tif형식으로 원본을 저장가능 무압축으로