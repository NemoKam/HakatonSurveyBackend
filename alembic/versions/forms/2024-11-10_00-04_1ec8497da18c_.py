"""empty message

Revision ID: 1ec8497da18c
Revises: f5d34d9f07a6
Create Date: 2024-11-10 00:04:47.094673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ec8497da18c'
down_revision: Union[str, None] = 'f5d34d9f07a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('survey_table', sa.Column('document_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'survey_table', 'survey_document_table', ['document_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'survey_table', type_='foreignkey')
    op.drop_column('survey_table', 'document_id')
    # ### end Alembic commands ###
