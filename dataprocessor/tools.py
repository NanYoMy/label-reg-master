
import numpy as np

def get_bounding_box(x):
    """ Calculates the bounding box of a ndarray"""
    mask = x == 0
    bbox = []
    all_axis = np.arange(x.ndim)
    for kdim in all_axis:
        nk_dim = np.delete(all_axis, kdim)
        mask_i = mask.all(axis=tuple(nk_dim))
        dmask_i = np.diff(mask_i)#边缘滤波
        idx_i = np.nonzero(dmask_i)[0]#idx_i[0]不为0的x坐标
        if len(idx_i) < 2:
            raise ValueError('Algorithm failed, {} does not have more than 2 elements!'.format(idx_i))
        bbox.append(slice(idx_i[0]+1, idx_i[-1]+1))
    return bbox
