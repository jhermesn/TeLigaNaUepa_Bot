import sqlite3
from typing import List, Dict, Any
from src.core.repositories.interfaces import IRoleRepository
from src.infra.database.connection import DatabaseConnection


class RoleRepository(IRoleRepository):
    """Implementação do repositório de cargos para SQLite."""

    def add(self, guild_id: str, role_id: str, role_name: str, added_by: str) -> bool:
        try:
            with DatabaseConnection() as cursor:
                cursor.execute(
                    "INSERT INTO guild_roles (guild_id, role_id, role_name, added_by) VALUES (?, ?, ?, ?)",
                    (str(guild_id), str(role_id), role_name, str(added_by)),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def remove(self, guild_id: str, role_id: str) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute(
                "DELETE FROM guild_roles WHERE guild_id = ? AND role_id = ?",
                (str(guild_id), str(role_id)),
            )
            return cursor.rowcount > 0

    def get_all(self, guild_id: str) -> List[Dict[str, Any]]:
        with DatabaseConnection() as cursor:
            cursor.execute(
                "SELECT role_id, role_name, added_by, added_at FROM guild_roles WHERE guild_id = ? ORDER BY added_at",
                (str(guild_id),),
            )
            return [dict(row) for row in cursor.fetchall()]

    def clear(self, guild_id: str) -> int:
        with DatabaseConnection() as cursor:
            cursor.execute(
                "DELETE FROM guild_roles WHERE guild_id = ?", (str(guild_id),)
            )
            return cursor.rowcount 