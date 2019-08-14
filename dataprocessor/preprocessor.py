from labelreg.helpers import DataReader
import numpy
import nibabel as nib

def crop_3d_image(image):
    pass

if __name__=="__main__":
    label_reader=DataReader("E:\MIA_CODE_DATA\zhuang_data\MMWHS\MRI\mr-label")
    img_reader=DataReader("E:\MIA_CODE_DATA\zhuang_data\MMWHS\MRI\mr-image")
    data=label_reader.get_data(case_indices=[1],label_indices=[1])
    # data=img_reader.get_data(case_indices=[1])
    # crop_3d_image()


