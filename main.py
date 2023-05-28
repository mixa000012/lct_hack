import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.endpoints import recs_router
from api.endpoints import routes_router
from api.user import user_router

app = FastAPI(title="lct_hack")

main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(routes_router, prefix="/api/v1/routes", tags=["routes"])
main_api_router.include_router(recs_router, prefix="/recs", tags=["recs"])

app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="10.0.0.51", port=8080)
