from fastapi import APIRouter

from app.api.v1.endpoints import user, routes, groups, recs, attends

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(routes.routes_router, prefix='/routes', tags=['routes'])
api_router.include_router(groups.groups_router, prefix='/groups', tags=['groups'])
api_router.include_router(recs.recs_router, prefix='/recs', tags=['recs'])
api_router.include_router(attends.attends_router, prefix='/attends', tags=['attends'])
