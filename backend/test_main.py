import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parent))
from database import Base, SessionLocal, engine, get_db
from main import app
from models import Product
from repository import create_product, get_product_by_id


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


class ProductRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.db = self.TestingSessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_product(self):
        product = Product(name="Test Widget", sku="WIDGET-001")
        created = create_product(self.db, product)

        self.assertIsNotNone(created.id)
        self.assertEqual(created.name, "Test Widget")
        self.assertEqual(created.sku, "WIDGET-001")
        self.assertIsNotNone(created.created_at)

    def test_get_product_by_id(self):
        product = Product(name="Gadget", sku="GADGET-001")
        created = create_product(self.db, product)

        fetched = get_product_by_id(self.db, created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, created.id)
        self.assertEqual(fetched.name, "Gadget")
        self.assertEqual(fetched.sku, "GADGET-001")

    def test_get_product_by_id_nonexistent(self):
        fetched = get_product_by_id(self.db, 99999)
        self.assertIsNone(fetched)

    def test_create_and_retrieve_multiple_products(self):
        product1 = Product(name="Item One", sku="SKU-001")
        product2 = Product(name="Item Two", sku="SKU-002")
        created1 = create_product(self.db, product1)
        created2 = create_product(self.db, product2)

        self.assertNotEqual(created1.id, created2.id)

        fetched1 = get_product_by_id(self.db, created1.id)
        fetched2 = get_product_by_id(self.db, created2.id)

        self.assertIsNotNone(fetched1)
        self.assertIsNotNone(fetched2)
        self.assertEqual(fetched1.name, "Item One")
        self.assertEqual(fetched2.name, "Item Two")
