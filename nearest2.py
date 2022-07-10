# import geopandas as gpd
# from SVY21 import SVY21
# from shapely.geometry.point import Point
# from pprint import pprint

# cv = SVY21()
# RECYCLINGBINS = gpd.read_file('datasets/recycling-bins-shp/RECYCLINGBINS.shp')

# # SOC = 103.77365634235952, 1.295056594145143
# def nearest(longitude, latitude, topNum=3):
#     N, E = cv.computeSVY21(latitude, longitude)
#     origin = Point(E, N)
#     RECYCLINGBINS['distance'] = RECYCLINGBINS['geometry'].distance(origin)
#     topFew = RECYCLINGBINS.sort_values(by=['distance']).head(topNum)
#     return topFew.to_dict()

def nearest(longitude, latitude, topNum=3): 
    return [(1.0626096996625594,
  {'ADDRESSBLO': '611',
   'ADDRESSBUI': 'HDB-CLEMENTI',
   'ADDRESSPOS': '120611',
   'ADDRESSSTR': 'CLEMENTI WEST STREET 1',
   'LATITUDE': '1.3036967344862374',
   'LONGITUDE': '103.76947657084446',
   'OBJECTID': '8528'}),
 (1.082667232806678,
  {'ADDRESSBLO': '612',
   'ADDRESSBUI': 'HDB-CLEMENTI',
   'ADDRESSPOS': '120612',
   'ADDRESSSTR': 'CLEMENTI WEST STREET 1',
   'LATITUDE': '1.3034415337965612',
   'LONGITUDE': '103.76863303248963',
   'OBJECTID': '951'}),
 (1.1578243554067367,
  {'ADDRESSBLO': '350',
   'ADDRESSBUI': 'KAMPONG UBI VIEW',
   'ADDRESSPOS': '400350',
   'ADDRESSSTR': 'UBI AVENUE 1',
   'LATITUDE': '1.325803428654137',
   'LONGITUDE': '103.90129203909851',
   'OBJECTID': '995'})]