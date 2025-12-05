from utils import Log

log = Log("MapDecoder")


class MapDecoderEntMixin:
    @staticmethod
    def get_ent_to_label_to_n(info_list):
        idx = {}
        for info in info_list:
            ent_id = info["ent_id"]
            label = info["label"]

            if ent_id not in idx:
                idx[ent_id] = {}
            if label not in idx[ent_id]:
                idx[ent_id][label] = 0

            idx[ent_id][label] += 1

        return idx
