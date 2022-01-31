import datetime

from pims import *
from pycomfort.files import *
from skimage import color
from skimage.exposure import rescale_intensity
from skimage.util import *
from bioimage.filters import *
from beartype import beartype

@beartype
def load_bio_image(from_file: Path):
    """
    Load microscopy image
    :param from_file:
    :return:
    """
    return pims.Bioformats(str(from_file))

@beartype
def load_frame(from_file: Path):
    return load_bio_image(from_file).get_frame_2D()


@beartype
def file_image(from_file: Path):
    return from_file, load_bio_image(from_file)

def get_date(image, verbose: bool=False):
    """
    Get date of the microscopy image
    :param i:
    :param verbose:
    :return:
    """
    d = image.metadata.ImageAcquisitionDate(0)
    if verbose:
        print(d)
    return datetime.datetime.strptime(d[0:d.index("T")], '%Y-%m-%d')


@beartype
def image_2_tiff(image: Union[np.ndarray, pims.Frame], where: Union[str, Path], clahe: bool = False):
    img = skimage.exposure.equalize_adapthist(image, kernel_size=None, clip_limit=0.01, nbins=256) if clahe else image
    import tifffile
    if isinstance(image, pims.Frame):
        tifffile.imwrite(where, img, metadata=image.metadata)
    else:
        tifffile.imwrite(where, img)

@beartype
def make_tiffs(folder: Path, overwrite: bool = False, extension: str = "czi", tiff_name: str = "tiffs"):
    for d in dirs(folder):
        tiffs: Path = (d / tiff_name)
        tiffs.mkdir(parents=True, exist_ok=True)
        print(f'creating tiffs at {tiffs.as_posix()}')
        for f in files(d):
            if extension in f.suffix:
                frame = load_frame(f)
                path: Path = (tiffs / (f.stem+".tiff"))
                if path.exists():
                    if overwrite:
                        print(f'\t {path.as_posix()} exists, but we are overwriting!')
                        image_2_tiff(frame, path.as_posix(), False)
                else:
                    print(f'\t Creating tiff {path.as_posix()}')
                    image_2_tiff(frame, path.as_posix(), False)


@beartype
def load_glowing(path: Path, correction: bool = True, color: Color = Color.GREEN):
    """
    Loads glowing image
    :param path: path to the file
    :param correction: if we should use rolling_balll correction
    :param color: channel to consider, green by default
    :return:
    """
    glowing_frame = load_frame(path)
    glowing = gray2color(rolling_ball(glowing_frame), color) if correction else gray2color(glowing_frame, 1)
    return glowing