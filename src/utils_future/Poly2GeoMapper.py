import numpy as np
from utils import Log

log = Log("Poly2GeoMapper")


class Poly2GeoMapper:

    @staticmethod
    def fit(xys: list[tuple[int, int]], latlngs: list[tuple[float, float]]):
        assert len(xys) == len(
            latlngs
        ), "Length of xys and latlngs must be equal"
        xys = np.asarray(xys)
        xs = xys[:, 0]
        ys = xys[:, 1]
        lats = np.asarray([latlng[0] for latlng in latlngs])
        lngs = np.asarray([latlng[1] for latlng in latlngs])

        A = np.column_stack([xs**2, ys**2, xs * ys, xs, ys, np.ones_like(xs)])

        lat_params, *_ = np.linalg.lstsq(A, lats, rcond=None)
        lng_params, *_ = np.linalg.lstsq(A, lngs, rcond=None)

        params = [lat_params, lng_params]
        return params

    @staticmethod
    def transform(xy: tuple, params: list[np.ndarray]):
        lat_params, lng_params = params
        x, y = xy
        x = np.asarray(x)
        y = np.asarray(y)

        # Ensure A has shape (N, 6)
        A = np.column_stack([x**2, y**2, x * y, x, y, np.ones_like(x)])

        lat = A.dot(lat_params)
        lng = A.dot(lng_params)

        # Return scalars if input was scalar
        if lat.size == 1:
            return float(lat), float(lng)
        return (lat, lng)
