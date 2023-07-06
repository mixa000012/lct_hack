from datetime import datetime
from random import randint


async def get_date():
    date = datetime.now()
    return date


async def get_id():
    return randint(100000000, 900000000)
