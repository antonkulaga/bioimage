from datetime import datetime
from pathlib import Path
from typing import Union
import skimage
from skimage.exposure import rescale_intensity
from skimage import util, filters, morphology
import matplotlib.pyplot as plt
import numpy as np
import pims
from functional import seq
from pims import *
from pycomfort.files import *


def rolling_ball(image, radius=20, light_bg=False):
    """
    Function to subtract background, be careful with radius as it can overload the PC!
    :param image: image
    :param radius: radius of the rolling ball
    :param light_bg: if the background is supposed to be light
    :return: corrected image
    """
    from skimage.morphology import white_tophat, black_tophat, disk
    str_el = disk(radius)
    return black_tophat(image, str_el) if light_bg else white_tophat(image, str_el)


def local_contrast(image):
    imageRooted = image ** 2
    imageRootedConvolved = skimage.filters.gaussian(imageRooted, 1.2)
    imageConvolved   =  skimage.filters.gaussian(image, 1.2)
    imageConvolvedRooted = imageConvolved  ** 2
    return np.sqrt(imageRootedConvolved - imageConvolvedRooted) / imageConvolved


def thresh(img, clahe: bool = False, median: bool = False, gaus: bool = True):
    img = skimage.filters.gaussian(img, 1.2) if gaus else img
    image_eq = skimage.exposure.equalize_adapthist(img, kernel_size=None, clip_limit=0.01, nbins=256) if clahe else img
    image = (skimage.filters.median(image_eq) if median else image_eq).copy()
    binary = image > skimage.filters.threshold_mean(image)
    image[binary] = 0
    return image


def clean_small(image, size = 1):
    selem =  morphology.disk(size)
    res = morphology.white_tophat(image, selem)
    return image - res