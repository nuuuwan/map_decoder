import numpy as np
from gig import EntType
from tqdm import tqdm
from utils import Log

from gig_future import EntFuture
from utils_future import Poly2GeoMapper

log = Log("MapDecoder")


class MapDecoderGeoMixin:

    @staticmethod
    def get_extreme_points(  # noqa: C901
        reference_list: list[dict],
    ) -> dict[str, dict]:
        x_min, x_max, y_min, y_max = (
            float("inf"),
            float("-inf"),
            float("inf"),
            float("-inf"),
        )

        for ref in reference_list:
            x, y = ref["xy"]
            extreme_point = ref.get("extreme_point", None)

            if extreme_point == "N":
                y_min = y
            elif extreme_point == "S":
                y_max = y
            elif extreme_point == "W":
                x_min = x
            elif extreme_point == "E":
                x_max = x

        return x_min, x_max, y_min, y_max

    @staticmethod
    def get_step(reference_list: list[dict], box_size_lat: float) -> int:
        lat_max = max(ref["latlng"][0] for ref in reference_list)
        lat_min = min(ref["latlng"][0] for ref in reference_list)
        y_max_image = max(ref["xy"][1] for ref in reference_list)
        y_min_image = min(ref["xy"][1] for ref in reference_list)
        log.debug(f"{lat_min=}, {lat_max=}, {y_min_image=}, {y_max_image=}")
        m_lat = (y_max_image - y_min_image) / (lat_max - lat_min)
        log.debug(f"{m_lat=}")
        step = int(m_lat * box_size_lat)
        log.debug(f"{step=}")

        return step

    @staticmethod
    def get_info(  # noqa: CFQ004
        x: int,
        y: int,
        c: np.ndarray,
        color_background: tuple[int, int, int],
        params: dict,
        color_to_label: dict[tuple, str],
        map_ent_type: EntType,
    ) -> dict | None:

        color = tuple(int(c) for c in (c * 255).astype(int))
        if color == color_background:
            return None

        label = color_to_label.get(color)
        if not label:
            log.error(f"Label not found for color: {color}")
            return None

        latlng = Poly2GeoMapper.transform((x, y), params)
        latlng = (
            round(latlng[0], 6),
            round(latlng[1], 6),
        )
        idx_regions = EntFuture.idx_regions_from_latlng(latlng, map_ent_type)
        ent = idx_regions.get(map_ent_type.name)
        if not ent:
            log.warning(f"Ent not found for latlng: {latlng} ({(x, y)})")
            return None

        info = dict(
            xy=(x, y),
            latlng=latlng,
            ent_id=ent.id,
            label=label,
            color=color,
        )

        return info

    @staticmethod
    def get_latlng_color_info_list(
        reference_list: list[dict],
        color_background: tuple[int, int, int],
        box_size_lat: int,
        map_ent_type: EntType,
        color_to_label: dict[tuple, str],
        color_matrix: np.ndarray,
    ) -> list[dict]:
        params = Poly2GeoMapper.fit(
            xys=[ref["xy"] for ref in reference_list],
            latlngs=[ref["latlng"] for ref in reference_list],
        )
        x_min, x_max, y_min, y_max = MapDecoderGeoMixin.get_extreme_points(
            reference_list=reference_list
        )
        step = MapDecoderGeoMixin.get_step(
            reference_list=reference_list,
            box_size_lat=box_size_lat,
        )
        x_start = max(0, int(x_min))
        x_end = min(color_matrix.shape[1], int(x_max) + 1)
        x_range = range(x_start, x_end, step)
        y_start = max(0, int(y_min))
        y_end = min(color_matrix.shape[0], int(y_max) + 1)
        y_range = range(y_start, y_end, step)
        info_list = []
        for x in tqdm(x_range, desc="Processing image"):
            for y in y_range:
                info = MapDecoderGeoMixin.get_info(
                    x=x,
                    y=y,
                    c=color_matrix[y, x],
                    color_background=color_background,
                    params=params,
                    color_to_label=color_to_label,
                    map_ent_type=map_ent_type,
                )
                if info is not None:
                    info_list.append(info)
        return info_list
