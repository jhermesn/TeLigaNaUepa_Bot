"""Implementação do repositório de logs para SQLAlchemy."""

from typing import Optional, Callable
from contextlib import AbstractContextManager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.repositories.interfaces import ILogRepository
from src.infra.database.tables import LogDB


class LogRepository(ILogRepository):
    """Implementação do repositório de logs para SQLAlchemy."""

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory

    def add(
        self,
        guild_id: Optional[str],
        action: str,
        details: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        with self.session_factory() as session:
            try:
                log_entry = LogDB(
                    guild_id=str(guild_id) if guild_id else None,
                    action=action,
                    details=details,
                    user_id=str(user_id) if user_id else None,
                )
                session.add(log_entry)
                session.commit()
            except SQLAlchemyError:
                session.rollback()
                # Evita que uma falha de log quebre a aplicação
