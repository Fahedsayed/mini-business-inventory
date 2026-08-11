import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

sys.path.append(str(Path(__file__).resolve().parent))
from database import Base, SessionLocal, engine, get_db
from main import app


client = TestClient(app)


class HealthEndpointTestCase(unittest.TestCase):
    def test_health_response_model(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "healthy"})


class DatabaseFoundationTestCase(unittest.TestCase):
    def test_declarative_base_exists(self):
        self.assertTrue(issubclass(Base, DeclarativeBase))

    def test_engine_is_initialized(self):
        self.assertIsInstance(engine, Engine)

    def test_session_factory_is_initialized(self):
        self.assertIsInstance(SessionLocal, sessionmaker)

    def test_database_session_dependency(self):
        db_generator = get_db()
        db = next(db_generator)
        self.assertIsInstance(db, Session)
        db_generator.close()
