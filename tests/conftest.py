"""
Configuración de pytest para el proyecto.

HUMAN REVIEW (Maria Paula Gutierrez):
Este archivo configura fixtures reutilizables para todos los tests.
Incluye datos de ejemplo y configuración de la base de datos de prueba.
"""
import pytest
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path


@pytest.fixture
def sample_transaction_data() -> Dict[str, Any]:
    """Datos de ejemplo para una transacción válida."""
    return {
        "id": "test_txn_001",  # Campo 'id' requerido por el código
        "transaction_id": "test_txn_001",  # Alias para compatibilidad
        "user_id": "user_test_001",
        "amount": 100.0,
        "location": {
            "latitude": 4.7110,
            "longitude": -74.0721
        },  # Bogotá, Colombia
        "device_id": "device_001",
        "timestamp": datetime.now().isoformat(),
        "metadata": {}
    }


@pytest.fixture
def high_risk_transaction_data() -> Dict[str, Any]:
    """Datos de ejemplo para una transacción de alto riesgo."""
    return {
        "transaction_id": "test_txn_high_risk",
        "user_id": "user_test_002",
        "amount": 5000.0,  # Monto alto
        "location": "40.7128,-74.0060",  # Nueva York (ubicación inusual)
        "device_id": "new_device_suspicious",
        "timestamp": datetime.now().isoformat(),
        "metadata": {}
    }


@pytest.fixture
def mock_mongodb():
    """Mock de MongoDB para tests."""
    from unittest.mock import MagicMock
    
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.transactions = mock_collection
    mock_db.custom_rules = MagicMock()
    
    return mock_db


@pytest.fixture
def mock_redis():
    """Mock de Redis para tests."""
    from unittest.mock import MagicMock
    
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    
    return mock_redis


def pytest_sessionstart(session):
    """Ensure service src folders are on sys.path so imports like `src.*` work."""
    repo_root = Path(__file__).resolve().parents[1]
    # Make the repository root importable so tests can `import services...`
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    services_dir = repo_root / 'services'
    if services_dir.exists():
        for child in services_dir.iterdir():
            src_folder = child / 'src'
            if src_folder.exists():
                p = str(src_folder)
                if p not in sys.path:
                    sys.path.insert(0, p)
