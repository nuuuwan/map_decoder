import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from utils import Log

log = Log("MapDecoderImageMixin")


class MapDecoderImageMixin:

    @staticmethod
    def cluster_colors(
        color_array: np.ndarray,
        n_clusters: int,
    ) -> np.ndarray:
        original_shape = color_array.shape
        pixels = color_array.reshape(-1, 3)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(pixels)

        clustered_pixels = kmeans.cluster_centers_[kmeans.labels_]

        clustered_array = clustered_pixels.reshape(original_shape)

        return clustered_array.astype(np.float32)

    @staticmethod
    def replace_low_saturation_colors(
        color_array: np.ndarray,
        min_saturation: float,
        color_background: tuple[int, int, int],
    ) -> np.ndarray:
        result_array = color_array.copy()

        normalized = color_array / 255.0
        r, g, b = (
            normalized[:, :, 0],
            normalized[:, :, 1],
            normalized[:, :, 2],
        )

        max_val = np.maximum(np.maximum(r, g), b)
        min_val = np.minimum(np.minimum(r, g), b)
        diff = max_val - min_val

        saturation = np.where(max_val != 0, diff / max_val, 0)

        low_sat_mask = saturation < min_saturation

        result_array[low_sat_mask] = color_background

        return result_array

    @staticmethod
    def get_color_matrix(
        pil_image: Image.Image,
        n_clusters: int,
        min_saturation: float,
        color_background: tuple[int, int, int],
    ) -> np.ndarray:
        image_rgb = pil_image.convert("RGB")
        color_array = np.array(image_rgb, dtype=np.float32)
        color_array = MapDecoderImageMixin.replace_low_saturation_colors(
            color_array=color_array,
            min_saturation=min_saturation,
            color_background=color_background,
        )
        color_array = MapDecoderImageMixin.cluster_colors(
            color_array=color_array,
            n_clusters=n_clusters,
        )
        color_array = MapDecoderImageMixin.replace_low_saturation_colors(
            color_array=color_array,
            min_saturation=min_saturation,
            color_background=color_background,
        )
        color_matrix = color_array / 255.0
        return color_matrix

    @staticmethod
    def get_most_common_colors(
        info_list: list[dict],
    ) -> dict[tuple, int]:
        color_count = {}
        for info in info_list:
            color = info["color"]
            if color not in color_count:
                color_count[color] = 0
            color_count[color] += 1
        n = len(info_list)

        color_p_count = dict(
            {k: round(v / n, 4) for k, v in color_count.items()}
        )

        color_p_count = dict(
            sorted(
                color_p_count.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
        return color_p_count
