"""File with settings and configs for the project"""
from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://misha:123@api.lapki.itatmisis.ru:5432/postgres",
)  # connect string for the real database

ACCESS_TOKEN_EXPIRE: int = env.int("ACCESS_TOKEN_EXPIRE", default=30)

SECRET_KEY: str = env.str("SECTET_KEY", default="secret_key")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")
