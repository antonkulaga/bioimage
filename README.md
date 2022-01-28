# bioimage
Library for convenient handling of bioimages

Contains the following modules:

## io

Convenient file management, uses pims and pycomfort under the hood.

def load_bio_image(from_file: Path) allows loading microscopy images
def load_frame(from_file: Path) loads first frame of the microscopy image from system path