
#
# load.py : utils on generators / lists of ids to transform from strings to
#           cropped images and masks

import os
import numpy as np
import pandas as pd

from PIL import Image
from functools import partial
from .utils import resize, normalize


def get_ids(dir):
    """Returns a list of the ids in the directory"""
    return (f[:-4] for f in os.listdir(dir))

def split_ids(ids, n=2):
    """Split each id in n, creating n tuples (id, k) for each id"""
    return ((id, i) for i in range(n) for id in ids)

def yield_imgs(ids, dir, suffix, scale):
    """From a list of tuples, returns the correct cropped img"""
    for id, pos in ids:
        im = Image.open(dir + id + suffix)
        im = resize(im, scale)
        yield im

def yield_depth_masks(ids, dir, suffix):
    """From a list of depth map, returns the correct cropped img"""
    yield_flag = True

    to_return = []
    for id, pos in ids:
        # im = resize_and_crop(Image.open(dir + id + suffix))
        df = pd.read_csv(dir+id+suffix, header=None)
        if not yield_flag:
            to_return.append(df.values.tolist())
        else:
            yield df.values.tolist()
    if not yield_flag:
        return to_return

def yield_masks(ids, dir, suffix, scale):
    """From a list of tuples, returns the correct cropped img"""
    to_return = []
    for id, pos in ids:
        im = Image.open(dir + id + suffix)
        im = resize(im, scale)
        to_return.append(np.array(im)/255)
    return to_return


def get_imgs_and_masks(ids, dir_img, dir_mask, scale):
    """Return all the couples (img, mask)"""

    # need to transform from HWC to CHW
    imgs = yield_imgs(ids, dir_img, ".jpg", scale)
    imgs_switched = map(partial(np.transpose, axes=[2, 0, 1]), imgs)
    imgs_normalized = map(normalize, imgs_switched)
    if "depth" in dir_mask:
        masks = yield_depth_masks(ids, dir_mask, '.txt')
    else:
        masks = yield_masks(ids, dir_mask, '.jpg')
        masks_switched = map(partial(np.transpose, axes=[0]), masks)
        masks_normalized = map(normalize, imgs_switched)
        masks = masks_normalized

    return zip(imgs_normalized, masks)

