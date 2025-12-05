from gig import Ent, EntType
from shapely.geometry import Point


class EntFuture(Ent):

    @classmethod
    def from_latlng(
        cls,
        latlng: tuple[float, float],
        region_ent_type: EntType = EntType.PROVINCE,
        parent_ent_id: str = "LK",
    ) -> str:
        ents = Ent.list_from_type(region_ent_type)
        candidate_ents = [ent for ent in ents if parent_ent_id in ent.id]
        lat, lng = latlng
        point = Point(lng, lat)
        for ent in candidate_ents:
            geo = ent.geo()
            if geo.geometry.contains(point).any():
                return ent

        return None

    @classmethod
    def list_regions_from_latlng(cls, latlng: tuple[float, float]) -> dict:
        region_hierarchy = {}
        parent_ent_id = "LK"
        for ent_type in [
            EntType.PROVINCE,
            EntType.DISTRICT,
            EntType.DSD,
            EntType.GND,
        ]:
            ent = cls.from_latlng(latlng, ent_type, parent_ent_id)
            if ent is None:
                return region_hierarchy
            region_hierarchy[ent_type.name] = ent
            parent_ent_id = ent.id

        return region_hierarchy
