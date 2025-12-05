import os
import unittest

from map_decoder import MapDecoder

TEST_MAP_DECODER = MapDecoder.open(
    os.path.join("tests", "inputs", "lk-elephant-corridors.png")
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
