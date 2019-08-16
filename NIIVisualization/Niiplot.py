from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
import SimpleITK as sitk
import skimage.io as io
import pylab
from dataprocessor.tools import get_bounding_box
from  NIIVisualization.myshow import myshow3d

def read_img(path):
    img=sitk.ReadImage(path)
    print(img)
    data=sitk.GetArrayFromImage(img)
    return data
def show_img(data):
    for i in range(data.shape[0]):
        io.imshow(data[i,:,:],cmap="gray")
        print(i)
        io.show()
def show_slice(data):
    io.imshow(data, cmap="gray")
    io.show()
def plot3D(Image):
    multi_slice_viewer(Image)
def multi_slice_viewer(volume,is_lable=False):
    remove_keymap_conflicts({'j', 'k'})
    fig, ax = plt.subplots()
    ax.volume = volume
    if is_lable:
        bbox = get_bounding_box(volume)
        ax.index=(bbox[0].stop+bbox[0].start)//2
    else:
        ax.index = volume.shape[0] // 2
    ax.imshow(volume[ax.index])
    fig.canvas.mpl_connect('key_press_event', process_key)
    pylab.show()
def process_key(event):
    fig = event.canvas.figure
    ax = fig.axes[0]
    if event.key == 'j':
        previous_slice(ax)
    elif event.key == 'k':
        next_slice(ax)
    fig.canvas.draw()
def previous_slice(ax):
    volume = ax.volume
    ax.index = (ax.index - 1) % volume.shape[0]  # wrap around using %
    ax.images[0].set_array(volume[ax.index])
    ax.set_title(ax.index)
def remove_keymap_conflicts(new_keys_set):
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)
def next_slice(ax):
    volume = ax.volume
    ax.index = (ax.index + 1) % volume.shape[0]
    ax.images[0].set_array(volume[ax.index])
    ax.set_title(ax.index)
if __name__== "__main__":


    nii=nib.load("../data/mr_train_1003_label.nii.gz")
    data=nii.get_data()
    get_bounding_box(data)
    intensity=np.sort(np.unique(data))
    print(intensity)
    labels=[]
    for i,gray in enumerate(intensity[1:]):
        labels.append(np.copy(data))
        labels[i]=np.where(labels[i]==gray,1,0)
        # show_slice(labels[i][:,:,56])
        # print(i)
        # multi_slice_viewer(labels[i])
        print(np.count_nonzero(labels[i]))
    labels_4D=np.stack(labels,-1)
    [multi_slice_viewer(labels_4D[...,i].T,is_lable=True) for i in range(labels_4D.shape[-1])]
    [print(np.unique(labels_4D[..., i]))for i in range(labels_4D.shape[-1])]




    # data=data.T
    # data=read_img("../mr_train_1001_image.nii.gz")
    # show_img(data)
    # multi_slice_viewer(data)
    #label-reg的数据
    nii2=nib.load("../data/train/mr_labels/case000000.nii.gz")
    data2=nii2.get_data()
    # [multi_slice_viewer(data2[...,i]) for i in range(data2.shape[-1])]
    [print(np.unique(data2[..., i]))for i in range(data2.shape[-1])]
    print("test")
