import pandas as pd

from bioimage.io import *
import matplotlib.pyplot as plt


def show_images(*images, titles=None, cols: int = 2,
                height_pixels: float = 200,
                output_folder: Path = None,
                cmap="gray",
                width_pixels: float = None):
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

    from skimage import img_as_float
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
        ax.set_title(label)
    plt.subplots_adjust(wspace=None, hspace=None)
    if output_folder is not None:
        fig.savefig(output_folder / f"condition_comparison_automatically_generated.png", bbox_inches='tight')


def show_file_images(*files: Path, cols: int = 2, height_pixels: float = 200,
                     output_folder: Path = None,
                     cmap="gray",
                     width_pixels: float = None):
    """
    shows images in a grid starting from files
    :param files:
    :param cols:
    :param height:
    :return:
    """
    titles = [file.name for file in files]
    images = seq(files).map(load_frame).to_list()
    show_images(*images, cols=cols, height_pixels = height_pixels, output_folder = output_folder, cmap= cmap, titles=titles, width_pixels=width_pixels)


def to_condition(p: Path, ind: int = -1, sep: str ="_") -> list[str]:
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


def get_image_groups(day_folder: Path, condition_index: int = -1, file_column: str = "file") -> seq[Path]:
    """
    get groups of images, for example: fluorescent/normal images
    :param day_folder:
    :param condition_index:
    :param file_column:
    :return:
    """
    return folder_to_conditions(day_folder, file_column=file_column, condition_index=condition_index).groupby("condition")[file_column].apply(seq)


def get_glowing_overlays(day_folder: Path, normal="phc", correction: bool = True, glowing_part: float = 0.5) -> list:
    results = []
    for pair in get_image_groups(day_folder):
        parts = pair.partition(lambda f: normal in f.stem)
        assert parts.len() == 2, f'{pair} should have only two files'
        normal_path: Path = parts[0][0]
        glowing_path: Path = parts[1][0]
        merged = img_as_uint(load_glowing_pair(normal_path, glowing_path, glowing_part=glowing_part, correction=correction))
        results.append((glowing_path.stem, merged))
    return results

