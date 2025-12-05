import os
import unittest

from map_decoder import MapDecoder

TEST_MAP_DECODER = MapDecoder.open(
    os.path.join("images", "lk-elephant-corridors.png")
)


class TestCase(unittest.TestCase):
    def test_color_matrix(self):
        md = TEST_MAP_DECODER
        cm = md.color_matrix
        self.assertEqual(cm.shape, (654, 455, 3))

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
            md.decode(reference_list, valid_color_list)
        )

        image_inspection.save(
            os.path.join("tests", "output", "test_decode_inspection.png")
        )
        image_info_list.save(
            os.path.join("tests", "output", "test_decode_info_list.png")
        )

        self.assertEqual(len(info_list), 654 * 455)
        first_info = info_list[0]
        print(first_info)
        self.assertEqual(
            first_info,
            {
                "latlng": (10.089629, 79.163467),
                "xy": (0, 0),
                "color": (65, 65, 65),
            },
        )
        print(most_common_colors)
        self.assertEqual(
            most_common_colors,
            {
                (255, 255, 255): 87771,
                (253, 253, 253): 24142,
                (251, 251, 251): 10028,
                (254, 254, 254): 9336,
                (250, 250, 250): 7239,
            },
        )
