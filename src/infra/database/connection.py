import sqlite3
import logging
from src.config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados SQLite."""

    def __init__(self, db_file: str = settings.DATABASE_FILE):
        self.db_file = db_file
        self.conn = None

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
            return self.conn.cursor()
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()


def setup_database():
    """Cria as tabelas do banco de dados se elas não existirem."""
    logger.info("Verificando e configurando o banco de dados...")
    try:
        with DatabaseConnection() as cursor:
            # Tabela de editais postados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS all_editais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    edital_hash TEXT NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(edital_hash)
                )
            ''')

            # Tabela de configurações do servidor
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id TEXT PRIMARY KEY,
                    channel_id TEXT,
                    enabled BOOLEAN DEFAULT 0
                )
            ''')

            # Tabela de cargos mencionados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guild_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT NOT NULL,
                    role_id TEXT NOT NULL,
                    role_name TEXT NOT NULL,
                    added_by TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, role_id)
                )
            ''')

            # Tabela de logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        logger.info("Banco de dados configurado com sucesso.")
    except sqlite3.Error as e:
        logger.error(f"Falha ao configurar o banco de dados: {e}")
        raise 