import asyncio
import json
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Groups
from db.session import engine
from geocoding.get_coords import find_closest_metro_async


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


async def find_closest_metros(data, metro_name):
    # Find the specified metro
    metro = next((item for item in data if item["name"] == metro_name), None)
    if not metro:
        raise ValueError(f"Metro station {metro_name} not found.")

    # Calculate the distances to all other metro stations
    distances = []
    for item in data:
        if item != metro:
            dist = calculate_distance(
                float(metro["latitude"]),
                float(metro["longtitute"]),
                float(item["latitude"]),
                float(item["longtitute"]),
            )
            distances.append((item["name"], dist))

    # Sort the distances in ascending order and take the first 3
    closest_metros = sorted(distances, key=lambda x: x[1])[:5]
    closest_metros = [i[0] for i in closest_metros]
    return ", ".join(closest_metros)


# Your data
with open("file.json", "r", encoding="utf-8") as f:
    data = json.load(f)


async def fetch_all_groups():
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(select(Groups))
            groups = result.scalars().all()

            tasks = []
            for group in groups:
                if (
                    group.closest_metro == "Онлайн"
                    or group.closest_metro == "далековато"
                ):
                    continue

                # Create a task for the function and append it to the tasks list
                task = asyncio.create_task(
                    find_closest_metros(data, group.closest_metro)
                )
                tasks.append((group, task))

            # Run the tasks concurrently
            for group, task in tasks:
                closest_metro = await task
                group.around_metros = closest_metro

            await session.commit()


asyncio.run(fetch_all_groups())
