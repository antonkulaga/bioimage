from enum import Enum

import cv2
import numpy as np
import skimage
from beartype import beartype
from skimage import filters, morphology, img_as_uint
from skimage.color import rgb2gray
from skimage.exposure import rescale_intensity


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

def gray2color(u: np.ndarray, channel: Color = Color.GREEN) -> np.ndarray:
    """
    :param u:  fluorescence image
    :param channel: Channel to code the image in (0: Red, 1: Green, 2: Blue).
    :return: The computed output image in color. Green by default
    """
    return np.dstack((
        rescale_intensity(u if channel == Color.RED else np.zeros_like(u), out_range='float'),
        rescale_intensity(u if channel == Color.GREEN else np.zeros_like(u), out_range='float'),
        rescale_intensity(u if channel == Color.BLUE else np.zeros_like(u), out_range='float'),
    ))


@beartype
def rolling_ball(image, radius: int = 20, light_bg: bool = False):
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


@beartype
def local_contrast(image: np.ndarray, multichannel: bool = False, to_uint: bool = False) -> np.ndarray:
    img = img_as_uint(image) if to_uint else image
    imageRooted = img ** 2
    imageRootedConvolved = skimage.filters.gaussian(imageRooted, 1.2, multichannel = multichannel)
    imageConvolved   =  skimage.filters.gaussian(image, 1.2, multichannel = multichannel)
    imageConvolvedRooted = imageConvolved  ** 2
    return np.clip(np.sqrt(imageRootedConvolved - imageConvolvedRooted) / imageConvolved, -1.0, 1.0)


@beartype
def thresh(img: np.ndarray, threshold: float = -1.0, to_gray: bool = True,
           fill: float = 0.0, verbose: bool = False, multichannel: bool = False,
           clahe: bool = False, median: bool = False,
           gaus: bool = False,
           to_uint: bool = True):
    img = img_as_uint(img) if to_uint else img
    img = rgb2gray(img) if to_gray and len(img.shape) != 2 else img
    img = skimage.filters.gaussian(img, 1.2, multichannel=multichannel) if gaus else img
    image_eq = skimage.exposure.equalize_adapthist(img, kernel_size=None, clip_limit=0.01, nbins=256) if clahe else img
    image = (skimage.filters.median(image_eq) if median else image_eq).copy()
    th = skimage.filters.threshold_mean(image) if threshold == -1 else threshold
    if verbose:
        if threshold < 0.0:
            print(f"setting up threshold automatically")
        print(f"threshold is {th}")
    binary = image < th
    image[binary] = fill
    return image


@beartype
def non_black_ratio(img: np.ndarray, verbose: bool = False) -> float:
    image = img if len(img.shape) == 2 else rgb2gray(img)
    tot_pix = image.size * 1.0
    # number of black pixels
    white_pix = cv2.countNonZero(image)
    ratio = white_pix / tot_pix
    if verbose:
        print(f"{white_pix} / {tot_pix} = {ratio} (non black percentage)")
    return ratio


@beartype
def clean_small(image: np.ndarray, size: int = 1):
    selem = morphology.disk(size)
    res = morphology.white_tophat(image, selem)
    return image - res
