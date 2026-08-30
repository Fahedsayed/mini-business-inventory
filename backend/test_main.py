import unittest
from unittest.mock import patch
from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
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
        created = create_product(self.db, name="Test Widget", sku="WIDGET-001")

        self.assertIsNotNone(created.id)
        self.assertEqual(created.name, "Test Widget")
        self.assertEqual(created.sku, "WIDGET-001")
        self.assertIsNotNone(created.created_at)

    def test_get_product_by_id(self):
        created = create_product(self.db, name="Gadget", sku="GADGET-001")

        fetched = get_product_by_id(self.db, created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, created.id)
        self.assertEqual(fetched.name, "Gadget")
        self.assertEqual(fetched.sku, "GADGET-001")

    def test_get_product_by_id_nonexistent(self):
        fetched = get_product_by_id(self.db, 99999)
        self.assertIsNone(fetched)

    def test_create_and_retrieve_multiple_products(self):
        created1 = create_product(self.db, name="Item One", sku="SKU-001")
        created2 = create_product(self.db, name="Item Two", sku="SKU-002")

        self.assertNotEqual(created1.id, created2.id)

        fetched1 = get_product_by_id(self.db, created1.id)
        fetched2 = get_product_by_id(self.db, created2.id)

        self.assertIsNotNone(fetched1)
        self.assertIsNotNone(fetched2)
        self.assertEqual(fetched1.name, "Item One")
        self.assertEqual(fetched2.name, "Item Two")

    def test_list_products_empty(self):
        products = list_products(self.db, limit=20, offset=0)
        self.assertEqual(products, [])

    def test_list_products_populated(self):
        create_product(self.db, name="Alpha", sku="SKU-A")
        create_product(self.db, name="Beta", sku="SKU-B")
        create_product(self.db, name="Gamma", sku="SKU-C")

        products = list_products(self.db, limit=20, offset=0)
        self.assertEqual(len(products), 3)
        self.assertEqual([p.id for p in products], sorted([p.id for p in products]))
        self.assertEqual(products[0].sku, "SKU-A")
        self.assertEqual(products[1].sku, "SKU-B")
        self.assertEqual(products[2].sku, "SKU-C")

    def test_list_products_applies_limit_and_offset(self):
        create_product(self.db, name="Alpha", sku="SKU-A")
        create_product(self.db, name="Beta", sku="SKU-B")
        create_product(self.db, name="Gamma", sku="SKU-C")

        products = list_products(self.db, limit=2, offset=1)

        self.assertEqual([product.sku for product in products], ["SKU-B", "SKU-C"])

    def test_list_products_returns_empty_page_beyond_available_records(self):
        create_product(self.db, name="Alpha", sku="SKU-A")

        products = list_products(self.db, limit=20, offset=1)

        self.assertEqual(products, [])


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

    def test_create_product_empty_name(self):
        payload = {"name": "", "sku": "VALID-SKU"}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_product_whitespace_name(self):
        payload = {"name": "   ", "sku": "VALID-SKU"}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_product_empty_sku(self):
        payload = {"name": "Valid Name", "sku": ""}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_product_whitespace_sku(self):
        payload = {"name": "Valid Name", "sku": "   "}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_product_name_too_long(self):
        payload = {"name": "A" * 256, "sku": "VALID-SKU"}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_product_sku_too_long(self):
        payload = {"name": "Valid Name", "sku": "A" * 101}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_product_trims_whitespace(self):
        payload = {"name": "  Trimmed Name  ", "sku": "  TRIM-001  "}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Trimmed Name")
        self.assertEqual(data["sku"], "TRIM-001")

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

    def test_create_product_duplicate_sku_conflict(self):
        payload = {"name": "First Product", "sku": "SKU-DUP"}
        response1 = self.client.post("/products", json=payload)
        self.assertEqual(response1.status_code, 201)

        payload_dup = {"name": "Duplicate Product", "sku": "SKU-DUP"}
        response2 = self.client.post("/products", json=payload_dup)
        self.assertEqual(response2.status_code, 409)
        self.assertEqual(response2.json(), {"detail": "Product with this SKU already exists"})

    @patch("main.create_product", side_effect=SQLAlchemyError("Internal database explosion"))
    def test_create_product_database_error_does_not_leak_internals(self, mock_create):
        payload = {"name": "Valid Product", "sku": "SKU-VALID"}
        response = self.client.post("/products", json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An error occurred while processing the database request"},
        )
        self.assertNotIn("Internal database explosion", response.text)


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
            created = create_product(db, name="Inventory Item", sku="ITEM-100")
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

    @patch("main.get_product_by_id", side_effect=SQLAlchemyError("Internal database explosion"))
    def test_get_product_database_error_does_not_leak_internals(self, mock_get):
        response = self.client.get("/products/1")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An error occurred while processing the database request"},
        )
        self.assertNotIn("Internal database explosion", response.text)


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
            p1 = create_product(db, name="Widget Alpha", sku="WID-001")
            p2 = create_product(db, name="Widget Beta", sku="WID-002")
            p3 = create_product(db, name="Widget Gamma", sku="WID-003")
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

    def test_list_products_uses_default_pagination(self):
        db = self.TestingSessionLocal()
        try:
            for index in range(21):
                create_product(db, name=f"Product {index}", sku=f"PAGE-{index:03d}")
        finally:
            db.close()

        response = self.client.get("/products")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 20)

    def test_list_products_accepts_custom_limit(self):
        db = self.TestingSessionLocal()
        try:
            create_product(db, name="Alpha", sku="SKU-A")
            create_product(db, name="Beta", sku="SKU-B")
            create_product(db, name="Gamma", sku="SKU-C")
        finally:
            db.close()

        response = self.client.get("/products?limit=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([product["sku"] for product in response.json()], ["SKU-A", "SKU-B"])

    def test_list_products_accepts_custom_offset(self):
        db = self.TestingSessionLocal()
        try:
            create_product(db, name="Alpha", sku="SKU-A")
            create_product(db, name="Beta", sku="SKU-B")
            create_product(db, name="Gamma", sku="SKU-C")
        finally:
            db.close()

        response = self.client.get("/products?limit=2&offset=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([product["sku"] for product in response.json()], ["SKU-B", "SKU-C"])

    def test_list_products_accepts_maximum_limit(self):
        response = self.client.get("/products?limit=100")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_products_rejects_invalid_pagination_values(self):
        for query in ("limit=0", "limit=101", "limit=invalid", "offset=-1", "offset=invalid"):
            with self.subTest(query=query):
                response = self.client.get(f"/products?{query}")
                self.assertEqual(response.status_code, 422)

    def test_list_products_returns_empty_result_beyond_available_offset(self):
        db = self.TestingSessionLocal()
        try:
            create_product(db, name="Alpha", sku="SKU-A")
        finally:
            db.close()

        response = self.client.get("/products?offset=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("main.list_products", side_effect=SQLAlchemyError("Internal database explosion"))
    def test_list_products_database_error_does_not_leak_internals(self, mock_list):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An error occurred while processing the database request"},
        )
        self.assertNotIn("Internal database explosion", response.text)


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
            product = create_product(db, name="Original Name", sku="ORIG-001")
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
            product = create_product(db, name="Before Update", sku="BEF-001")
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

    def test_update_product_empty_name(self):
        payload = {"name": "", "sku": "VALID-SKU"}
        response = self.client.put("/products/1", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_update_product_whitespace_name(self):
        payload = {"name": "   ", "sku": "VALID-SKU"}
        response = self.client.put("/products/1", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_update_product_empty_sku(self):
        payload = {"name": "Valid Name", "sku": ""}
        response = self.client.put("/products/1", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_update_product_whitespace_sku(self):
        payload = {"name": "Valid Name", "sku": "   "}
        response = self.client.put("/products/1", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_update_product_name_too_long(self):
        payload = {"name": "A" * 256, "sku": "VALID-SKU"}
        response = self.client.put("/products/1", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_update_product_sku_too_long(self):
        payload = {"name": "Valid Name", "sku": "A" * 101}
        response = self.client.put("/products/1", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_update_product_trims_whitespace(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, name="Original", sku="ORIG-TRIM")
            product_id = product.id
        finally:
            db.close()

        payload = {"name": "  Updated Trimmed  ", "sku": "  UPD-TRIM  "}
        response = self.client.put(f"/products/{product_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Trimmed")
        self.assertEqual(data["sku"], "UPD-TRIM")

    def test_update_product_duplicate_sku_conflict(self):
        db = self.TestingSessionLocal()
        try:
            create_product(db, name="Item 1", sku="SKU-EXISTING-1")
            p2 = create_product(db, name="Item 2", sku="SKU-EXISTING-2")
            p2_id = p2.id
        finally:
            db.close()

        payload = {"name": "Updated Name", "sku": "SKU-EXISTING-1"}
        response = self.client.put(f"/products/{p2_id}", json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "Product with this SKU already exists"})

    def test_update_product_invalid_id_type(self):
        response = self.client.put("/products/abc", json={"name": "Name", "sku": "SKU-001"})
        self.assertEqual(response.status_code, 422)

    @patch("main.update_product", side_effect=SQLAlchemyError("Internal database explosion"))
    def test_update_product_database_error_does_not_leak_internals(self, mock_update):
        payload = {"name": "Valid Name", "sku": "SKU-VALID"}
        response = self.client.put("/products/1", json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An error occurred while processing the database request"},
        )
        self.assertNotIn("Internal database explosion", response.text)


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
            product = create_product(db, name="To Delete", sku="DEL-001")
            product_id = product.id
        finally:
            db.close()

        response = self.client.delete(f"/products/{product_id}")
        self.assertEqual(response.status_code, 204)

    def test_delete_product_no_longer_retrievable(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, name="Gone Soon", sku="GONE-001")
            product_id = product.id
        finally:
            db.close()

        self.client.delete(f"/products/{product_id}")

        response = self.client.get(f"/products/{product_id}")
        self.assertEqual(response.status_code, 404)

    def test_delete_product_removed_from_db(self):
        db = self.TestingSessionLocal()
        try:
            product = create_product(db, name="DB Check", sku="DBC-001")
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

    @patch("main.delete_product", side_effect=SQLAlchemyError("Internal database explosion"))
    def test_delete_product_database_error_does_not_leak_internals(self, mock_delete):
        response = self.client.delete("/products/1")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An error occurred while processing the database request"},
        )
        self.assertNotIn("Internal database explosion", response.text)


class ProductCRUDLifecycleTestCase(unittest.TestCase):
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

    def test_full_product_crud_lifecycle(self):
        # 1. CREATE (POST /products)
        create_payload = {"name": "Lifecycle Laptop", "sku": "LIFE-LAPTOP-01"}
        create_res = self.client.post("/products", json=create_payload)
        self.assertEqual(create_res.status_code, 201)
        created_data = create_res.json()
        product_id = created_data["id"]
        self.assertEqual(created_data["name"], "Lifecycle Laptop")
        self.assertEqual(created_data["sku"], "LIFE-LAPTOP-01")
        self.assertIn("created_at", created_data)

        # 2. RETRIEVE SINGLE (GET /products/{id})
        get_res = self.client.get(f"/products/{product_id}")
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.json()
        self.assertEqual(get_data["id"], product_id)
        self.assertEqual(get_data["name"], "Lifecycle Laptop")
        self.assertEqual(get_data["sku"], "LIFE-LAPTOP-01")

        # 3. LIST ALL (GET /products)
        list_res = self.client.get("/products")
        self.assertEqual(list_res.status_code, 200)
        list_data = list_res.json()
        self.assertEqual(len(list_data), 1)
        self.assertEqual(list_data[0]["id"], product_id)

        # 4. UPDATE (PUT /products/{id})
        update_payload = {"name": "Updated Lifecycle Laptop", "sku": "LIFE-LAPTOP-02"}
        update_res = self.client.put(f"/products/{product_id}", json=update_payload)
        self.assertEqual(update_res.status_code, 200)
        updated_data = update_res.json()
        self.assertEqual(updated_data["id"], product_id)
        self.assertEqual(updated_data["name"], "Updated Lifecycle Laptop")
        self.assertEqual(updated_data["sku"], "LIFE-LAPTOP-02")

        # 5. RETRIEVE UPDATED (GET /products/{id})
        get_updated_res = self.client.get(f"/products/{product_id}")
        self.assertEqual(get_updated_res.status_code, 200)
        self.assertEqual(get_updated_res.json()["name"], "Updated Lifecycle Laptop")
        self.assertEqual(get_updated_res.json()["sku"], "LIFE-LAPTOP-02")

        # 6. DELETE (DELETE /products/{id})
        delete_res = self.client.delete(f"/products/{product_id}")
        self.assertEqual(delete_res.status_code, 204)

        # 7. CONFIRM 404 ON RETRIEVE (GET /products/{id})
        get_deleted_res = self.client.get(f"/products/{product_id}")
        self.assertEqual(get_deleted_res.status_code, 404)
        self.assertEqual(get_deleted_res.json(), {"detail": "Product not found"})

        # 8. CONFIRM EMPTY LIST (GET /products)
        final_list_res = self.client.get("/products")
        self.assertEqual(final_list_res.status_code, 200)
        self.assertEqual(final_list_res.json(), [])

    def test_crud_isolation_across_multiple_entities(self):
        # Create 3 products
        p1 = self.client.post("/products", json={"name": "Item 1", "sku": "ISO-001"}).json()
        p2 = self.client.post("/products", json={"name": "Item 2", "sku": "ISO-002"}).json()
        p3 = self.client.post("/products", json={"name": "Item 3", "sku": "ISO-003"}).json()

        # Verify listing contains all 3
        list_all = self.client.get("/products").json()
        self.assertEqual(len(list_all), 3)

        # Update P2
        upd_p2 = self.client.put(
            f"/products/{p2['id']}",
            json={"name": "Item 2 Modified", "sku": "ISO-002-MOD"},
        )
        self.assertEqual(upd_p2.status_code, 200)

        # Verify P1 and P3 are unaffected
        self.assertEqual(self.client.get(f"/products/{p1['id']}").json()["name"], "Item 1")
        self.assertEqual(self.client.get(f"/products/{p3['id']}").json()["name"], "Item 3")

        # Delete P2
        self.assertEqual(self.client.delete(f"/products/{p2['id']}").status_code, 204)

        # Verify list now has exactly 2 items: P1 and P3
        remaining = self.client.get("/products").json()
        self.assertEqual(len(remaining), 2)
        remaining_ids = [item["id"] for item in remaining]
        self.assertEqual(remaining_ids, [p1["id"], p3["id"]])

        # Verify P2 is 404 on GET, PUT, and DELETE
        self.assertEqual(self.client.get(f"/products/{p2['id']}").status_code, 404)
        self.assertEqual(
            self.client.put(f"/products/{p2['id']}", json={"name": "X", "sku": "Y"}).status_code,
            404,
        )
        self.assertEqual(self.client.delete(f"/products/{p2['id']}").status_code, 404)
