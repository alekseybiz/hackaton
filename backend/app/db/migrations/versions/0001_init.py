from alembic import op
import sqlalchemy as sa
from geoalchemy2.types import Geometry


revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table(
        'region',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('okato', sa.String(length=20), nullable=True),
        sa.Column('polygon', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False),
    )
    op.create_index('ix_region_name', 'region', ['name'])
    op.create_index('ix_region_okato', 'region', ['okato'])


def downgrade() -> None:
    op.drop_index('ix_region_okato', table_name='region')
    op.drop_index('ix_region_name', table_name='region')
    op.drop_table('region')


