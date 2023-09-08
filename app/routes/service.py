import ast

import openrouteservice
from openrouteservice.geocode import pelias_autocomplete
from openrouteservice.geocode import pelias_reverse


client = openrouteservice.Client(
    key="5b3ce3597851110001cf6248d849a8330bbd463fb95a896f83abd13f"
)  # Specify your personal API key


async def suggest(query: str) -> list[str]:
    results = []

    try:
        routes = pelias_autocomplete(client, query, country="RUS", layers=["address"])
        for i in range(10):
            result = routes.get("features")[i].get("properties").get("name")
            results.append(result)
    except Exception:
        return results


async def get_address(coordinates: str) -> dict:
    coordinates = ast.literal_eval(coordinates)
    coordinates = (coordinates[1], coordinates[0])
    routes = pelias_reverse(client, coordinates, country="RUS")
    return routes
