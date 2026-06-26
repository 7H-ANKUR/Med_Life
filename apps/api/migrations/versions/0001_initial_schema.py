"""Initial schema — all 8 tables

Revision ID: 0001
Revises:
Create Date: 2026-06-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('oauth_provider', sa.String(50), nullable=True),
        sa.Column('oauth_id', sa.String(255), nullable=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('default_city', sa.String(100), nullable=True),
        sa.Column('language_pref', sa.String(20), server_default='en'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_admin', sa.Boolean(), server_default='false'),
        sa.Column('email_verified', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table('searches',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('session_id', sa.String(64), nullable=True),
        sa.Column('symptom_text', sa.Text(), nullable=False),
        sa.Column('specialist_type', sa.String(100), nullable=True),
        sa.Column('urgency_level', sa.String(20), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('fee_min', sa.Integer(), nullable=True),
        sa.Column('fee_max', sa.Integer(), nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=True),
        sa.Column('emergency_mode', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_searches_user_id', 'searches', ['user_id'])
    op.create_index('ix_searches_created_at', 'searches', ['created_at'])

    op.create_table('saved_places',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('google_place_id', sa.String(100), nullable=False),
        sa.Column('place_name', sa.String(255), nullable=True),
        sa.Column('place_type', sa.String(50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('phone_number', sa.String(30), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('specialist_type', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('saved_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'google_place_id', name='uq_user_place'),
    )

    op.create_table('feedback',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('google_place_id', sa.String(100), nullable=False),
        sa.Column('search_id', UUID(as_uuid=False), sa.ForeignKey('searches.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rating', sa.SmallInteger(), nullable=False),
        sa.Column('comment', sa.String(200), nullable=True),
        sa.Column('visited', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('fee_estimates',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('specialist_type', sa.String(100), nullable=False),
        sa.Column('fee_min', sa.Integer(), nullable=False),
        sa.Column('fee_max', sa.Integer(), nullable=False),
        sa.Column('sample_count', sa.Integer(), nullable=True),
        sa.Column('data_source', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('city', 'specialist_type', name='uq_city_specialist'),
    )
    op.create_index('ix_fee_estimates_city', 'fee_estimates', ['city'])
    op.create_index('ix_fee_estimates_specialist', 'fee_estimates', ['specialist_type'])

    op.create_table('city_configs',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('city_name', sa.String(100), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('country_code', sa.String(2), server_default='IN'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('search_radius', sa.Integer(), server_default='5000'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table('emergency_events',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('session_id', sa.String(64), nullable=True),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('symptom_text', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('action_taken', sa.String(50), nullable=True),
        sa.Column('nearest_er_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_emergency_events_city', 'emergency_events', ['city'])
    op.create_index('ix_emergency_events_created_at', 'emergency_events', ['created_at'])

    op.create_table('refresh_tokens',
        sa.Column('id', UUID(as_uuid=False), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=False), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('refresh_tokens')
    op.drop_table('emergency_events')
    op.drop_table('city_configs')
    op.drop_table('fee_estimates')
    op.drop_table('feedback')
    op.drop_table('saved_places')
    op.drop_table('searches')
    op.drop_table('users')
