""" migrations_tr

Revision ID: 1412f6b00950
Revises: 860804179da1
Create Date: 2023-05-28 23:52:42.240931

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "1412f6b00950"
down_revision = "860804179da1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("attends", sa.Column("metro", sa.String(), nullable=True))
    op.add_column("attends", sa.Column("address", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("attends", "address")
    op.drop_column("attends", "metro")
    # ### end Alembic commands ###
