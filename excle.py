import asyncpg
import pandas as pd
import asyncio

DATABASE = {
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': '127.0.0.1',
    'port': '5433',
}

async def run():
    conn = await asyncpg.connect(**DATABASE)
    df = pd.read_csv('groups.csv')
    df = df.where(pd.notnull(df), None)
    for index, row in df.iterrows():
        await conn.execute('''
            INSERT INTO groups(id, direction_1, direction_2, direction_3, address, okrug, district, schedule_active, schedule_closed, schedule_planned) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', row['уникальный номер'], row['направление 1'], row['направление 2'], row['направление 3'], row['адрес площадки'], str(row['округ площадки']), row['район площадки'], str(row['расписание в активных периодах']), str(row['расписание в закрытых периодах']), str(row['расписание в плановом периоде']))
    await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())