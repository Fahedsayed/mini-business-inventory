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
from repository import create_product, delete_product, get_product_by_id, list_products, update_product
from schemas import HealthResponse, ProductCreate, ProductResponse, ProductUpdate


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

    def test_list_products_empty(self):
        products = list_products(self.db)
        self.assertEqual(products, [])

    def test_list_products_populated(self):
        product1 = Product(name="Alpha", sku="SKU-A")
        product2 = Product(name="Beta", sku="SKU-B")
        product3 = Product(name="Gamma", sku="SKU-C")
        create_product(self.db, product1)
        create_product(self.db, product2)
        create_product(self.db, product3)

        products = list_products(self.db)
        self.assertEqual(len(products), 3)
        self.assertEqual([p.id for p in products], sorted([p.id for p in products]))
        self.assertEqual(products[0].sku, "SKU-A")
        self.assertEqual(products[1].sku, "SKU-B")
        self.assertEqual(products[2].sku, "SKU-C")


class CreateProductEndpointTestCase(unittest.TestCase):
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

        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_create_product_success(self):
        payload = {"name": "Test Product", "sku": "TEST-001"}
        response = self.client.post("/products", json=payload)

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertIsInstance(data["id"], int)
        self.assertEqual(data["name"], "Test Product")
        self.assertEqual(data["sku"], "TEST-001")
        self.assertIn("created_at", data)

    def test_create_product_missing_sku(self):
        payload = {"name": "Incomplete Product"}
        response = self.client.post("/products", json=payload)

        self.assertEqual(response.status_code, 422)

    def test_create_product_missing_name(self):
        payload = {"sku": "NO-NAME-001"}
        response = self.client.post("/products", json=payload)

        self.assertEqual(response.status_code, 422)

    def test_create_product_empty_payload(self):
        response = self.client.post("/products", json={})
        self.assertEqual(response.status_code, 422)

    def test_create_product_persisted_in_database(self):
        payload = {"name": "Database Persisted", "sku": "DB-001"}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 201)
        product_id = response.json()["id"]

        db = self.TestingSessionLocal()
        try:
            persisted = get_product_by_id(db, product_id)
            self.assertIsNotNone(persisted)
            self.assertEqual(persisted.name, "Database Persisted")
            self.assertEqual(persisted.sku, "DB-001")
        finally:
            db.close()


class RetrieveProductEndpointTestCase(unittest.TestCase):
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

        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_get_product_success(self):
        db = self.TestingSessionLocal()
        try:
            product = Product(name="Inventory Item", sku="ITEM-100")
            created = create_product(db, product)
            product_id = created.id
        finally:
            db.close()

        response = self.client.get(f"/products/{product_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], product_id)
        self.assertEqual(data["name"], "Inventory Item")
        self.assertEqual(data["sku"], "ITEM-100")
        self.assertIn("created_at", data)

    def test_get_product_not_found(self):
        response = self.client.get("/products/99999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Product not found"})

    def test_get_product_invalid_id_type(self):
        response = self.client.get("/products/abc")
        self.assertEqual(response.status_code, 422)


class ListProductsEndpointTestCase(unittest.TestCase):
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

        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_list_products_empty(self):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_products_populated(self):
        db = self.TestingSessionLocal()
        try:
            p1 = create_product(db, Product(name="Widget Alpha", sku="WID-001"))
            p2 = create_product(db, Product(name="Widget Beta", sku="WID-002"))
            p3 = create_product(db, Product(name="Widget Gamma", sku="WID-003"))
            p1_id, p2_id, p3_id = p1.id, p2.id, p3.id
        finally:
            db.close()

        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

        # Verify deterministic ordering by ID ascending
        ids = [item["id"] for item in data]
        self.assertEqual(ids, [p1_id, p2_id, p3_id])


        # Verify fields match
        self.assertEqual(data[0]["name"], "Widget Alpha")
        self.assertEqual(data[0]["sku"], "WID-001")
        self.assertIn("created_at", data[0])

        self.assertEqual(data[1]["name"], "Widget Beta")
        self.assertEqual(data[1]["sku"], "WID-002")
        self.assertIn("created_at", data[1])

        self.assertEqual(data[2]["name"], "Widget Gamma")
        self.assertEqual(data[2]["sku"], "WID-003")
        self.assertIn("created_at", data[2])


class UpdateProductEndpointTestCase(unittest.TestCase):
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

        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_update_product_success(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, Product(name="Original Name", sku="ORIG-001"))
            product_id = product.id
        finally:
            db.close()

        payload = {"name": "Updated Name", "sku": "UPD-001"}
        response = self.client.put(f"/products/{product_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], product_id)
        self.assertEqual(data["name"], "Updated Name")
        self.assertEqual(data["sku"], "UPD-001")
        self.assertIn("created_at", data)

    def test_update_product_persisted(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, Product(name="Before Update", sku="BEF-001"))
            product_id = product.id
        finally:
            db.close()

        payload = {"name": "After Update", "sku": "AFT-001"}
        self.client.put(f"/products/{product_id}", json=payload)

        db = self.TestingSessionLocal()
        try:
            fetched = get_product_by_id(db, product_id)
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.name, "After Update")
            self.assertEqual(fetched.sku, "AFT-001")
        finally:
            db.close()

    def test_update_product_not_found(self):
        response = self.client.put("/products/99999", json={"name": "X", "sku": "Y"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Product not found"})

    def test_update_product_missing_name(self):
        response = self.client.put("/products/1", json={"sku": "SKU-ONLY"})
        self.assertEqual(response.status_code, 422)

    def test_update_product_missing_sku(self):
        response = self.client.put("/products/1", json={"name": "Name Only"})
        self.assertEqual(response.status_code, 422)

    def test_update_product_empty_payload(self):
        response = self.client.put("/products/1", json={})
        self.assertEqual(response.status_code, 422)


class DeleteProductEndpointTestCase(unittest.TestCase):
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

        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_delete_product_success(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, Product(name="To Delete", sku="DEL-001"))
            product_id = product.id
        finally:
            db.close()

        response = self.client.delete(f"/products/{product_id}")
        self.assertEqual(response.status_code, 204)

    def test_delete_product_no_longer_retrievable(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, Product(name="Gone Soon", sku="GONE-001"))
            product_id = product.id
        finally:
            db.close()

        self.client.delete(f"/products/{product_id}")

        response = self.client.get(f"/products/{product_id}")
        self.assertEqual(response.status_code, 404)

    def test_delete_product_removed_from_db(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, Product(name="DB Check", sku="DBC-001"))
            product_id = product.id
        finally:
            db.close()

        self.client.delete(f"/products/{product_id}")

        db = self.TestingSessionLocal()
        try:
            fetched = get_product_by_id(db, product_id)
            self.assertIsNone(fetched)
        finally:
            db.close()

    def test_delete_product_not_found(self):
        response = self.client.delete("/products/99999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Product not found"})

    def test_delete_product_invalid_id_type(self):
        response = self.client.delete("/products/abc")
        self.assertEqual(response.status_code, 422)
