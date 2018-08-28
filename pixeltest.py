import nibabel as nib
import pydicom
from dipy.align.reslice import reslice
import cv2
import skimage.io as skimage
from skimage.transform import resize
from skimage import data, io, filters, color
import numpy as np
#
org_ct = pydicom.dcmread('30008.dcm')
a1 = org_ct.pixel_array
after_org = pydicom.dcmread('m000-s0004-Reslice_ct_1.dcm')
a2 = after_org.pixel_array

# org_mr = pydicom.dcmread('60002.dcm')
# b1 = org_mr.pixel_array
# res_dcm = pydicom.dcmread('m000-s0001-Reslice_mri_36.dcm')
# b2 = res_dcm.pixel_array

print((a1==a2).all())
# print((b1==b2).all())

# CT_image = nib.load('m000-stacks-30005.nii')
# CT_array = np.copy(CT_image.get_data())
# CT_array = CT_array.astype(np.int16)
# CT_affine = CT_image.affine
# CT_zooms = CT_image.header.get_zooms()
#
# ### MRI read
# MRT2_image = nib.load('m000-stacks-60002.nii')
# MRT2_array = np.copy(MRT2_image.get_data())
# MRT2_array = MRT2_array.astype(np.int16)
# MRT2_affine = MRT2_image.affine
# MRT2_zooms = MRT2_image.header.get_zooms()
#
# ### CT의 zoom 수정
# # CT_zooma = CT_image.header['dim'][1] / MRT2_image.header['dim'][1] * CT_zooms[0]
# # CT_zoomb = CT_image.header['dim'][2] / MRT2_image.header['dim'][2] * CT_zooms[1]
# CT_zoomc = CT_image.header['dim'][3] / MRT2_image.header['dim'][3] * CT_zooms[2]
#
# ### CT의 바뀐 zoom 적용
# # change_zoomCT_L = [CT_zooma, CT_zoomb, CT_zoomc]
# change_zoomCT_L = [CT_zooms[0], CT_zooms[1], CT_zoomc]
# change_zoomCT = tuple(change_zoomCT_L)
#
# ### 수정된 zoom으로 Reslice
# newCT_brain, newCT_affine = reslice(CT_array, CT_affine, CT_zooms, CT_zooms)
# newT2_brain, newT2_affine = reslice(MRT2_array, MRT2_affine, MRT2_zooms, MRT2_zooms)
#
# ### Reslice한 파일 저장
# newCT_image = nib.Nifti1Image(newCT_brain, newCT_affine)
# newT2_image = nib.Nifti1Image(newT2_brain, newT2_affine)
# nib.save(newCT_image, "Reslice_ct.nii")
# nib.save(newT2_image, "Reslice_mri.nii")


# # skimage.imsave('test.tif', program.pixel_array, plugin="tifffile")
# ski_prog = skimage.imread('1.tif')
# test = resize(ski_prog, (800, 800), anti_aliasing=False)
# io.imshow(test)
# io.show()
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