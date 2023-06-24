from db.models import Groups
from db.session import engine
from sqlalchemy import text
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_metros_for_addresses():
    async with AsyncSession(engine) as session:
        # Use raw SQL to perform the JOIN operation
        query = text(
            """
            SELECT groups.address, uniquegroups.closest_smetro, uniquegroups.coordinates_of_address
            FROM "groups"
            LEFT JOIN uniquegroups ON groups.address = uniquegroups.address
        """
        )
        result = await session.execute(query)
        return result.fetchall()


async def update_metros_for_addresses():
    async with AsyncSession(engine) as session:
        # Get the addresses and their closest metros
        addresses_metros = await get_metros_for_addresses()

        # Update the closest_metro column in db2.table2 for each address
        for address, closest_metro, coordinates_of_address in addresses_metros:
            stmt = (
                update(Groups)
                .where(Groups.address == address)
                .values(
                    closest_metro=closest_metro,
                    coordinates_of_address=coordinates_of_address,
                )
            )
            await session.execute(stmt)

        await session.commit()
