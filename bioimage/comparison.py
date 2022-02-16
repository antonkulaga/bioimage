from typing import Optional

import pandas as pd

from bioimage.io import *
import matplotlib.pyplot as plt
from beartype import beartype
from skimage import img_as_float

from bioimage.glowing import GlowingTrio

numeric = Union[float, int]


@beartype
def show_images(*images, titles=Optional[Union[list, seq]], cols: int = 2,
                height_pixels: numeric = 200,
                output_folder: Optional[Path] = None,
                cmap: str = "gray",
                width_pixels: Optional[numeric], font_size: int = 16):
    '''
    Shows images in a nice grid
    :param images:
    :param titles:
    :param cols:
    :param height:
    :param output_folder:
    :param cmap:
    :return:
    '''
    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    height = height_pixels * px
    width_pixels = height_pixels if width_pixels is None else width_pixels
    width = width_pixels * px

    images = [img_as_float(img) for img in images]

    if titles is None:
        titles = [''] * len(images)
    vmin = min(map(np.min, images))
    vmax = max(map(np.max, images))
    num = len(images)
    ncols = cols if num > cols else num
    nrows = round(num / cols)
    plot_height = height * nrows
    plot_width = width * ncols
    print(f"columns ({cols}), rows ({nrows}), num ({num}), width_pixels ({width_pixels}), height_pixels ({height_pixels}), plot_height_inches ({plot_height}), plot_width_inches ({plot_width})")
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                             figsize=(plot_width, plot_height))
    fig.tight_layout()
    for ax, img, label in zip(axes.ravel(), images, titles):
        ax.imshow(img, vmin=vmin, vmax=vmax, cmap=cmap)
        ax.set_title(label, fontsize=font_size)
    plt.subplots_adjust(wspace=None, hspace=None)
    if output_folder is not None:
        fig.savefig(output_folder / f"condition_comparison_automatically_generated.png", bbox_inches='tight')

@beartype
def show_file_images(*files: Path, cols: int = 2, height_pixels: numeric = 200,
                     output_folder: Optional[Path] = None,
                     cmap: str = "gray",
                     width_pixels: Optional[numeric] = None,
                     font_size: int = 16):
    """
    :param files:
    :param cols:
    :param height_pixels:
    :param output_folder:
    :param cmap:
    :param width_pixels:
    :return:
    """
    titles = [file.name for file in files]
    images = seq(files).map(load_frame).to_list()
    show_images(*images, cols=cols,
                height_pixels=height_pixels, output_folder=output_folder,
                cmap=cmap, titles=titles, width_pixels=width_pixels,
                font_size=font_size)


@beartype
def show_glowing_overlays(trios: list[GlowingTrio],
                 cols: int = 2,
                 height_pixels: numeric = 200,
                 output_folder: Optional[Path] = None,
                 cmap: str = "gray",
                 width_pixels: Optional[numeric] = None):
    images = seq(trios).map(lambda t: t.merged_image).to_list()
    titles = seq(trios).map(lambda t: t.merged_label).to_list()
    show_images(*images, cols=cols, height_pixels = height_pixels, output_folder = output_folder, cmap= cmap, titles=titles, width_pixels=width_pixels)


@beartype
def to_condition(p: Path, ind: int = -1, sep: str = "_") -> list:
    """
    converts path into a row for condition dataframe
    it assumes that the names of the files have pars separated by "_" or other separator
    :param p path to the file
    :param ind where in a splited file name to search for condition
    :param sep separator in the file name, _ by default
    :rtype: list
    """
    split = p.stem.split(sep)
    last = split[ind]
    if last.find("(") == -1 or last.find(")") == -1:
        return [last, 0, p, True]
    else:
        start = last.index("(")
        end = last.index(")")
        num = last[start+1:end].strip()
        return [last[0:start].strip(), num, p, False]


@beartype
def folder_to_conditions(folder: Path, condition_index: int = -1, file_column: str = "file", extension: str = "czi", sep: str ="_") -> pd.DataFrame:
    """
    :param folder: path to the folder
    :param condition_index: after we split file names with the separator, which part of the splited name should be considered condition
    :param file_column: name of the file column
    :param extension: extension of the files to consider, czi by default
    :param sep: separator, "_" by default
    :return: pd.DataFrame pandas dataframe
    """
    return with_ext(folder, extension)\
        .map(lambda f: to_condition(f, condition_index, sep))\
        .to_pandas(["condition", "num", file_column, "selected"])


@beartype
def get_image_groups(day_folder: Path, condition_index: int = -1, file_column: str = "file"):
    """
    get groups of images, for example: fluorescent/normal images
    :param day_folder:
    :param condition_index:
    :param file_column:
    :return:
    """
    return folder_to_conditions(day_folder, file_column=file_column, condition_index=condition_index).groupby("condition")[file_column].apply(seq)


@beartype
def get_glowing_overlays(day_folder: Path,
                         normal="phc",
                         glowing_ball: int = 30,
                         color: Color = Color.GREEN,
                         glowing_part: float = 0.5,
                         skip_unpaired: bool = True,
                         verbose: bool = False
                         ) -> list[GlowingTrio]:
    results = []
    for pair in get_image_groups(day_folder):
        parts = pair.partition(lambda f: normal in f.stem)
        assert parts.len() == 2, f'{pair} should have only two files'
        if parts[0].len() == 1 or parts[1].len() == 1:
            normal_path: Path = parts[0][0]
            glowing_path: Path = parts[1][0]
            results.append(GlowingTrio.load(normal_path, glowing_path, color, glowing_ball=glowing_ball, glowing_part=glowing_part))
        else:
            if not skip_unpaired:
                assert parts[0].len() ==1 or parts[1].len(), f"f{parts} length are wrong: {parts[0].len()} and {parts[1].len()}"
            else:
                if verbose:
                    print(f"skipping parts with wrong length: {parts[0].len()} and {parts[1].len()}, parts are: {parts}")
    return results


@beartype
def write_glowing_overlays(day_folder: Path,
                           normal="phc",
                           prefix: str = "_merged",
                           color: Color = Color.GREEN,
                           glowing_ball: int = 30,
                           glowing_part: float = 0.5,
                           skip_unpaired: bool = True,
                           verbose: bool = False,
                           clahe: bool = False,
                           where: Optional[Path] = None
                           ) -> Path:
    tiffs: Path = day_folder / "tiffs" if where is None else where
    tiffs.mkdir(parents=True, exist_ok=True)
    trios = get_glowing_overlays(day_folder, normal, glowing_ball, color, glowing_part, skip_unpaired, verbose, clahe)
    for trio in trios:
        trio.write_tiff(where, trio.normal_path.stem.replace(normal, prefix))
    return tiffs

