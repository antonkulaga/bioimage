from __future__ import annotations
import numpy as np
import pandas as pd

from bioimage.io import *
import matplotlib.pyplot as plt
from beartype import beartype

from dataclasses import dataclass



@dataclass
class GlowingTrio:

    normal_image: np.ndarray
    glowing_image: np.ndarray
    merged_image: np.ndarray

    normal_path: Path = None #optional path to normal file
    glowing_path: Path = None #optional path to normal file
    merged_path: Path = None #optional merged path
    glowing_part: float = 0.5

    @staticmethod
    @beartype
    def create(normal_image: np.ndarray, glowing_image: np.ndarray, color: Color = Color.GREEN,
                          normal_ball: int = 0, glowing_ball: int = 30,
                          glowing_part: float = 0.5,
                          normal_path: Path = None, glowing_path: Path = None) -> GlowingTrio:
        """
        :param normal_image:
        :param glowing_image:
        :param color:
        :param correction:
        :param ball:
        :param glowing_part:
        :param normal_path:
        :param glowing_path:
        :return:
        """
        normal_frame = img_as_float64(skimage.color.gray2rgb(normal_image))
        normal = normal_frame if normal_ball == 0 else rolling_ball(normal_image, normal_ball)
        glowing_frame = img_as_float64(glowing_image)
        glowing = gray2color(glowing_frame, color) if glowing_ball == 0 else gray2color(rolling_ball(glowing_frame, glowing_ball), color)
        merged = normal_frame * (1 - glowing_part) + glowing * glowing_part
        return GlowingTrio(normal_image=normal, glowing_image=glowing, merged_image=merged,
                           normal_path=normal_path, glowing_path=glowing_path, glowing_part = glowing_part)

    @staticmethod
    @beartype
    def load(normal_path: Path, glowing_path: Path, color: Color = Color.GREEN, normal_ball: int = 0, glowing_ball: int = 30, glowing_part: float = 0.5):
        normal = load_frame(normal_path)
        glowing = load_frame(glowing_path)
        return GlowingTrio.create(normal, glowing, color, normal_ball, glowing_ball, glowing_part, normal_path, glowing_path)

    @beartype
    def write_merged(self, where: Path, clahe: bool = False) -> Path:
        image_2_tiff(self.merged_image, where, clahe)
        self.merged_path = where
        return where

    @beartype
    def write_tiff(self, folder: Path, merged_name: str, normal_name: str = None, glowing_name: str = None, clahe: bool = False) -> Path:
        folder.mkdir(exist_ok=True)
        if normal_name is None:
            normal_tiff = self.normal_path.stem + ".tiff"
        else:
            normal_tiff = normal_name if ".tif" in normal_name else normal_name + ".tiff"

        image_2_tiff(self.normal_image, folder / normal_tiff, clahe)

        if glowing_name is None:
            glowing_tiff = self.glowing_path.stem + ".tiff"
        else:
            glowing_tiff = glowing_name if ".tif" in glowing_name else glowing_name + ".tiff"

        image_2_tiff(self.glowing_image, folder / glowing_tiff, clahe)

        merged_tiff = merged_name if ".tif" in merged_name else merged_name + ".tiff"
        self.write_merged(folder / merged_tiff, clahe)
        return folder

    def plot_normal(self):
        plt.imshow(self.normal_image, cmap="gray")

    def plot_glowing(self):
        plt.imshow(self.glowing_image, cmap="gray")

    def plot_merged(self):
        plt.imshow(self.merged_image)