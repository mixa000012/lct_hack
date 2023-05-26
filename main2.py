import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.endpoints import order_router
from api.endpoints import routes_router
from api.endpoints import values_router

app = FastAPI(title="Poizon Bot")

main_api_router = APIRouter()

main_api_router.include_router(order_router, prefix="/order", tags=["order"])
main_api_router.include_router(routes_router, prefix="/api/v1/routes", tags=["routes"])
main_api_router.include_router(values_router, prefix="/values", tags=["values"])

app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
