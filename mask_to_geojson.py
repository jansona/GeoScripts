import cv2
import math
import json
import solaris
import os


# 得到掩膜图矢量化后的json形式
def get_footprint_geoms_json(filepath):

    mask_image = cv2.imread(filepath)
    geoms = solaris.vector.mask.mask_to_poly_geojson(mask_image[:, :, 0])
    return json.loads(geoms.to_json())


# 将geojson中的行列号映射到经纬度
def affine_coord(geoms_json, x_origin, y_origin, zoom, width=256, height=256):

    feature_arr = geoms_json["features"]
    for feature_obj in feature_arr:
        geometry_obj = feature_obj["geometry"]
        coord_arr_arr = geometry_obj["coordinates"]
        for coord_arr in coord_arr_arr:
            coord_arr[:] = list(map(lambda coord: num2deg(x_origin + coord[0] / width, 
            y_origin + coord[1] / height, zoom), coord_arr))

    return geoms_json


# OpenStreetMap经纬度转行列号
def deg2num(lon_deg, lat_deg, zoom):

    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


# OpenStreetMap行列号转经纬度
def num2deg(xtile, ytile, zoom):

    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)


if __name__ == '__main__':

    file_path = "/data01/ml_space_ybg/solaris_test/8391_12194_15.png"
    file_name = os.path.basename(file_path)
    dir_path = os.path.dirname(file_path)
    print(file_name)
    x, y, z = file_name.split(".")[0].split("_")
    x = int(x)
    y = int(y)
    z = int(z)

    image = cv2.imread(file_path)
    w, h, _ = image.shape

    geoms_json = get_footprint_geoms_json(file_path)
    new_geoms_json = affine_coord(geoms_json, x, y, z, w, h)

    with open(os.path.join(dir_path, file_name.split(".")[0] + ".json"), "w") as fout:
        fout.write(json.dumps(geoms_json))
