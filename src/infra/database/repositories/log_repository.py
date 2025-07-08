import sqlite3
from typing import Optional
from src.core.repositories.interfaces import ILogRepository
from src.infra.database.connection import DatabaseConnection


class LogRepository(ILogRepository):
    """Implementação do repositório de logs para SQLite."""

    def add(self, guild_id: Optional[str], action: str, details: Optional[str] = None, user_id: Optional[str] = None) -> None:
        try:
            with DatabaseConnection() as cursor:
                cursor.execute(
                    "INSERT INTO bot_logs (guild_id, action, details, user_id) VALUES (?, ?, ?, ?)",
                    (
                        str(guild_id) if guild_id else None,
                        action,
                        details,
                        str(user_id) if user_id else None,
                    ),
                )
        except sqlite3.Error:
            # Evita que uma falha de log quebre a aplicação
            pass 