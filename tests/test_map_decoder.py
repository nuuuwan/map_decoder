import os
import unittest

from gig import EntType
from utils import JSONFile

from map_decoder import MapDecoder

TEST_MAP_DECODER = MapDecoder.open(
    os.path.join("images", "lk-elephant-corridors.png")
)


class TestCase(unittest.TestCase):
    def test_color_matrix(self):
        md = TEST_MAP_DECODER
        cm = md.get_color_matrix(
            md.pil_image,
            n_clusters=3,
            min_saturation=0.1,
            color_background=(255, 255, 255),
        )
        self.assertEqual(cm.shape, (654, 455, 3))
        first_item = tuple((cm[0, 0] * 255).astype(int))
        self.assertEqual(first_item, (255, 255, 255))

    def test_decode(self):
        md = TEST_MAP_DECODER
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
        ]
        valid_color_list = None
        info_list, image_inspection, image_info_list, most_common_colors = (
            md.decode(
                reference_list=reference_list,
                valid_color_list=valid_color_list,
                min_saturation=0.1,
                n_clusters=3,
                color_reference_point=(255, 0, 0),
                color_map_boundaries=(0, 0, 0),
                color_background=(255, 255, 255),
                box_size_lat=0.1,
                map_ent_type=EntType.DSD,
                title="Elephant Corridors in Sri Lanka",
            )
        )

        JSONFile(
            os.path.join("tests", "output", "test_decode_info_list.json")
        ).write(info_list)

        image_inspection.save(
            os.path.join("tests", "output", "test_decode_inspection.png")
        )
        image_info_list.save(
            os.path.join("tests", "output", "test_decode_info_list.png")
        )

        self.assertEqual(len(info_list), 139)
        first_info = info_list[0]
        print(first_info)
        self.assertEqual(
            first_info,
            {
                "latlng": (8.550446, 79.943227),
                "xy": (112, 224),
                "color": (20, 167, 85),
                "ent_id": "LK-6206",
            },
        )
        print(most_common_colors)
        self.assertEqual(
            most_common_colors,
            {(81, 174, 200): 0.5108, (20, 167, 85): 0.4892},
        )
