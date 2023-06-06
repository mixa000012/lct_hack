import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.endpoints import recs_router
from api.endpoints import routes_router, groups_router
from api.user import user_router
from starlette.middleware.cors import CORSMiddleware


app = FastAPI(title="lct_hack")

main_api_router = APIRouter()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_api_router.include_router(user_router, prefix="/api/v1/user", tags=["user"])
main_api_router.include_router(routes_router, prefix="/api/v1/routes", tags=["routes"])
main_api_router.include_router(recs_router, prefix="/api/v1/recs", tags=["recs"])
main_api_router.include_router(groups_router, prefix="/api/v1/groups", tags=["groups"])

app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="10.0.0.51", port=8080,
                ssl_keyfile="/etc/letsencrypt/live/api.lapki.itatmisis.ru/privkey.pem",
                ssl_certfile="/etc/letsencrypt/live/api.lapki.itatmisis.ru/fullchain.pem")
