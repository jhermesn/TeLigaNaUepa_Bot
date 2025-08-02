"""Implementação do repositório de configurações do servidor para SQLAlchemy."""

from typing import Dict, Any, Optional
from sqlalchemy.orm import sessionmaker

from src.core.repositories.interfaces import IGuildSettingsRepository
from src.infra.database.tables import GuildSettingsDB


class GuildSettingsRepository(IGuildSettingsRepository):
    """Implementação do repositório de configurações do servidor para SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def get(self, guild_id: str) -> Optional[GuildSettingsDB]:
        with self.session_factory() as session:
            return session.get(GuildSettingsDB, guild_id)

    def set(self, guild_id: str, settings: Dict[str, Any]) -> None:
        with self.session_factory() as session:
            guild_settings = session.get(GuildSettingsDB, guild_id)
            if guild_settings:
                for key, value in settings.items():
                    setattr(guild_settings, key, value)
            else:
                guild_settings = GuildSettingsDB(guild_id=guild_id, **settings)
                session.add(guild_settings)
            session.commit()

    def get_all_guilds(self) -> list[type[GuildSettingsDB]]:
        with self.session_factory() as session:
            return (
                session.query(GuildSettingsDB)
                .filter(
                    GuildSettingsDB.enabled.is_(True),
                    GuildSettingsDB.channel_id.isnot(None),
                )
                .all()
                )
