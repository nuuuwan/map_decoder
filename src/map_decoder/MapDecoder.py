import colorsys
import tempfile

import matplotlib.pyplot as plt
import numpy as np
from gig import Ent, EntType
from PIL import Image, ImageDraw, ImageFont
from utils import Log

log = Log("MapDecoder")


class MapDecoder:
    @classmethod
    def open(cls, filepath: str) -> "MapDecoder":
        pil_image = Image.open(filepath)
        return cls(pil_image)

    def __init__(self, pil_image):
        self.pil_image = pil_image

    @staticmethod
    def quantize_color_array(
        color_array: np.ndarray, q: int = 16
    ) -> np.ndarray:
        return np.int16(color_array / q) * q

    @staticmethod
    def get_color_matrix(pil_image) -> np.ndarray:
        image_rgb = pil_image.convert("RGB")
        color_array = np.array(image_rgb, dtype=np.float32)
        color_array = MapDecoder.quantize_color_array(color_array)
        color_matrix = color_array / 255.0
        return color_matrix

    @staticmethod
    def generate_inspection_image(
        pil_image: Image.Image, reference_list: list[dict]
    ) -> Image.Image:
        result_image = pil_image.copy()
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

    @staticmethod
    def get_latlng_transform_coefficients(
        reference_list: list[dict],
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        assert (
            len(reference_list) >= 4
        ), "At least 4 reference points are required."
        (lat1, lng1), (lat2, lng2), (lat3, lng3), (lat4, lng4) = (
            reference_list[0]["latlng"],
            reference_list[1]["latlng"],
            reference_list[2]["latlng"],
            reference_list[3]["latlng"],
        )

        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = (
            reference_list[0]["xy"],
            reference_list[1]["xy"],
            reference_list[2]["xy"],
            reference_list[3]["xy"],
        )

        m_lat = (lat2 - lat1) / (y2 - y1)
        c_lat = lat1 - m_lat * y1

        m_lng = (lng4 - lng3) / (x4 - x3)
        c_lng = lng3 - m_lng * x3
        return (m_lat, c_lat), (m_lng, c_lng)

    @staticmethod
    def get_latlng_color_info_list(
        pil_image: Image.Image,
        reference_list: list[dict],
        valid_color_list: list[tuple],
        min_saturation: float = 0.2,
    ) -> list[dict]:
        color_matrix = MapDecoder.get_color_matrix(pil_image)
        info_list = []
        (m_lat, c_lat), (m_lng, c_lng) = (
            MapDecoder.get_latlng_transform_coefficients(reference_list)
        )
        for x in range(color_matrix.shape[1]):
            for y in range(color_matrix.shape[0]):
                color = tuple((color_matrix[y, x] * 255).astype(int))
                if valid_color_list and color not in valid_color_list:
                    continue

                # Filter by saturation
                r, g, b = color
                _, saturation, _ = colorsys.rgb_to_hsv(
                    r / 255.0, g / 255.0, b / 255.0
                )
                if saturation < min_saturation:
                    continue

                lat = round(y * m_lat + c_lat, 6)
                lng = round(x * m_lng + c_lng, 6)
                info_list.append(
                    dict(latlng=(lat, lng), xy=(x, y), color=color)
                )
        return info_list

    @staticmethod
    def get_most_common_colors(
        info_list: list[dict], min_p: float = 0.05
    ) -> dict[tuple, int]:
        color_count = {}
        for info in info_list:
            color = info["color"]
            if color not in color_count:
                color_count[color] = 0
            color_count[color] += 1
        n = len(info_list)
        n_limit = int(n * min_p)
        color_p_count = dict(
            {
                k: round(v / n, 4)
                for k, v in color_count.items()
                if v >= n_limit
            }
        )

        color_p_count = dict(
            sorted(
                color_p_count.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:n_limit]
        )
        return color_p_count

    @staticmethod
    def generate_info_list_image(
        info_list: list[dict],
    ) -> Image.Image:
        plt.close()
        lats = [info["latlng"][0] for info in info_list]
        lngs = [info["latlng"][1] for info in info_list]
        colors = [
            (
                info["color"][0] / 255,
                info["color"][1] / 255,
                info["color"][2] / 255,
            )
            for info in info_list
        ]
        fig, ax = plt.subplots(figsize=(10, 10))

        ax.scatter(lngs, lats, s=1, c=colors)

        district_ents = Ent.list_from_type(EntType.DISTRICT)
        for ent in district_ents:
            geo = ent.geo()
            geo.plot(ax=ax, facecolor="none", edgecolor="red", linewidth=0.5)

        temp_image_path = tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ).name
        plt.savefig(temp_image_path, dpi=300)
        plt.close(fig)
        return Image.open(temp_image_path)

    def decode(
        self,
        reference_list: list[dict],
        valid_color_list: list[tuple],
        min_saturation: float = 0.1,
    ) -> Image.Image:
        info_list = MapDecoder.get_latlng_color_info_list(
            self.pil_image, reference_list, valid_color_list, min_saturation
        )
        image_info_list = MapDecoder.generate_info_list_image(info_list)
        image_inspection = MapDecoder.generate_inspection_image(
            self.pil_image, reference_list
        )

        most_common_colors = MapDecoder.get_most_common_colors(info_list)
        return (
            info_list,
            image_inspection,
            image_info_list,
            most_common_colors,
        )
