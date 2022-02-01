from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'bioimage - library to make working with biomedical images more comfortable'
LONG_DESCRIPTION = 'A package with python helper functions to make your work with bioimages more comfortable'

# Setting up
setup(
    name="bioimage",
    version=VERSION,
    author="antonkulaga (Anton Kulaga)",
    author_email="<antonkulaga@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['beartype', 'matplotlib', 'pandas', 'pycomfort','more-itertools', "pims", "scikit-image", "jpype1", "opencv-python", 'tifffile'],
    keywords=['python', 'utils', 'files', "bioimages", "microscopy", "imaging", "numpy"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
