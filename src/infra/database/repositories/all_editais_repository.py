"""Implementação do repositório de editais vistos para SQLAlchemy."""

from typing import List, Callable, Any
from contextlib import AbstractContextManager

from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.core.entities.edital import Edital
from src.core.repositories.interfaces import IAllEditaisRepository
from src.infra.database.tables import EditalDB


class AllEditaisRepository(IAllEditaisRepository):
    """Implementação do repositório de editais vistos para SQLAlchemy."""

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory

    def get_all_hashes(self) -> set[ColumnElement[Any]]:
        with self.session_factory() as session:
            return {row[0] for row in session.query(EditalDB.edital_hash).all()}

    def add_many(self, editais: List[Edital]) -> bool:
        with self.session_factory() as session:
            try:
                db_editais = [
                    EditalDB(
                        edital_hash=edital.hash,
                        title=edital.title,
                        link=str(edital.link),
                    )
                    for edital in editais
                ]
                session.bulk_save_objects(db_editais)
                session.commit()
                return True
            except SQLAlchemyError:
                session.rollback()
                return False

    def is_empty(self) -> bool:
        with self.session_factory() as session:
            return session.query(EditalDB).first() is None

    def clear_all(self) -> int:
        with self.session_factory() as session:
            try:
                deleted_rows = session.query(EditalDB).delete()
                session.commit()
                return deleted_rows
            except SQLAlchemyError:
                session.rollback()
                return 0

    def count_all(self) -> int:
        with self.session_factory() as session:
            return session.query(EditalDB).count()
