import sqlite3
from typing import List, Dict, Any, Optional
from src.core.repositories.interfaces import IGuildSettingsRepository
from src.infra.database.connection import DatabaseConnection


class GuildSettingsRepository(IGuildSettingsRepository):
    """Implementação do repositório de configurações do servidor para SQLite."""

    def get(self, guild_id: str) -> Optional[Dict[str, Any]]:
        with DatabaseConnection() as cursor:
            cursor.execute(
                "SELECT * FROM guild_settings WHERE guild_id = ?",
                (str(guild_id),),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def set(self, guild_id: str, settings: Dict[str, Any]) -> None:
        with DatabaseConnection() as cursor:
            existing = self.get(str(guild_id))
            
            if existing:
                updates = {k: v for k, v in settings.items() if k in ['channel_id', 'enabled']}
                if not updates:
                    return

                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                values = list(updates.values())
                values.append(str(guild_id))

                cursor.execute(
                    f"UPDATE guild_settings SET {set_clause} WHERE guild_id = ?",
                    values,
                )
            else:
                cursor.execute(
                    "INSERT INTO guild_settings (guild_id, channel_id, enabled) VALUES (?, ?, ?)",
                    (
                        str(guild_id),
                        settings.get("channel_id"),
                        settings.get("enabled", False),
                    ),
                )
    
    def get_all_guilds(self) -> List[Dict[str, Any]]:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT * FROM guild_settings WHERE enabled = 1 AND channel_id IS NOT NULL")
            return [dict(row) for row in cursor.fetchall()] 