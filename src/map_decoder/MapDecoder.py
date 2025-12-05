from gig import EntType
from PIL import Image
from utils import Log

from map_decoder.MapDecoderDrawMixin import MapDecoderDrawMixin
from map_decoder.MapDecoderGeoMixin import MapDecoderGeoMixin
from map_decoder.MapDecoderImageMixin import MapDecoderImageMixin

log = Log("MapDecoder")


class MapDecoderEntMixin:
    @staticmethod
    def get_ent_to_label_to_n(info_list):
        idx = {}
        for info in info_list:
            ent_id = info["ent_id"]
            label = info["label"]

            if ent_id not in idx:
                idx[ent_id] = {}
            if label not in idx[ent_id]:
                idx[ent_id][label] = 0

            idx[ent_id][label] += 1

        return idx


class MapDecoder(
    MapDecoderImageMixin,
    MapDecoderGeoMixin,
    MapDecoderDrawMixin,
    MapDecoderEntMixin,
):

    def __init__(self, pil_image):
        self.pil_image = pil_image

    @classmethod
    def open(cls, filepath: str) -> "MapDecoder":
        pil_image = Image.open(filepath)
        return cls(pil_image)

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
        color_matrix = MapDecoder.get_color_matrix(
            pil_image=self.pil_image,
            n_clusters=n_clusters,
            min_saturation=min_saturation,
            color_background=color_background,
        )

        info_list = MapDecoder.get_latlng_color_info_list(
            reference_list=reference_list,
            color_background=color_background,
            box_size_lat=box_size_lat,
            map_ent_type=map_ent_type,
            color_to_label=color_to_label,
            color_matrix=color_matrix,
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

        ent_to_label_to_n = self.get_ent_to_label_to_n(info_list)

        image_for_ents = MapDecoder.generate_image_for_ents(
            ent_to_label_to_n=ent_to_label_to_n,
            color_to_label=color_to_label,
        )

        return (
            info_list,
            image_inspection,
            image_info_list,
            most_common_colors,
            ent_to_label_to_n,
            image_for_ents,
        )
