import unittest

from utils_future import Poly2GeoMapper

TEST_REFERENCE_LIST = [
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


class TestCase(unittest.TestCase):
    def test_fit_and_transform(self):

        xys = [ref["xy"] for ref in TEST_REFERENCE_LIST]
        latlngs = [ref["latlng"] for ref in TEST_REFERENCE_LIST]

        params = Poly2GeoMapper.fit(xys=xys, latlngs=latlngs)
        for ref in TEST_REFERENCE_LIST:
            xy = ref["xy"]
            expected_latlng = ref["latlng"]
            predicted_latlng = Poly2GeoMapper.transform(xy, params)
            self.assertAlmostEqual(
                expected_latlng[0], predicted_latlng[0], places=10
            )
            self.assertAlmostEqual(
                expected_latlng[1], predicted_latlng[1], places=10
            )
