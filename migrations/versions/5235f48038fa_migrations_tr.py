""" migrations_tr

Revision ID: 5235f48038fa
Revises: f9a30bb31a7d
Create Date: 2023-05-26 14:38:48.290091

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "5235f48038fa"
down_revision = "f9a30bb31a7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_groups_id", table_name="groups")
    op.drop_table("groups")
    op.alter_column(
        "uniquegroups",
        "id",
        existing_type=sa.INTEGER(),
        nullable=False,
        autoincrement=True,
    )
    op.create_index(op.f("ix_uniquegroups_id"), "uniquegroups", ["id"], unique=False)
    op.drop_column("uniquegroups", "направление 3")
    op.drop_column("uniquegroups", "адрес площадки")
    op.drop_column("uniquegroups", "район площадки")
    op.drop_column("uniquegroups", "округ площадки")
    op.drop_column("uniquegroups", "расписание в плановом периоде")
    op.drop_column("uniquegroups", "направление 1")
    op.drop_column("uniquegroups", "уникальный номер")
    op.drop_column("uniquegroups", "расписание в активных периодах")
    op.drop_column("uniquegroups", "расписание в закрытых периодах")
    op.drop_column("uniquegroups", "направление 2")
    op.add_column("users", sa.Column("uuid", sa.UUID(), nullable=False))
    op.drop_column("users", "id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False)
    )
    op.drop_column("users", "uuid")
    op.add_column(
        "uniquegroups",
        sa.Column(
            "направление 2", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "расписание в закрытых периодах",
            sa.VARCHAR(length=2048),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "расписание в активных периодах",
            sa.VARCHAR(length=64),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column("уникальный номер", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "направление 1", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "расписание в плановом периоде",
            sa.VARCHAR(length=64),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "округ площадки", sa.VARCHAR(length=256), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "район площадки", sa.VARCHAR(length=256), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "адрес площадки", sa.VARCHAR(length=512), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "uniquegroups",
        sa.Column(
            "направление 3", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
    )
    op.drop_index(op.f("ix_uniquegroups_id"), table_name="uniquegroups")
    op.alter_column(
        "uniquegroups",
        "id",
        existing_type=sa.INTEGER(),
        nullable=True,
        autoincrement=True,
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("direction_1", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("direction_2", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("direction_3", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("address", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("okrug", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("district", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("schedule_active", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("schedule_closed", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("schedule_planned", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("closest_smetro", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("уникальный номер", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "направление 1", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
        sa.Column(
            "направление 2", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
        sa.Column(
            "направление 3", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
        sa.Column(
            "адрес площадки", sa.VARCHAR(length=512), autoincrement=False, nullable=True
        ),
        sa.Column(
            "округ площадки", sa.VARCHAR(length=256), autoincrement=False, nullable=True
        ),
        sa.Column(
            "район площадки", sa.VARCHAR(length=256), autoincrement=False, nullable=True
        ),
        sa.Column(
            "расписание в активных периодах",
            sa.VARCHAR(length=64),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "расписание в закрытых периодах",
            sa.VARCHAR(length=2048),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "расписание в плановом периоде",
            sa.VARCHAR(length=64),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name="groups_pkey"),
    )
    op.create_index("ix_groups_id", "groups", ["id"], unique=False)
    # ### end Alembic commands ###
