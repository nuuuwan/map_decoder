from functools import cached_property

import cv2
import numpy as np


class Image:
    def __init__(self, image_path: str):
        self.image_path = image_path

    @cached_property
    def color_matrix(self):
        image = cv2.imread(self.image_path)
        if image is None:
            raise FileNotFoundError(
                f"Image not found at path: {self.image_path}"
            )
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        color_matrix = image_rgb.astype(np.float32) / 255.0
        return color_matrix
