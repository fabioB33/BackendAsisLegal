"""
SQLite Knowledge Base Service
Búsqueda por palabras clave (sin torch ni sentence-transformers)
"""
import sqlite3
import json
import logging
import re
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteKnowledgeBase:
    def __init__(self, db_path: str = "/app/backend/prados.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()
        logger.info(f"✅ SQLite KnowledgeBase initialized at {db_path}")

    def _init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conocimiento_legal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    contenido TEXT NOT NULL,
                    embedding TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_titulo
                ON conocimiento_legal(titulo)
            ''')
            conn.commit()
            conn.close()
            logger.info("✅ Database tables created/verified")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _keyword_score(self, query: str, titulo: str, contenido: str) -> float:
        """Puntaje simple por coincidencia de palabras clave."""
        words = set(re.findall(r'\w+', query.lower()))
        text = (titulo + " " + contenido).lower()
        if not words:
            return 0.0
        matches = sum(1 for w in words if w in text)
        return matches / len(words)

    def add_document(self, titulo: str, contenido: str, metadata: Optional[Dict] = None):
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conocimiento_legal (titulo, contenido, metadata)
                VALUES (?, ?, ?)
            ''', (titulo, contenido, metadata_json))
            conn.commit()
            doc_id = cursor.lastrowid
            conn.close()
            logger.info(f"✅ Document added: {titulo} (ID: {doc_id})")
            return doc_id
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, titulo, contenido FROM conocimiento_legal')
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                logger.warning("No documents in knowledge base")
                return []

            results = []
            for doc_id, titulo, contenido in rows:
                score = self._keyword_score(query, titulo, contenido)
                results.append({
                    'id': doc_id,
                    'titulo': titulo,
                    'contenido': contenido,
                    'score': score
                })

            results.sort(key=lambda x: x['score'], reverse=True)
            top_results = results[:top_k]
            logger.info(f"Search '{query}' → {len(top_results)} docs")
            return top_results

        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []

    def get_all_documents(self) -> List[Dict]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, titulo, contenido, metadata FROM conocimiento_legal')
            rows = cursor.fetchall()
            conn.close()
            documents = []
            for doc_id, titulo, contenido, metadata_json in rows:
                metadata = json.loads(metadata_json) if metadata_json else {}
                documents.append({
                    'id': doc_id,
                    'titulo': titulo,
                    'contenido': contenido[:200] + '...',
                    'metadata': metadata
                })
            return documents
        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            return []

    def count_documents(self) -> int:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM conocimiento_legal')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {str(e)}")
            return 0

    def clear_database(self):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conocimiento_legal')
            conn.commit()
            conn.close()
            logger.info("✅ Database cleared")
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            raise
