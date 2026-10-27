"""Importar todos los modelos para registrar sus tablas en Alembic."""

from app.models.group import Group
from app.models.member import Member

__all__ = ["Group", "Member"]
