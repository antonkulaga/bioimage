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


def folder_to_conditions(p: Path, file_column: str = "file", ext: str = "czi", ind: int = -1, sep: str ="_"):
    """
    :param p: path to the folder
    :param ext: extension of files to consider (czi by default)
    :param ind: where condition is inside file name
    :param sep: separator, _ by default
    :return: pandas dataframe
    """
    return with_ext(p, ext).map(lambda f: to_condition(f, ind, sep)).to_pandas(["condition", "num", file_column, "selected"])