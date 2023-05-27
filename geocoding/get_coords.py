import json
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

import openrouteservice
from openrouteservice.geocode import pelias_search

coords = ((8.34234, 48.23424), (8.34423, 48.26424))
client = openrouteservice.Client(
    key="5b3ce3597851110001cf6248d4e646702ef148e5a55e272b239c23cb"
)  # Specify your personal API key

with open("../file.json", "r", encoding="utf-8") as f:
    metro_data = json.load(f)
# Convert data to the correct format and convert coordinates to floats
for station in metro_data:
    station["latitude"] = float(station["latitude"])
    station["longtitute"] = float(station["longtitute"])


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # radius of Earth in km

    lat1_radians = radians(lat1)
    lon1_radians = radians(lon1)
    lat2_radians = radians(lat2)
    lon2_radians = radians(lon2)

    dlon = lon2_radians - lon1_radians
    dlat = lat2_radians - lat1_radians

    a = sin(dlat / 2) ** 2 + cos(lat1_radians) * cos(lat2_radians) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def find_closest_metro_async(lat, lon):
    closest_metro = None
    closest_distance = None

    for metro in metro_data:
        metro_lat, metro_lon = metro["latitude"], metro["longtitute"]
        distance = calculate_distance(lat, lon, metro_lat, metro_lon)

        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_metro = metro
    if int(closest_distance) > 500:
        closest_metro["name"] = "далековато"
        return closest_metro
    return closest_metro


text = "Москва, улица Крупской, дом 1, корпус 1"
routes = pelias_search(client, text, country="RUS")
print(routes)
final_coords = routes.get("features")[0].get("geometry").get("coordinates")[::-1]
print(final_coords[0], final_coords[1])

closest_metro = find_closest_metro_async(final_coords[0], final_coords[1])
print(
    f"The closest metro station is {closest_metro['name']} at a distance of {calculate_distance(final_coords[0], final_coords[1], closest_metro['latitude'], closest_metro['longtitute'])} km."
)
