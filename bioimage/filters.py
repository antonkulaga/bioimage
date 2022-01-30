import numpy as np
import pandas
import skimage
from skimage import filters, morphology, img_as_float64
from skimage.exposure import rescale_intensity
from enum import Enum
from numpy.typing import ArrayLike, NDArray

from beartype import beartype

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
def merge_glowing(normal_image: np.ndarray, glowing_image: np.ndarray, color: Color = Color.GREEN,
                  correction: bool = True, ball: int = 30, glowing_part: float = 0.5):
    """
    :param normal_image: image without fluorescence
    :param glowing_image: image with fluorescence
    :param color: color, GFP by default
    :param correction:
    :param ball:
    :param glowing_part:
    :return:
    """
    normal_frame = img_as_float64(skimage.color.gray2rgb(normal_image))
    glowing_frame = img_as_float64(glowing_image)
    glowing = gray2color(rolling_ball(glowing_frame, ball), color) if correction else gray2color(glowing_frame, color)
    return normal_frame * (1 - glowing_part) + glowing * glowing_part


@beartype
def local_contrast(image: np.ndarray):
    imageRooted = image ** 2
    imageRootedConvolved = skimage.filters.gaussian(imageRooted, 1.2)
    imageConvolved   =  skimage.filters.gaussian(image, 1.2)
    imageConvolvedRooted = imageConvolved  ** 2
    return np.sqrt(imageRootedConvolved - imageConvolvedRooted) / imageConvolved


@beartype
def thresh(img, clahe: bool = False, median: bool = False, gaus: bool = True):
    img = skimage.filters.gaussian(img, 1.2) if gaus else img
    image_eq = skimage.exposure.equalize_adapthist(img, kernel_size=None, clip_limit=0.01, nbins=256) if clahe else img
    image = (skimage.filters.median(image_eq) if median else image_eq).copy()
    binary = image > skimage.filters.threshold_mean(image)
    image[binary] = 0
    return image


@beartype
def clean_small(image: np.ndarray, size: int = 1):
    selem =  morphology.disk(size)
    res = morphology.white_tophat(image, selem)
    return image - res
