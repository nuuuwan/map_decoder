import os
import unittest

from map_decoder import Image


class TestCase(unittest.TestCase):
    def test_color_matrix(self):
        test_image = Image(
            os.path.join("images", "lk-elephant-corridors.png")
        )
        color_matrix = test_image.color_matrix
        self.assertEqual(color_matrix.shape, (654, 455, 3))
