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
    return {'ADDRESSBLO': {950: '612', 1064: '613', 8527: '611'},
 'ADDRESSBUI': {950: 'HDB-CLEMENTI',
                1064: 'HDB-CLEMENTI',
                8527: 'HDB-CLEMENTI'},
 'ADDRESSFLO': {950: None, 1064: None, 8527: None},
 'ADDRESSPOS': {950: '120612', 1064: '120613', 8527: '120611'},
 'ADDRESSSTR': {950: 'CLEMENTI WEST STREET 1',
                1064: 'CLEMENTI WEST STREET 1',
                8527: 'CLEMENTI WEST STREET 1'},
 'ADDRESSTYP': {950: 'H', 1064: 'H', 8527: 'H'},
 'ADDRESSUNI': {950: None, 1064: None, 8527: None},
 'DESCRIPTIO': {950: 'To deposit recyclables such as paper (e.g. carton boxes, '
                     'newspaper, magazine), plastics (e.g. plastic bottle, '
                     'container), glass (e.g. beverage glass bottle) and '
                     'metals (e.g. drink cans, metal containe',
                1064: 'To deposit recyclables such as paper (e.g. carton '
                      'boxes, newspaper, magazine), plastics (e.g. plastic '
                      'bottle, container), glass (e.g. beverage glass bottle) '
                      'and metals (e.g. drink cans, metal containe',
                8527: 'To deposit recyclables such as paper (e.g. carton '
                      'boxes, newspaper, magazine), plastics (e.g. plastic '
                      'bottle, container), glass (e.g. beverage glass bottle) '
                      'and metals (e.g. drink cans, metal containe'},
 'FMEL_UPD_D': {950: '2017-06-02', 1064: '2017-06-02', 8527: '2017-06-02'},
 'HYPERLINK': {950: 'www.nea.gov.sg/3R',
               1064: 'www.nea.gov.sg/3R',
               8527: 'www.nea.gov.sg/3R'},
 'INC_CRC': {950: '40E295711C1F445D',
             1064: '291823D850345700',
             8527: '6E46FA7DF2E5D94A'},
 'LANDXADDRE': {950: 0.0, 1064: 0.0, 8527: 0.0},
 'LANDYADDRE': {950: 0.0, 1064: 0.0, 8527: 0.0},
 'NAME': {950: 'Recycling Bins in HDB Estates',
          1064: 'Recycling Bins in HDB Estates',
          8527: 'Recycling Bins in HDB Estates'},
 'OBJECTID': {950: 951, 1064: 1030, 8527: 8528},
 'PHOTOURL': {950: None, 1064: None, 8527: None},
 'X_ADDR': {950: 20801.1242, 1064: 20712.6308, 8527: 20895.0031},
 'Y_ADDR': {950: 31753.6268, 1064: 31786.2804, 8527: 31781.8432},
 'distance': {950: 1082.6678761074893,
              1064: 1157.8250523596478,
              8527: 1062.610322222315},
 'geometry': {950: 0x14f42efb0,
              1064: 0x14f491b40,
              8527: 0x152a8d4e0}}