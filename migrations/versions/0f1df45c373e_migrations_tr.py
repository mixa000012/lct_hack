""" migrations_tr

Revision ID: 0f1df45c373e
Revises: 9e81207c2607
Create Date: 2023-05-27 20:20:25.598786

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0f1df45c373e"
down_revision = "9e81207c2607"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("id", sa.Integer(), nullable=False))
    op.drop_column("users", "uuid")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("uuid", sa.UUID(), autoincrement=False, nullable=False)
    )
    op.drop_column("users", "id")
    # ### end Alembic commands ###
