import sqlitecloud
import asyncio
import logging
from typing import Any, Tuple
from contextlib import contextmanager

from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._connection_string = settings.SQLITE_CLOUD_CONN_STR

    @contextmanager
    def _get_connection(self):
        conn = None
        try:
            conn_str = settings.SQLITE_CLOUD_CONN_STR or self._connection_string
            if not conn_str:
                raise RuntimeError("SQLITE_CLOUD_CONN_STR is missing in configuration.")
            
            # Connect strictly to SQLite Cloud (ssqlitecloud:// or sqlitecloud://)
            conn = sqlitecloud.connect(conn_str)
            yield conn
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    async def execute(self, query: str, params: Tuple = (), fetch: bool = False) -> Any:
        def _sync_execute():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
                return cursor.lastrowid
        
        try:
            return await asyncio.to_thread(_sync_execute)
        except Exception as e:
            logger.error(f"Query execution failed: {query} | Params: {params} | Error: {e}")
            raise

    async def initialize_schema(self):
        logger.info("Initializing database schema...")
        
        schema_statements = [
            # Core Users
            """
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                points INTEGER DEFAULT 0,
                settings_json TEXT DEFAULT '{}',
                role TEXT DEFAULT 'guest',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Finance
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_code TEXT,
                amount REAL NOT NULL,
                fee REAL DEFAULT 0.0,
                balance REAL,
                vendor TEXT,
                category TEXT,
                transaction_type TEXT DEFAULT 'expense', 
                raw_sms TEXT,
                transaction_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(tg_id)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_txn_code ON transactions(user_id, transaction_code) WHERE transaction_code IS NOT NULL;
            """,
            # CRM / Network Intelligence
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                email TEXT, phone TEXT, company TEXT, context_summary TEXT,
                relationship_score REAL DEFAULT 0.5, last_interaction DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(tg_id)
            )
            """,
            # Workflow / Tasks
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 3, 
                due_date DATETIME,
                status TEXT DEFAULT 'pending', 
                source_type TEXT, 
                source_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(tg_id)
            )
            """,
            # RAG / Knowledge Base
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_name TEXT,
                file_type TEXT,
                raw_text TEXT,
                metadata_json TEXT,
                embedding_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(tg_id)
            )
            """,
            # FTS5 for High-Speed Hybrid Search
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_documents USING fts5(
                raw_text, 
                metadata_json, 
                content='documents', 
                content_rowid='id'
            )
            """,
            # Long-term Memory & Personal Facts
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fact_key TEXT NOT NULL,
                fact_value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(tg_id)
            )
            """,
            # Connected Apps (Universal App Framework)
            """
            CREATE TABLE IF NOT EXISTS user_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                app_id TEXT NOT NULL,
                auth_type TEXT,
                auth_token TEXT,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(tg_id),
                UNIQUE(user_id, app_id)
            )
            """
        ]

        def _sync_init():
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for stmt in schema_statements:
                    for sub_stmt in stmt.split(';'):
                        cleaned = sub_stmt.strip()
                        if cleaned:
                            cursor.execute(cleaned)
                            
                # Migration for existing databases
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'guest'")
                except Exception:
                    pass
                    
                # Sync Admin IDs from config
                if settings.ADMIN_IDS:
                    placeholders = ','.join('?' * len(settings.ADMIN_IDS))
                    cursor.execute(f"UPDATE users SET role = 'admin' WHERE tg_id IN ({placeholders})", settings.ADMIN_IDS)
                    
                conn.commit()

        try:
            await asyncio.to_thread(_sync_init)
            logger.info("Database schema initialized successfully.")
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")

db = DatabaseManager()
