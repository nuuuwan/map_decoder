import unittest

from gig import EntType

from gig_future import EntFuture


class TestCase(unittest.TestCase):
    def test_from_latlng(self):
        ent = EntFuture.from_latlng(
            latlng=(
                6.915706285411007,
                79.86352777692407,
            ),  # Town Hall, Colombo,
            region_ent_type=EntType.DISTRICT,
        )
        self.assertEqual(ent.id, "LK-11")

    def test_list_regions_from_latlng(self):
        region_hierarchy = EntFuture.list_regions_from_latlng(
            latlng=(
                6.915706285411007,
                79.86352777692407,
            ),  # Town Hall, Colombo,
        )
        self.assertEqual(
            region_hierarchy[EntType.PROVINCE.name].name,
            "Western",
        )
        self.assertEqual(
            region_hierarchy[EntType.DISTRICT.name].name,
            "Colombo",
        )
        self.assertEqual(
            region_hierarchy[EntType.DSD.name].name,
            "Thimbirigasyaya",
        )
        self.assertEqual(
            region_hierarchy[EntType.GND.name].name,
            "Kurunduwatta",
        )
