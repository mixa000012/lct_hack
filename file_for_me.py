import time

import openrouteservice
from openrouteservice.geocode import pelias_search
import json
from math import radians, cos, sin, sqrt, atan2
import pandas as pd
from db.session import SessionLocal

coords = ((8.34234, 48.23424), (8.34423, 48.26424))
api_key = '5b3ce3597851110001cf6248c0f128b2bc2948f1bd9de41db8980cd2'
client = openrouteservice.Client(
    key='5b3ce3597851110001cf6248d849a8330bbd463fb95a896f83abd13f')  # Specify your personal API key
text = 'москва 60-летия октября 11'
# routes = pelias_search(client, text, country='RUS', size=2)
# print(routes)
# final_coords = routes.get('features')[0].get('geometry').get('coordinates')[::-1]
# print(final_coords[0], final_coords[1])

with open('file.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convert data to the correct format and convert coordinates to floats
for station in data:
    station['latitude'] = float(station['latitude'])
    station['longtitute'] = float(station['longtitute'])


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


def find_closest_metro(lat, lon, metro_data):
    closest_metro = None
    closest_distance = None

    for metro in metro_data:
        metro_lat, metro_lon = metro['latitude'], metro['longtitute']
        distance = calculate_distance(lat, lon, metro_lat, metro_lon)

        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_metro = metro
    if int(closest_distance) > 500:
        closest_metro['name'] = 'далековато'
        return closest_metro
    return closest_metro


# closest_metro = find_closest_metro(final_coords[0], final_coords[1], data)
# print(
#     f"The closest metro station is {closest_metro['name']} at a distance of {calculate_distance(final_coords[0], final_coords[1], closest_metro['latitude'], closest_metro['longtitute'])} km.")

import aiohttp
import asyncio
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.session import get_db, engine
from db.models import Groups
from sqlalchemy import select, update


async def get_coordinates_async(address):
    url = f'http://94.139.252.94:4000/geocode/search?&text={urllib.parse.quote(address)}'
    # url = f'https://api.openrouteservice.org/geocode/search?api_key={api_key}&text={urllib.parse.quote(address)}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp_json_payload = await resp.json()

            if resp.status != 200:
                raise Exception(f"API request failed with status {resp.status}:{resp.text}")

            if len(resp_json_payload['features']) == 0:
                raise Exception('No results found for the given address.')

            lng, lat = resp_json_payload['features'][0]['geometry']['coordinates']

            return lat, lng

sem = asyncio.Semaphore(1)  # Adjust to desired concurrency level

async def update_group(group):
    try:
        async with sem:  # This will block if too many tasks are running
            async with AsyncSession(engine) as session:
                # Query for an existing group with a closest metro
                stmt = select(Groups).where(Groups.address == group.address, Groups.closest_smetro != None)
                result = await session.execute(stmt)
                existing_group = result.scalar_one_or_none()

                # If such a group was found, there's nothing more to do
                if existing_group is not None:
                    return

                lat, lon = await get_coordinates_async(group.address)
                closest_metro = find_closest_metro(lat, lon, data)

                # Assign the closest metro station name to the group's closest_metro field
                group.closest_smetro = closest_metro['name']

                session.add(group)
                await session.commit()

    except Exception as e:
        time.sleep(10)
        print(f"An error occurred for group with id {group.id}: {str(e)}")


# Fetch all groups
async def fetch_all_groups():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Groups))
        groups = result.scalars().all()
        return groups

async def main():
    # Fetch all groups
    groups = await fetch_all_groups()

    # Create a coroutine for each group
    coroutines = [update_group(group) for group in groups]

    # Run the coroutines concurrently
    await asyncio.gather(*coroutines)

asyncio.run(main())