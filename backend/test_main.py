import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent))
from main import app, get_db
from sqlalchemy.orm import Session


client = TestClient(app)


class HealthEndpointTestCase(unittest.TestCase):
    def test_health_response_model(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "healthy"})

    def test_database_session_dependency(self):
        db_generator = get_db()
        db = next(db_generator)
        self.assertIsInstance(db, Session)
        db_generator.close()
