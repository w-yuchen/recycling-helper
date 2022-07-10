import csv
from geopy.distance import distance

with open('datasets/recycling-bins/recycling_bins.csv', 'r') as rr:
    RECYCLING_BINS = list(csv.DictReader(rr))

with open('datasets/2nd-hand-goods-collection-points/secondhand.csv', 'r') as ss:
    SECONDHAND = list(csv.DictReader(ss))

# SOC
# latitude, longitude = 1.295056594145143, 103.77365634235952
def nearest_bin(latitude, longitude, topNum=3):
    distances = [
        (
            distance((latitude, longitude), (x['LATITUDE'], x['LONGITUDE'])).km,
            int(x['OBJECTID']) - 1
        )
        for x in RECYCLING_BINS
    ]
    distances.sort(key=lambda x: x[0])
    topFew = []
    for i in range(topNum):
        kilometers, bin_index = distances[i]
        topFew.append((kilometers, RECYCLING_BINS[bin_index]))
    return topFew

# there are only 21
def nearest_secondhand(latitude, longitude, topNum=2):
    distances = list(enumerate([
        distance((latitude, longitude), (x['LATITUDE'], x['LONGITUDE'])).km
        for x in SECONDHAND
    ]))
    distances.sort(key=lambda x: x[1])
    topFew = []
    for i in range(topNum):
        index, kilometers = distances[i]
        topFew.append((kilometers, SECONDHAND[index]))
    return topFew