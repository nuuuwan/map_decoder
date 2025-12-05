from functools import cached_property

import numpy as np
from PIL import Image, ImageDraw, ImageFont


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

    def __generate_inspection_image__(
        self, reference_list: list[dict]
    ) -> Image.Image:
        result_image = self.pil_image.copy()
        draw = ImageDraw.Draw(result_image)

        try:
            font = ImageFont.truetype("Arial.ttf", 12)
        except OSError:
            font = ImageFont.load_default()

        for ref in reference_list:
            label = ref.get("label", "")
            xy = ref.get("xy", (0, 0))
            latlng = ref.get("latlng", (0, 0))
            x, y = xy
            radius = 5
            draw.ellipse(
                [(x - radius, y - radius), (x + radius, y + radius)],
                fill="red",
                outline="black",
                width=2,
            )

            text = f"{label}\n{latlng}"
            draw.text((x + 8, y - 8), text, fill="black", font=font)

        return result_image

    def decode(self, reference_list: list[dict]) -> Image.Image:
        inspection_image = self.__generate_inspection_image__(reference_list)
        return inspection_image
