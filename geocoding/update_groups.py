import asyncio
import re
import urllib.parse

import aiohttp
from db.models import Groups
from db.session import engine
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from geocoding.get_coords import find_closest_metro_async

api_key = "5b3ce3597851110001cf6248d4e646702ef148e5a55e272b239c23cb"

sem = asyncio.Semaphore(1)  # Adjust to desired concurrency level


async def get_coordinates_async(address):
    address = str(address).lower()
    address = address.replace("город", "")
    url = f"https://api.openrouteservice.org/geocode/search?api_key={api_key}&text={urllib.parse.quote(address)}&boundary.country=RUS"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp_json_payload = await resp.json()

            if resp.status != 200:
                print((f"API request failed with status {resp.status}:{resp.text}"))
                await asyncio.sleep(5)
                async with session.get(url) as resp:
                    resp_json_payload = await resp.json()
            if len(resp_json_payload["features"]) == 0:
                print(("No results found for the given address."))
                return 71.985533, 115.205860

            lng, lat = resp_json_payload["features"][0]["geometry"]["coordinates"]

            return lat, lng


async def update_group(group):
    async with sem:  # This will block if too many tasks are running
        async with AsyncSession(engine) as session:
            print(group.address)
            addresses = re.split(r"(?:г\. Москва|город Москва)", group.address)
            addresses = [
                "Москва " + address.strip(", ")
                for address in addresses
                if address.strip(", ")
            ]
            print(addresses[0])
            lat, lon = await get_coordinates_async(addresses[0])
            print(f"coord: {lat},{lon}")
            closest_metro = find_closest_metro_async(lat, lon)
            print(closest_metro)

            # Assign the closest metro station name to the group's closest_metro field
            group.closest_metro = closest_metro["name"]
            group.coordinates_of_address = f"{lat},{lon}"
            session.add(group)
            await session.commit()


async def fetch_all_groups():
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Groups).where(Groups.closest_metro == None)  # noqa
        )
        groups = result.scalars().all()
        print(groups)
        return groups


async def main():
    # Fetch all groups
    groups = await fetch_all_groups()

    # Create a coroutine for each group
    coroutines = [update_group(group) for group in groups]

    # Run the coroutines concurrently
    await asyncio.gather(*coroutines)
