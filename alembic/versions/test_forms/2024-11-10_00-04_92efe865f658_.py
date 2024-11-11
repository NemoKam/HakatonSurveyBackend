"""empty message

Revision ID: 92efe865f658
Revises: 4bf7978cef24
Create Date: 2024-11-10 00:04:50.755209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92efe865f658'
down_revision: Union[str, None] = '4bf7978cef24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('survey_document_table',
    sa.Column('survey_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('refresh_document_datetime', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['survey_id'], ['survey_table.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_survey_document_table_id'), 'survey_document_table', ['id'], unique=False)
    op.add_column('survey_table', sa.Column('document_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'survey_table', 'survey_document_table', ['document_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'survey_table', type_='foreignkey')
    op.drop_column('survey_table', 'document_id')
    op.drop_index(op.f('ix_survey_document_table_id'), table_name='survey_document_table')
    op.drop_table('survey_document_table')
    # ### end Alembic commands ###