import tempfile

import matplotlib.pyplot as plt
import numpy as np
from gig import Ent, EntType
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
from utils import Log

from gig_future import EntFuture
from utils_future import Poly2GeoMapper

log = Log("MapDecoder")


class MapDecoder:
    @classmethod
    def open(cls, filepath: str) -> "MapDecoder":
        pil_image = Image.open(filepath)
        return cls(pil_image)

    def __init__(self, pil_image):
        self.pil_image = pil_image

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
        color_array = MapDecoder.replace_low_saturation_colors(
            color_array=color_array,
            min_saturation=min_saturation,
            color_background=color_background,
        )
        color_array = MapDecoder.cluster_colors(
            color_array=color_array,
            n_clusters=n_clusters,
        )
        color_array = MapDecoder.replace_low_saturation_colors(
            color_array=color_array,
            min_saturation=min_saturation,
            color_background=color_background,
        )
        color_matrix = color_array / 255.0
        return color_matrix

    @staticmethod
    def generate_inspection_image(
        pil_image: Image.Image,
        reference_list: list[dict],
        color_reference_point: tuple[int, int, int],
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
                fill=color_reference_point,
            )

            text = f"{label}\n{latlng}"
            draw.text((x + 8, y - 8), text, fill="black", font=font)

        return result_image

    @staticmethod
    def get_latlng_color_info_list(
        pil_image: Image.Image,
        reference_list: list[dict],
        min_saturation: float,
        n_clusters: int,
        color_background: tuple[int, int, int],
        box_size_lat: int,
        map_ent_type: EntType,
        color_to_label: dict[tuple, str] = None,
    ) -> list[dict]:
        color_matrix = MapDecoder.get_color_matrix(
            pil_image=pil_image,
            n_clusters=n_clusters,
            min_saturation=min_saturation,
            color_background=color_background,
        )
        info_list = []

        step = 5

        lat_params, lng_params = Poly2GeoMapper.fit(
            xys=[ref["xy"] for ref in reference_list],
            latlngs=[ref["latlng"] for ref in reference_list],
        )

        for x in range(0, color_matrix.shape[1], step):
            print(f"\t\t{x}/{color_matrix.shape[1]}", end="\r")
            for y in range(0, color_matrix.shape[0], step):

                color = tuple(
                    int(c) for c in (color_matrix[y, x] * 255).astype(int)
                )
                if color == color_background:
                    continue

                latlng = Poly2GeoMapper.transform(
                    (x, y), lat_params, lng_params
                )
                latlng = (
                    round(latlng[0], 6),
                    round(latlng[1], 6),
                )
                idx_regions = EntFuture.idx_regions_from_latlng(
                    latlng, map_ent_type
                )
                ent = idx_regions.get(map_ent_type.name)
                if not ent:
                    continue

                label = color_to_label.get(color)
                if not label:
                    log.error(f"Label not found for color: {color}")
                    continue

                info_list.append(
                    dict(
                        xy=(x, y),
                        latlng=latlng,
                        ent_id=ent.id,
                        label=label,
                        color=color,
                    )
                )
        return info_list

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

    @staticmethod
    def generate_info_list_image(
        info_list: list[dict],
        color_map_boundaries: tuple[int, int, int],
        box_size_lat: int,
        map_ent_type: EntType,
        title: str,
        color_to_label: dict[tuple, str],
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

        ents = Ent.list_from_type(map_ent_type)
        for ent in ents:
            geo = ent.geo()
            geo.plot(
                ax=ax,
                facecolor="none",
                edgecolor=color_map_boundaries,
                linewidth=0.1,
            )

        ax.scatter(
            lngs,
            lats,
            c=colors,
            s=10 / box_size_lat,
            marker="s",
        )

        for color, label in color_to_label.items():
            ax.scatter(
                [],
                [],
                c=[
                    (
                        color[0] / 255,
                        color[1] / 255,
                        color[2] / 255,
                    )
                ],
                label=label,
                marker="s",
            )
        ax.legend(loc="upper right", fontsize="small", markerscale=2)

        plt.title(title)

        temp_image_path = tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ).name
        plt.savefig(temp_image_path, dpi=300)
        plt.close(fig)
        return Image.open(temp_image_path)

    def decode(
        self,
        reference_list: list[dict],
        min_saturation: float,
        n_clusters: int,
        color_reference_point: tuple[int, int, int],
        color_map_boundaries: tuple[int, int, int],
        color_background: tuple[int, int, int],
        box_size_lat: int,
        map_ent_type: EntType,
        title: str,
        color_to_label: dict[tuple, str] = None,
    ) -> Image.Image:
        info_list = MapDecoder.get_latlng_color_info_list(
            pil_image=self.pil_image,
            reference_list=reference_list,
            min_saturation=min_saturation,
            n_clusters=n_clusters,
            color_background=color_background,
            box_size_lat=box_size_lat,
            map_ent_type=map_ent_type,
            color_to_label=color_to_label,
        )
        image_info_list = MapDecoder.generate_info_list_image(
            info_list=info_list,
            color_map_boundaries=color_map_boundaries,
            box_size_lat=box_size_lat,
            map_ent_type=map_ent_type,
            title=title,
            color_to_label=color_to_label,
        )
        image_inspection = MapDecoder.generate_inspection_image(
            pil_image=self.pil_image,
            reference_list=reference_list,
            color_reference_point=color_reference_point,
        )

        most_common_colors = MapDecoder.get_most_common_colors(
            info_list=info_list
        )
        return (
            info_list,
            image_inspection,
            image_info_list,
            most_common_colors,
        )
