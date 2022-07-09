import geopandas as gpd
from SVY21 import SVY21
from shapely.geometry.point import Point
from pprint import pprint

cv = SVY21()
RECYCLINGBINS = gpd.read_file('datasets/recycling-bins-shp/RECYCLINGBINS.shp')

# SOC = 103.77365634235952, 1.295056594145143
def nearest(longitude, latitude, topNum=3):
    N, E = cv.computeSVY21(latitude, longitude)
    origin = Point(E, N)
    RECYCLINGBINS['distance'] = RECYCLINGBINS['geometry'].distance(origin)
    topFew = RECYCLINGBINS.sort_values(by=['distance']).head(topNum)
    return topFew.to_dict()