import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

sys.path.append(str(Path(__file__).resolve().parent))
from database import Base, SessionLocal, engine, get_db
from main import app
from models import Product


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


class ProductModelTestCase(unittest.TestCase):
    def test_product_inherits_from_base(self):
        self.assertTrue(issubclass(Product, Base))

    def test_product_table_is_registered_in_metadata(self):
        self.assertIn("products", Base.metadata.tables)
        self.assertIs(Base.metadata.tables["products"], Product.__table__)

    def test_product_columns_exist(self):
        self.assertEqual(set(Product.__table__.columns.keys()), {"id", "name", "sku", "created_at"})

    def test_product_id_is_primary_key(self):
        primary_key_columns = [column.name for column in Product.__table__.primary_key.columns]
        self.assertEqual(primary_key_columns, ["id"])

    def test_product_column_types(self):
        columns = Product.__table__.columns
        self.assertIsInstance(columns["id"].type, Integer)
        self.assertIsInstance(columns["name"].type, String)
        self.assertIsInstance(columns["sku"].type, String)
        self.assertIsInstance(columns["created_at"].type, DateTime)

    def test_product_created_at_has_default(self):
        self.assertIsNotNone(Product.__table__.columns["created_at"].server_default)
