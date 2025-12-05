import unittest

from utils_future import Poly2GeoMapper


class TestCase(unittest.TestCase):
    def test_method(self):
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
        xys = [ref["xy"] for ref in reference_list]
        latlngs = [ref["latlng"] for ref in reference_list]

        lat_params, lng_params = Poly2GeoMapper.fit(xys=xys, latlngs=latlngs)

        for ref in reference_list:
            xy = ref["xy"]
            expected_latlng = ref["latlng"]
            predicted_latlng = Poly2GeoMapper.transform(
                xy, lat_params, lng_params
            )
            print(expected_latlng)
            print(predicted_latlng)
            self.assertAlmostEqual(
                expected_latlng[0], predicted_latlng[0], places=10
            )
            self.assertAlmostEqual(
                expected_latlng[1], predicted_latlng[1], places=10
            )
