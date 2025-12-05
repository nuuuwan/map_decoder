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
                "xy": (154, 38),
                "latlng": (9.835389314753982, 80.2121458415902),
            },
            {
                "label": "Point Dondra",
                "xy": (208, 607),
                "latlng": (5.918717418993297, 80.5912354116987),
            },
        ]
        decoded_image = md.decode(reference_list)
        decoded_image.save(
            os.path.join(
                "tests", "output", "lk-elephant-corridors-decoded.png"
            )
        )
