import os
import unittest

from map_decoder import MapDecoder


class TestCase(unittest.TestCase):
    def test_color_matrix(self):
        md = MapDecoder.open(
            os.path.join("images", "lk-elephant-corridors.png")
        )
        cm = md.color_matrix
        self.assertEqual(cm.shape, (654, 455, 3))
