
from labelreg.helpers import DataReader
import SimpleITK  as sitk
from dataprocessor.tools import get_bounding_box
from NIIVisualization.Niiplot import multi_slice_viewer
class NiiDataPreprocessor():
    def __init__(self,img_dir,lable_dir):
        self.img=DataReader(img_dir)
        self.label=DataReader(lable_dir)


    def preprocess(self):

        #get a lable and img
        for i in range(self.img.num_data):
            image=self.img.get_data([i])
            label=self.label.get_data([i])
            #do the process
            image,label=self.__crop(image[0,0:,0:,0:,0],label[0,0:,0:,0:,0])
            image,label=self.__resize(image,label)

        pass

    def __crop(self,image,label):

        bbox=get_bounding_box(label)
        crop_img=image[bbox[0].start:bbox[0].stop,bbox[1].start:bbox[1].stop,bbox[2].start:bbox[2].stop]
        crop_label = label[bbox[0].start:bbox[0].stop, bbox[1].start:bbox[1].stop, bbox[2].start:bbox[2].stop]
        multi_slice_viewer(crop_label)
        multi_slice_viewer(crop_img)
        return crop_img,crop_label

    def __resize(self,image,label):

        pass

    def save_all(self,imagedir,labeldir):
        for i in range(self.img.num_data):
            image = self.img.get_data([i])
            label = self.label.get_data([i])



if __name__=="__main__":
    pre=NiiDataPreprocessor("../data/test_mr-image", \
                                     "../data/test_mr-label")
    pre.preprocess()
    mr_label_reader=DataReader("E:\MIA_CODE_DATA\zhuang_data\MMWHS\MRI\mr-label")
    mr_img_reader=DataReader("E:\MIA_CODE_DATA\zhuang_data\MMWHS\MRI\mr-image")
    data=mr_label_reader.get_data(case_indices=[1],label_indices=[1])
    pre=NiiDataPreprocessor("E:\MIA_CODE_DATA\zhuang_data\MMWHS\MRI\mr-image", \
                                     "E:\MIA_CODE_DATA\zhuang_data\MMWHS\MRI\mr-label")

    # data=img_reader.get_data(case_indices=[1])
    # crop_3d_image()
