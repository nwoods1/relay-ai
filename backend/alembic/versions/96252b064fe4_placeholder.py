"""placeholder for missing migration

Revision ID: 96252b064fe4
Revises: 16b775558718
Create Date: 2026-09-25
"""

from typing import Sequence, Union


revision: str = "96252b064fe4"

down_revision: Union[
    str,
    None,
] = "16b775558718"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass