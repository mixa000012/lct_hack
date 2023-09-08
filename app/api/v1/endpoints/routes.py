from fastapi import APIRouter

from app.routes import service

router = APIRouter()


@router.get("/suggest")
async def suggest(query: str) -> list[str]:
    results = await service.suggest(query)
    return results


@router.get("/address")
async def get_address(coordinates: str) -> dict:
    routes = await service.get_address(coordinates)
    return routes
