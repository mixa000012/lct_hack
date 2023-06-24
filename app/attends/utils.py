from datetime import datetime
from random import randint


async def get_date():
    return datetime.now()


async def get_id():
    return randint(100000000, 900000000)
