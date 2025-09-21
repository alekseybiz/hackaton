from alembic import op
import sqlalchemy as sa


revision = '0002_stats'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'daily_region_stats',
        sa.Column('date', sa.Date(), primary_key=True, nullable=False),
        sa.Column('region_id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('flights_cnt', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_duration_sec', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_duration_sec', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_daily_region_stats_region_id', 'daily_region_stats', ['region_id'])

    op.create_table(
        'hourly_region_stats',
        sa.Column('hour_ts', sa.DateTime(timezone=True), primary_key=True, nullable=False),
        sa.Column('region_id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('flights_cnt', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_hourly_region_stats_region_id', 'hourly_region_stats', ['region_id'])


def downgrade() -> None:
    op.drop_index('ix_hourly_region_stats_region_id', table_name='hourly_region_stats')
    op.drop_table('hourly_region_stats')
    op.drop_index('ix_daily_region_stats_region_id', table_name='daily_region_stats')
    op.drop_table('daily_region_stats')


