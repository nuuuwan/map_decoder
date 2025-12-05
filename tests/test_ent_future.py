import unittest

from gig import EntType

from gig_future import EntFuture


class TestCase(unittest.TestCase):
    def test_from_latlng(self):

        for latlng, expected_ent_id in [
            [
                (
                    6.915706285411007,
                    79.86352777692407,
                ),  # Town Hall, Colombo,
                "LK-1",  # Western Province
            ],
            [
                (4.1748, 73.50888),  # Male, Maldives
                None,
            ],
        ]:
            observed_ent = EntFuture.from_latlng(
                latlng=latlng,
                region_ent_type=EntType.PROVINCE,
            )
            if expected_ent_id is None:
                self.assertIsNone(observed_ent)
            else:
                self.assertEqual(observed_ent.id, expected_ent_id)

    def test_list_regions_from_latlng(self):
        region_hierarchy = EntFuture.idx_regions_from_latlng(
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
        # self.assertEqual(
        #     region_hierarchy[EntType.DSD.name].name,
        #     "Thimbirigasyaya",
        # )
        # self.assertEqual(
        #     region_hierarchy[EntType.GND.name].name,
        #     "Kurunduwatta",
        # )
