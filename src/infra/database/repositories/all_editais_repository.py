import sqlite3
from typing import Set, List

from src.core.repositories.interfaces import IAllEditaisRepository
from src.infra.database.connection import DatabaseConnection


class AllEditaisRepository(IAllEditaisRepository):
    """Implementação do repositório de editais vistos para SQLite."""

    def get_all_hashes(self) -> Set[str]:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT edital_hash FROM all_editais")
            return {row[0] for row in cursor.fetchall()}

    def add_many(self, editais: List[dict]) -> bool:
        # Usando INSERT OR IGNORE para previnir erros com duplicatas
        try:
            with DatabaseConnection() as cursor:
                # Converte os dados para o formato correto do banco
                db_data = []
                for edital in editais:
                    db_data.append({
                        'hash': edital['hash'],
                        'title': edital['title'], 
                        'link': str(edital['link'])
                    })
                
                cursor.executemany(
                    "INSERT OR IGNORE INTO all_editais (edital_hash, title, link) VALUES (:hash, :title, :link)",
                    db_data,
                )
            return True
        except sqlite3.Error as e:
            import logging
            logging.error(f"Erro ao inserir editais: {e}")
            return False

    def is_empty(self) -> bool:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT 1 FROM all_editais LIMIT 1")
            return cursor.fetchone() is None
    
    def clear_all(self) -> int:
        with DatabaseConnection() as cursor:
            cursor.execute("DELETE FROM all_editais")
            return cursor.rowcount
            
    def count_all(self) -> int:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT COUNT(id) FROM all_editais")
            return cursor.fetchone()[0]