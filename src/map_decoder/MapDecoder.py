from functools import cached_property

import numpy as np
from PIL import Image


class MapDecoder:
    @classmethod
    def open(cls, filepath: str) -> "MapDecoder":
        pil_image = Image.open(filepath)
        return cls(pil_image)

    def __init__(self, pil_image):
        self.pil_image = pil_image

    @cached_property
    def color_matrix(self) -> np.ndarray:
        image_rgb = self.pil_image.convert("RGB")
        color_matrix = np.array(image_rgb, dtype=np.float32) / 255.0
        return color_matrix
