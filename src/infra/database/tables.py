"""Define as tabelas do banco de dados."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class EditalDB(Base):
    """Tabela para armazenar os editais vistos."""
    __tablename__ = "all_editais"
    id = Column(Integer, primary_key=True, autoincrement=True)
    edital_hash = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False)
    posted_at = Column(DateTime, server_default=func.now())


class GuildSettingsDB(Base):
    """Tabela para armazenar as configurações do servidor."""
    __tablename__ = "guild_settings"
    guild_id = Column(String, primary_key=True)
    channel_id = Column(String)
    enabled = Column(Boolean, default=False)


class GuildRoleDB(Base):
    """Tabela para armazenar os cargos do servidor."""
    __tablename__ = "guild_roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String, nullable=False)
    role_id = Column(String, nullable=False)
    role_name = Column(String, nullable=False)
    added_by = Column(String)
    added_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint("guild_id", "role_id", name="_guild_role_uc"),)


class LogDB(Base):
    """Tabela para armazenar os logs do bot."""
    __tablename__ = "bot_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String)
    action = Column(String, nullable=False)
    details = Column(String)
    user_id = Column(String)
    timestamp = Column(DateTime, server_default=func.now())


def setup_database(engine):
    """Cria as tabelas no banco de dados se elas não existirem."""
    Base.metadata.create_all(engine)


def get_session_factory(engine):
    """Retorna uma fábrica de sessões para o banco de dados."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
