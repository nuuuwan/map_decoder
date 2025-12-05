import os
import unittest

from gig import EntType
from utils import JSONFile

from map_decoder import MapDecoder

image_path = os.path.join("images", "lk-elephant-corridors.png")
md = MapDecoder.open(image_path)

dir_self = os.path.join("examples", "example_1_elephant_corridors")


reference_list = [
    {
        "label": "Point Pedro",
        "xy": (154, 37),
        "latlng": (9.835389314753982, 80.2121458415902),
    },
    {
        "label": "Dondra Head",
        "xy": (208, 607),
        "latlng": (5.918717418993297, 80.5912354116987),
    },
    {
        "label": "Kandakuliya",
        "xy": (76, 269),
        "latlng": (8.210296842304663, 79.69258966975879),
    },
    {
        "label": "Sangaman Kanda",
        "xy": (390, 442),
        "latlng": (7.022706066775057, 81.8787010500323),
    },
    {
        "label": "Colombo",
        "xy": (96, 458),
        "latlng": (6.942870277422712, 79.83995049428376),
    },
    {
        "label": "Negombo",
        "xy": (98, 417),
        "latlng": (7.20648075894579, 79.84092635802587),
    },
]

info_list, image_inspection, image_info_list, most_common_colors = md.decode(
    reference_list=reference_list,
    min_saturation=0.1,
    n_clusters=3,
    color_reference_point=(255, 0, 0),
    color_map_boundaries=(0, 0, 0),
    color_background=(255, 255, 255),
    box_size_lat=0.1,
    map_ent_type=EntType.DSD,
    title="Elephant Corridors in Sri Lanka",
    color_to_label={
        (81, 174, 200): "Temporary Corridors",
        (20, 167, 85): "Permanent Corridors and Parks",
    },
)

JSONFile(os.path.join(dir_self, "info_list.json")).write(info_list)
image_inspection.save(os.path.join(dir_self, "inspection.png"))
image_info_list.save(os.path.join(dir_self, "info_list.png"))
print(most_common_colors)

first_info = info_list[0]
print(first_info)
