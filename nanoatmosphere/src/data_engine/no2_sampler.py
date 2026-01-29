import rasterio

FILES = {
    "Recent": "data/NO2_Chennai_1.tif",
    "Last Week": "data/NO2_Chennai_2.tif",
    "Last Month": "data/NO2_Chennai_3.tif",
}

_srcs = {name: rasterio.open(path) for name, path in FILES.items()}

def get_no2_at_latlon(lat, lon, layer="Recent"):
    src = _srcs[layer]
    for arr in src.sample([(lon, lat)]):
        return float(arr[0])

