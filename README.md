# bioimage
Library for convenient handling of bioimages

Contains the following modules:

## io

Convenient file management, uses pims and pycomfort under the hood.
For example:
* load_bio_image(from_file: Path) that allows loading microscopy images
* load_frame(from_file: Path): that loads first frame of the microscopy image from the system path

## filters

Useful filters to process images.
For example:
* rolling ball filter to fix some issues on the background
* local_contrast filter that can be used together with thresholding to find boundaries of the objects
* gray2color that deals with fluorescent images
* glowing - for dealing with comparisons between normal and fluorescent images

## comparisons

When you need to compare multiple conditions
For example:
* show_images that displays images from the whole folder as a grid plot
* folder_to_conditions that allows splitting images in the folder to multiple conditions based on their namings
* get_glowing_overlays that allows combining fluorescent and phase-contrast images