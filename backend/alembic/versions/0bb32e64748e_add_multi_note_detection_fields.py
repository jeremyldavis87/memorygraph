"""add_multi_note_detection_fields

Revision ID: 0bb32e64748e
Revises: b8a80815529b
Create Date: 2025-10-27 10:26:25.023096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bb32e64748e'
down_revision: Union[str, None] = 'b8a80815529b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields to users table
    op.add_column('users', sa.Column('vision_model_preference', sa.String(), nullable=True))
    op.add_column('users', sa.Column('ocr_confidence_threshold', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('multi_note_detection_enabled', sa.Boolean(), nullable=True))
    
    # Add new fields to notes table
    op.add_column('notes', sa.Column('parent_note_id', sa.Integer(), nullable=True))
    op.add_column('notes', sa.Column('note_position', sa.Integer(), nullable=True))
    op.add_column('notes', sa.Column('detection_method', sa.String(), nullable=True))
    
    # Add foreign key constraint for parent_note_id
    op.create_foreign_key('fk_notes_parent_note_id', 'notes', 'notes', ['parent_note_id'], ['id'])
    
    # Set default values for existing users
    op.execute("UPDATE users SET vision_model_preference = 'gpt-5-mini' WHERE vision_model_preference IS NULL")
    op.execute("UPDATE users SET ocr_confidence_threshold = 90 WHERE ocr_confidence_threshold IS NULL")
    op.execute("UPDATE users SET multi_note_detection_enabled = true WHERE multi_note_detection_enabled IS NULL")


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint('fk_notes_parent_note_id', 'notes', type_='foreignkey')
    
    # Remove columns from notes table
    op.drop_column('notes', 'detection_method')
    op.drop_column('notes', 'note_position')
    op.drop_column('notes', 'parent_note_id')
    
    # Remove columns from users table
    op.drop_column('users', 'multi_note_detection_enabled')
    op.drop_column('users', 'ocr_confidence_threshold')
    op.drop_column('users', 'vision_model_preference')
