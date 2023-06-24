import ast
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt
from typing import Tuple

import openrouteservice
from openrouteservice.geocode import pelias_search

from app.groups.schema import Group
from app.groups.schema import GroupInDB

client = openrouteservice.Client(
    key="5b3ce3597851110001cf6248d849a8330bbd463fb95a896f83abd13f"
)  # Specify your personal API key


async def calculate_distance(lat1, lon1, lat2, lon2):
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


async def calculate_time_to_walk(coordinate_place, coordinates_user):
    coordinates = ast.literal_eval(coordinate_place)
    coord = (coordinates_user, coordinates)
    try:
        dist = await calculate_distance(
            coord[0][0], coord[0][1], coord[1][0], coord[1][1]
        )
        # print(coord[0][0], coord[0][1], coord[1][0], coord[1][1])
        # print('fsdfdsfsdfsdfsdfsd')
        # print(dist)
    except:  # noqa
        return 500
    # time = routes.get("durations")[0][1]
    if dist:
        return int((dist / 3) * 60)
    else:
        return 1000


async def get_coordinates(address: str) -> Tuple[float, float]:
    if "Moscow, MS, Russia" not in address:
        address += ", Moscow, MS, Russia"
    routes = pelias_search(client, address, country="RUS")
    final_coords = routes.get("features")[0].get("geometry").get("coordinates")[::-1]
    return final_coords[0], final_coords[1]


async def create_group_in_db(group) -> GroupInDB:
    time = (
        group.schedule_active
        if len(group.schedule_active) > 0
        else group.schedule_closed
    )
    return GroupInDB(
        id=group.id,
        name=group.direction_3,
        type=group.direction_1,
        address=group.address,
        metro=group.closest_metro,
        time=time,
        description=group.description,
    )


async def create_group_with_time_to_walk(
    group_in_db: GroupInDB, coordinates_of_address, coordinates_user, closest_metro
) -> Group:
    if closest_metro == "Онлайн":
        time_to_walk = 0
    else:
        time_to_walk = await calculate_time_to_walk(
            coordinates_of_address, coordinates_user
        )

    group = Group(**group_in_db.dict(), timeToWalk=time_to_walk)
    return group
