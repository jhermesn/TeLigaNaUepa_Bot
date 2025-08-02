"""Container para injeção de dependências."""


from dependency_injector import containers, providers
from aiohttp import ClientSession

from src.config import settings
from src.infra.database.connection import DatabaseConnection
from src.infra.database.repositories.all_editais_repository import AllEditaisRepository
from src.infra.database.repositories.guild_settings_repository import GuildSettingsRepository
from src.infra.database.repositories.log_repository import LogRepository
from src.infra.database.repositories.role_repository import RoleRepository
from src.infra.web_scraper.uepa_scraper import UepaScraper
from src.presentation.discord.bot import UEPABot

class Container(containers.DeclarativeContainer):
    """Container para injeção de dependências."""

    config = providers.Configuration()
    config.from_pydantic(settings)

    db_connection = providers.Singleton(DatabaseConnection, db_url=config.DATABASE_URL)

    session = providers.Singleton(db_connection.provided.get_session)

    aiohttp_session = providers.Singleton(ClientSession)

    all_editais_repo = providers.Factory(AllEditaisRepository, session_factory=session)
    guild_settings_repo = providers.Factory(GuildSettingsRepository, session_factory=session)
    log_repo = providers.Factory(LogRepository, session_factory=session)
    role_repo = providers.Factory(RoleRepository, session_factory=session)

    uepa_scraper = providers.Factory(UepaScraper, session=aiohttp_session)

    bot = providers.Singleton(
        UEPABot,
        guild_repo=guild_settings_repo,
        all_editais_repo=all_editais_repo,
        role_repo=role_repo,
        log_repo=log_repo,
        scraper=uepa_scraper,
    )
