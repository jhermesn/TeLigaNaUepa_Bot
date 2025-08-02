"""Implementação do repositório de cargos para SQLAlchemy."""

from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.repositories.interfaces import IRoleRepository
from src.infra.database.tables import GuildRoleDB


class RoleRepository(IRoleRepository):
    """Implementação do repositório de cargos para SQLAlchemy."""

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory

    def add(self, guild_id: str, role_id: str, role_name: str, added_by: str) -> bool:
        with self.session_factory() as session:
            try:
                new_role = GuildRoleDB(
                    guild_id=guild_id,
                    role_id=role_id,
                    role_name=role_name,
                    added_by=added_by,
                )
                session.add(new_role)
                session.commit()
                return True
            except SQLAlchemyError:
                session.rollback()
                return False

    def remove(self, guild_id: str, role_id: str) -> bool:
        with self.session_factory() as session:
            try:
                deleted_rows = (
                    session.query(GuildRoleDB)
                    .filter_by(guild_id=guild_id, role_id=role_id)
                    .delete()
                )
                session.commit()
                return deleted_rows > 0
            except SQLAlchemyError:
                session.rollback()
                return False

    def get_all(self, guild_id: str) -> list[type[GuildRoleDB]]:
        with self.session_factory() as session:
            return (
                session.query(GuildRoleDB)
                .filter_by(guild_id=guild_id)
                .order_by(GuildRoleDB.added_at)
                .all()
            )

    def clear(self, guild_id: str) -> int:
        with self.session_factory() as session:
            try:
                deleted_rows = (
                    session.query(GuildRoleDB).filter_by(guild_id=guild_id).delete()
                )
                session.commit()
                return deleted_rows
            except SQLAlchemyError:
                session.rollback()
                return 0
