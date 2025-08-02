"""Gerencia a conexão com o banco de dados usando SQLAlchemy."""

import logging
from contextlib import contextmanager
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.infra.database.tables import Base

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados usando SQLAlchemy."""

    def __init__(self, db_url: str):
        self._engine = create_engine(db_url)
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def setup(self):
        """Cria as tabelas do banco de dados se elas não existirem."""
        logger.info("Verificando e configurando o banco de dados...")
        try:
            Base.metadata.create_all(self._engine)
            logger.info("Banco de dados configurado com sucesso.")
        except Exception as e:
            logger.error("Falha ao configurar o banco de dados: %s", e, exc_info=True)
            raise

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """Fornece uma sessão do SQLAlchemy."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error("Erro na sessão do banco de dados: %s", e, exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()
