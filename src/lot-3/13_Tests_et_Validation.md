# Tests et Validation - Espace Métier Perplexity AI

## Vue d'ensemble
Ce document présente la stratégie complète de tests et validation pour l'espace métier Perplexity AI, couvrant tous les niveaux de test depuis les tests unitaires jusqu'aux tests d'acceptation utilisateur.

## Stratégie de Tests Globale

### Pyramide de Tests

#### Architecture des Tests
```
                    ┌─────────────────┐
                    │   Tests E2E     │  ← Interface utilisateur complète
                    │   (Selenium)    │
                    └─────────────────┘
                  ┌───────────────────────┐
                  │  Tests d'Intégration  │  ← APIs, Base de données
                  │  (API, DB, Services)  │
                  └───────────────────────┘
            ┌─────────────────────────────────────┐
            │           Tests Unitaires           │  ← Fonctions, Classes
            │     (Pytest, Jest, JUnit)          │
            └─────────────────────────────────────┘
```

#### Distribution des Tests (Recommandée)
- **Tests Unitaires** : 70% - Rapides, isolés, nombreux
- **Tests d'Intégration** : 20% - Modérément rapides, composants
- **Tests E2E** : 10% - Lents, critiques, interface utilisateur

### Framework de Tests Python

#### Configuration Pytest Avancée
```python
# conftest.py - Configuration globale des tests
import pytest
import asyncio
import logging
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Generator, Dict, Any
import tempfile
import shutil
from pathlib import Path

# Configuration test database
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

# Configuration Redis test
import redis
import fakeredis

# Fixtures globales
@pytest.fixture(scope="session")
def event_loop():
    """Crée event loop pour tests async"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_database():
    """Base de données de test isolée"""
    # Crée DB temporaire
    engine = sa.create_engine("sqlite:///:memory:", echo=False)
    
    # Applique migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")
    
    with engine.connect() as connection:
        alembic_cfg.attributes['connection'] = connection
        command.upgrade(alembic_cfg, "head")
    
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(test_database):
    """Session database pour chaque test"""
    Session = sessionmaker(bind=test_database)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()

@pytest.fixture
def redis_client():
    """Client Redis fake pour tests"""
    fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)
    yield fake_redis
    fake_redis.flushall()

@pytest.fixture
def temp_workspace():
    """Répertoire temporaire pour tests fichiers"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_api_calls():
    """Mock pour appels API externes"""
    with patch('requests.Session.request') as mock_request:
        def side_effect(*args, **kwargs):
            # Simule réponses API selon URL
            url = args[1] if len(args) > 1 else kwargs.get('url', '')
            
            if 'api.competitor.com' in url:
                response = Mock()
                response.status_code = 200
                response.json.return_value = {
                    'prices': [{'product_id': 'TEST001', 'price': 99.99}]
                }
                return response
            
            # Réponse par défaut
            response = Mock()
            response.status_code = 404
            return response
        
        mock_request.side_effect = side_effect
        yield mock_request

@pytest.fixture
def sample_user_data():
    """Données utilisateur pour tests"""
    return {
        'id': 'test-user-123',
        'email': 'test@example.com',
        'role': 'expert_metier',
        'spaces': ['space-001', 'space-002']
    }

@pytest.fixture
def sample_script_data():
    """Données script Python pour tests"""
    return {
        'id': 'script-123',
        'name': 'Test Price Analysis',
        'code': '''
import pandas as pd

def analyze_prices(data):
    df = pd.DataFrame(data)
    return {
        'mean_price': df['price'].mean(),
        'max_price': df['price'].max(),
        'min_price': df['price'].min()
    }
''',
        'author_id': 'test-user-123',
        'space_id': 'space-001',
        'status': 'validated'
    }

# Configuration logging pour tests
logging.basicConfig(level=logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

# Markers personnalisés
def pytest_configure(config):
    """Configuration des markers pytest"""
    config.addinivalue_line("markers", "unit: Tests unitaires rapides")
    config.addinivalue_line("markers", "integration: Tests d'intégration")
    config.addinivalue_line("markers", "slow: Tests lents")
    config.addinivalue_line("markers", "security: Tests sécurité")
    config.addinivalue_line("markers", "performance: Tests performance")

# Hooks personnalisés
def pytest_runtest_setup(item):
    """Setup avant chaque test"""
    # Log début test
    print(f"\n🧪 Début test: {item.name}")

def pytest_runtest_teardown(item, nextitem):
    """Cleanup après chaque test"""
    # Log fin test
    print(f"✅ Fin test: {item.name}")

# Paramètres de configuration
def pytest_addoption(parser):
    """Options CLI personnalisées"""
    parser.addoption(
        "--run-slow", action="store_true", default=False,
        help="Exécute les tests marqués comme lents"
    )
    parser.addoption(
        "--run-integration", action="store_true", default=False,
        help="Exécute les tests d'intégration"
    )

def pytest_collection_modifyitems(config, items):
    """Modifie collection de tests selon options"""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="Tests lents ignorés (utilisez --run-slow)")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="Tests intégration ignorés (utilisez --run-integration)")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
```

#### Tests Unitaires - Modules Métier
```python
# tests/unit/test_price_analyzer.py
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.business.price_analyzer import PriceAnalyzer
from src.business.exceptions import InsufficientDataError, AnalysisError

class TestPriceAnalyzer:
    """Tests unitaires pour PriceAnalyzer"""
    
    @pytest.fixture
    def price_analyzer(self):
        """Instance PriceAnalyzer pour tests"""
        return PriceAnalyzer()
    
    @pytest.fixture
    def sample_price_data(self):
        """Données prix sample pour tests"""
        return [
            {'product_sku': 'PROD001', 'price': 99.99, 'timestamp': '2025-09-01T10:00:00Z', 'competitor': 'CompA'},
            {'product_sku': 'PROD001', 'price': 105.50, 'timestamp': '2025-09-01T11:00:00Z', 'competitor': 'CompB'},
            {'product_sku': 'PROD001', 'price': 98.75, 'timestamp': '2025-09-01T12:00:00Z', 'competitor': 'CompC'},
            {'product_sku': 'PROD002', 'price': 149.99, 'timestamp': '2025-09-01T10:00:00Z', 'competitor': 'CompA'},
            {'product_sku': 'PROD002', 'price': 155.00, 'timestamp': '2025-09-01T11:00:00Z', 'competitor': 'CompB'},
        ]
    
    @pytest.mark.unit
    def test_calculate_price_statistics_success(self, price_analyzer, sample_price_data):
        """Test calcul statistiques prix - cas normal"""
        # Arrange
        price_analyzer.load_price_history(sample_price_data)
        
        # Act
        stats = price_analyzer.calculate_price_statistics('PROD001')
        
        # Assert
        assert stats is not None
        assert 'mean_price' in stats
        assert 'median_price' in stats
        assert 'std_deviation' in stats
        assert stats['mean_price'] == pytest.approx(101.41, rel=1e-2)
        assert stats['min_price'] == 98.75
        assert stats['max_price'] == 105.50
    
    @pytest.mark.unit
    def test_calculate_price_statistics_no_data(self, price_analyzer):
        """Test calcul statistiques prix - aucune donnée"""
        # Act & Assert
        stats = price_analyzer.calculate_price_statistics('NONEXISTENT')
        assert stats == {}
    
    @pytest.mark.unit
    def test_detect_price_anomalies_spike(self, price_analyzer):
        """Test détection anomalies - pic de prix"""
        # Arrange
        anomaly_data = [
            {'product_sku': 'PROD001', 'price': 100.0, 'timestamp': '2025-09-01T10:00:00Z'},
            {'product_sku': 'PROD001', 'price': 101.0, 'timestamp': '2025-09-01T11:00:00Z'},
            {'product_sku': 'PROD001', 'price': 99.0, 'timestamp': '2025-09-01T12:00:00Z'},
            {'product_sku': 'PROD001', 'price': 200.0, 'timestamp': '2025-09-01T13:00:00Z'},  # Anomalie
        ]
        price_analyzer.load_price_history(anomaly_data)
        
        # Act
        anomaly_result = price_analyzer.detect_price_anomalies('PROD001', 200.0)
        
        # Assert
        assert anomaly_result['is_anomaly'] is True
        assert anomaly_result['anomaly_type'] == 'price_spike'
        assert anomaly_result['z_score'] > 2.0
    
    @pytest.mark.unit
    def test_generate_pricing_recommendations_aggressive(self, price_analyzer):
        """Test génération recommandations - stratégie agressive"""
        # Arrange
        competitor_prices = {
            'CompA': 95.0,
            'CompB': 98.0,
            'CompC': 92.0
        }
        business_rules = {
            'target_competitive_position': 'aggressive',
            'min_margin_percent': 5
        }
        current_price = 100.0
        
        # Act
        recommendations = price_analyzer.generate_pricing_recommendations(
            'PROD001', current_price, competitor_prices, business_rules
        )
        
        # Assert
        assert recommendations['recommended_price'] < current_price
        assert recommendations['competitive_analysis']['competitor_mean'] == pytest.approx(95.0, rel=1e-2)
    
    @pytest.mark.unit 
    def test_price_variation_calculation(self, price_analyzer):
        """Test calcul variation prix"""
        # Arrange & Act
        variation = price_analyzer._calculate_variation(100.0, 110.0)
        
        # Assert
        assert variation == pytest.approx(10.0, rel=1e-2)
    
    @pytest.mark.unit
    def test_competitive_position_calculation(self, price_analyzer):
        """Test calcul position concurrentielle"""
        # Arrange
        our_price = 100.0
        competitor_prices = [80.0, 90.0, 110.0, 120.0]  # Notre prix au milieu
        
        # Act
        position = price_analyzer._calculate_competitive_position(our_price, competitor_prices)
        
        # Assert
        assert position == 'middle'
    
    @pytest.mark.unit
    @pytest.mark.parametrize("current,new,expected", [
        (100.0, 110.0, 'low'),      # +10% = risque faible
        (100.0, 120.0, 'medium'),   # +20% = risque moyen  
        (100.0, 140.0, 'high'),     # +40% = risque élevé
    ])
    def test_pricing_risk_assessment(self, price_analyzer, current, new, expected):
        """Test évaluation risque pricing - cas paramétrés"""
        # Arrange
        price_change_percent = (new - current) / current
        
        # Act
        risk = price_analyzer._assess_pricing_risk(price_change_percent)
        
        # Assert
        assert risk == expected
    
    @pytest.mark.unit
    def test_load_price_history_invalid_format(self, price_analyzer):
        """Test chargement historique - format invalide"""
        # Arrange
        invalid_data = [
            {'invalid_field': 'value'},  # Manque champs requis
        ]
        
        # Act & Assert
        with pytest.raises(ValueError, match="Format de données invalide"):
            price_analyzer.load_price_history(invalid_data)
    
    @pytest.mark.unit
    def test_thread_safety(self, price_analyzer, sample_price_data):
        """Test thread safety des calculs"""
        import threading
        import time
        
        # Arrange
        price_analyzer.load_price_history(sample_price_data)
        results = []
        
        def calculate_stats():
            stats = price_analyzer.calculate_price_statistics('PROD001')
            results.append(stats['mean_price'])
        
        # Act - Exécution parallèle
        threads = []
        for _ in range(5):
            t = threading.Thread(target=calculate_stats)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Assert - Tous résultats identiques
        assert all(result == results[0] for result in results)
        assert len(results) == 5


# tests/unit/test_workflow_engine.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime

from src.workflow.engine import WorkflowEngine, WorkflowStatus
from src.workflow.steps import PythonScriptStep, APICallStep, DecisionStep
from src.workflow.exceptions import WorkflowExecutionError

class TestWorkflowEngine:
    """Tests unitaires pour WorkflowEngine"""
    
    @pytest.fixture
    def workflow_engine(self):
        """Instance WorkflowEngine pour tests"""
        return WorkflowEngine()
    
    @pytest.fixture
    def mock_python_step(self):
        """Mock étape Python"""
        step = Mock(spec=PythonScriptStep)
        step.step_name = "python_analysis"
        step.execute = AsyncMock(return_value={'result': 'success', 'data': [1, 2, 3]})
        return step
    
    @pytest.fixture
    def mock_api_step(self):
        """Mock étape API"""
        step = Mock(spec=APICallStep)
        step.step_name = "api_call"
        step.execute = AsyncMock(return_value={'status': 'ok', 'response': {'value': 42}})
        return step
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, workflow_engine, mock_python_step, mock_api_step):
        """Test exécution workflow - succès"""
        # Arrange
        workflow_engine.add_step(mock_python_step)
        workflow_engine.add_step(mock_api_step)
        
        initial_context = {'input': 'test_data'}
        
        # Act
        result = await workflow_engine.execute_workflow(initial_context)
        
        # Assert
        assert result['status'] == WorkflowStatus.COMPLETED
        assert 'result' in result['context']
        mock_python_step.execute.assert_called_once()
        mock_api_step.execute.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_execute_workflow_step_failure(self, workflow_engine, mock_python_step):
        """Test exécution workflow - échec étape"""
        # Arrange
        mock_python_step.execute = AsyncMock(side_effect=Exception("Step failed"))
        workflow_engine.add_step(mock_python_step)
        
        # Act & Assert
        with pytest.raises(WorkflowExecutionError):
            await workflow_engine.execute_workflow({'input': 'test'})
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_workflow_timeout(self, workflow_engine):
        """Test timeout workflow"""
        # Arrange
        slow_step = Mock()
        slow_step.step_name = "slow_step"
        slow_step.execute = AsyncMock()
        
        async def slow_execution(context):
            await asyncio.sleep(10)  # Trop lent
            return context
        
        slow_step.execute = slow_execution
        workflow_engine.add_step(slow_step)
        workflow_engine.timeout_seconds = 1  # Timeout court
        
        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await workflow_engine.execute_workflow({'input': 'test'})
    
    @pytest.mark.unit
    def test_add_remove_steps(self, workflow_engine, mock_python_step):
        """Test ajout/suppression étapes"""
        # Test ajout
        workflow_engine.add_step(mock_python_step)
        assert len(workflow_engine.steps) == 1
        assert workflow_engine.steps[0] == mock_python_step
        
        # Test suppression
        workflow_engine.remove_step("python_analysis")
        assert len(workflow_engine.steps) == 0
    
    @pytest.mark.unit
    def test_workflow_validation(self, workflow_engine):
        """Test validation workflow"""
        # Workflow vide invalide
        assert not workflow_engine.validate_workflow()
        
        # Ajoute étape
        mock_step = Mock()
        mock_step.step_name = "test_step"
        mock_step.validate = Mock(return_value=True)
        workflow_engine.add_step(mock_step)
        
        # Workflow valide
        assert workflow_engine.validate_workflow()


# tests/unit/test_security.py
import pytest
from unittest.mock import Mock, patch
import jwt
from datetime import datetime, timedelta

from src.security.auth import AuthManager, TokenValidator
from src.security.sandbox import PythonSandbox
from src.security.exceptions import AuthenticationError, SecurityViolationError

class TestAuthManager:
    """Tests sécurité authentification"""
    
    @pytest.fixture
    def auth_manager(self):
        """Instance AuthManager pour tests"""
        return AuthManager(secret_key="test-secret-key-12345")
    
    @pytest.mark.unit
    def test_generate_jwt_token_success(self, auth_manager):
        """Test génération token JWT"""
        # Arrange
        user_data = {'user_id': '123', 'role': 'expert_metier'}
        
        # Act
        token = auth_manager.generate_token(user_data)
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        
        # Décode et vérifie
        decoded = jwt.decode(token, "test-secret-key-12345", algorithms=["HS256"])
        assert decoded['user_id'] == '123'
        assert decoded['role'] == 'expert_metier'
        assert 'exp' in decoded
    
    @pytest.mark.unit
    def test_validate_token_success(self, auth_manager):
        """Test validation token valide"""
        # Arrange
        user_data = {'user_id': '123', 'role': 'expert_metier'}
        token = auth_manager.generate_token(user_data)
        
        # Act
        validated_data = auth_manager.validate_token(token)
        
        # Assert
        assert validated_data['user_id'] == '123'
        assert validated_data['role'] == 'expert_metier'
    
    @pytest.mark.unit
    def test_validate_token_expired(self, auth_manager):
        """Test validation token expiré"""
        # Arrange - Token expiré
        expired_payload = {
            'user_id': '123',
            'exp': datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(expired_payload, "test-secret-key-12345", algorithm="HS256")
        
        # Act & Assert
        with pytest.raises(AuthenticationError, match="Token expiré"):
            auth_manager.validate_token(expired_token)
    
    @pytest.mark.unit
    def test_validate_token_invalid_signature(self, auth_manager):
        """Test validation token signature invalide"""
        # Arrange - Token avec mauvaise signature
        bad_token = jwt.encode({'user_id': '123'}, "wrong-secret", algorithm="HS256")
        
        # Act & Assert
        with pytest.raises(AuthenticationError, match="Signature invalide"):
            auth_manager.validate_token(bad_token)

class TestPythonSandbox:
    """Tests sandbox Python sécurisé"""
    
    @pytest.fixture
    def sandbox(self):
        """Instance PythonSandbox pour tests"""
        return PythonSandbox(
            max_execution_time=10,
            max_memory_mb=128,
            allowed_imports=['pandas', 'numpy']
        )
    
    @pytest.mark.unit
    def test_execute_safe_code_success(self, sandbox):
        """Test exécution code sécurisé"""
        # Arrange
        safe_code = """
import pandas as pd
data = [1, 2, 3, 4, 5]
df = pd.DataFrame({'values': data})
result = df['values'].sum()
"""
        
        # Act
        result = sandbox.execute_code(safe_code)
        
        # Assert
        assert result['success'] is True
        assert result['output'] is not None
        assert 'result' in result['locals']
        assert result['locals']['result'] == 15
    
    @pytest.mark.unit
    def test_execute_code_blocked_import(self, sandbox):
        """Test blocage import non autorisé"""
        # Arrange
        dangerous_code = """
import os
os.system('ls')
"""
        
        # Act & Assert
        with pytest.raises(SecurityViolationError, match="Import non autorisé: os"):
            sandbox.execute_code(dangerous_code)
    
    @pytest.mark.unit
    def test_execute_code_timeout(self, sandbox):
        """Test timeout exécution"""
        # Arrange
        slow_code = """
import time
time.sleep(20)  # Plus long que timeout
"""
        sandbox.max_execution_time = 1  # 1 seconde
        
        # Act & Assert
        with pytest.raises(TimeoutError, match="Timeout exécution"):
            sandbox.execute_code(slow_code)
    
    @pytest.mark.unit
    def test_execute_code_memory_limit(self, sandbox):
        """Test limite mémoire"""
        # Arrange
        memory_intensive_code = """
# Crée liste énorme
big_list = [0] * (10**8)  # ~800MB
"""
        sandbox.max_memory_mb = 64  # Limite basse
        
        # Act & Assert  
        with pytest.raises(MemoryError, match="Limite mémoire dépassée"):
            sandbox.execute_code(memory_intensive_code)
    
    @pytest.mark.unit
    @pytest.mark.parametrize("code,expected_error", [
        ("exec('import os')", "Fonction exec bloquée"),
        ("eval('__import__(\"os\")')", "Fonction eval bloquée"),
        ("open('/etc/passwd')", "Accès fichier bloqué"),
    ])
    def test_security_restrictions(self, sandbox, code, expected_error):
        """Test restrictions sécurité - cas paramétrés"""
        with pytest.raises(SecurityViolationError, match=expected_error):
            sandbox.execute_code(code)
```

### Tests d'Intégration

#### Tests APIs et Services
```python
# tests/integration/test_api_endpoints.py
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from src.main import app
from src.database import get_db
from src.auth import get_current_user

class TestScriptAPIEndpoints:
    """Tests intégration endpoints API scripts"""
    
    @pytest.fixture
    def client(self, db_session):
        """Client test avec DB override"""
        def override_get_db():
            yield db_session
        
        def override_get_current_user():
            return {
                'user_id': 'test-user-123',
                'role': 'expert_metier',
                'email': 'test@example.com'
            }
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        with TestClient(app) as test_client:
            yield test_client
        
        app.dependency_overrides.clear()
    
    @pytest.mark.integration
    def test_create_script_success(self, client, sample_script_data):
        """Test création script via API"""
        # Act
        response = client.post("/api/scripts", json=sample_script_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == sample_script_data['name']
        assert 'id' in data
        assert data['status'] == 'validated'
    
    @pytest.mark.integration
    def test_execute_script_success(self, client, sample_script_data):
        """Test exécution script via API"""
        # Arrange - Crée script d'abord
        create_response = client.post("/api/scripts", json=sample_script_data)
        script_id = create_response.json()['id']
        
        execution_data = {
            'input_data': [
                {'price': 100.0},
                {'price': 110.0}, 
                {'price': 95.0}
            ]
        }
        
        # Act
        response = client.post(f"/api/scripts/{script_id}/execute", json=execution_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'completed'
        assert 'output_data' in data
        assert data['output_data']['mean_price'] == pytest.approx(101.67, rel=1e-2)
    
    @pytest.mark.integration
    def test_get_script_history(self, client, sample_script_data):
        """Test récupération historique exécutions"""
        # Arrange - Crée script et exécute plusieurs fois
        create_response = client.post("/api/scripts", json=sample_script_data)
        script_id = create_response.json()['id']
        
        # Exécute 3 fois
        for i in range(3):
            client.post(f"/api/scripts/{script_id}/execute", json={'input_data': []})
        
        # Act
        response = client.get(f"/api/scripts/{script_id}/executions")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data['executions']) == 3
        
        # Vérifie ordre chronologique
        timestamps = [exec['started_at'] for exec in data['executions']]
        assert timestamps == sorted(timestamps, reverse=True)  # Plus récent en premier
    
    @pytest.mark.integration
    def test_unauthorized_access(self, client, sample_script_data):
        """Test accès non autorisé"""
        # Override pour utilisateur non connecté
        app.dependency_overrides[get_current_user] = lambda: None
        
        try:
            # Act
            response = client.get("/api/scripts")
            
            # Assert
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()
    
    @pytest.mark.integration 
    def test_role_based_access(self, client, sample_script_data):
        """Test contrôle accès basé rôles"""
        # Override pour utilisateur basic
        def override_basic_user():
            return {
                'user_id': 'basic-user',
                'role': 'user_metier',  # Rôle basique
                'email': 'basic@example.com'
            }
        
        app.dependency_overrides[get_current_user] = override_basic_user
        
        try:
            # Act - Tente création script (interdit pour user_metier)
            response = client.post("/api/scripts", json=sample_script_data)
            
            # Assert
            assert response.status_code == 403
            assert "permissions insuffisantes" in response.json()['detail'].lower()
        finally:
            app.dependency_overrides.clear()


# tests/integration/test_database_operations.py
import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from src.models.script import PythonScript
from src.models.execution import ScriptExecution  
from src.models.user import User
from src.repositories.script_repository import ScriptRepository

class TestDatabaseIntegration:
    """Tests intégration base de données"""
    
    @pytest.fixture
    def script_repository(self, db_session):
        """Repository scripts pour tests"""
        return ScriptRepository(db_session)
    
    @pytest.mark.integration
    def test_create_and_retrieve_script(self, script_repository, sample_script_data):
        """Test création et récupération script"""
        # Act - Création
        created_script = script_repository.create(sample_script_data)
        
        # Assert - Vérification création
        assert created_script.id is not None
        assert created_script.name == sample_script_data['name']
        
        # Act - Récupération
        retrieved_script = script_repository.get_by_id(created_script.id)
        
        # Assert - Vérification récupération  
        assert retrieved_script is not None
        assert retrieved_script.name == sample_script_data['name']
        assert retrieved_script.code == sample_script_data['code']
    
    @pytest.mark.integration
    def test_script_execution_history(self, db_session, sample_script_data):
        """Test historique exécutions"""
        # Arrange - Crée script
        script = PythonScript(**sample_script_data)
        db_session.add(script)
        db_session.commit()
        
        # Crée plusieurs exécutions
        executions = []
        for i in range(5):
            execution = ScriptExecution(
                script_id=script.id,
                executor_id='test-user-123',
                space_id='space-001',
                status='completed',
                input_data={'iteration': i},
                output_data={'result': i * 2},
                execution_time_ms=100 + i * 10,
                started_at=datetime.now() - timedelta(hours=i),
                completed_at=datetime.now() - timedelta(hours=i) + timedelta(minutes=1)
            )
            executions.append(execution)
            db_session.add(execution)
        
        db_session.commit()
        
        # Act - Requête historique
        history = db_session.query(ScriptExecution)\
            .filter(ScriptExecution.script_id == script.id)\
            .order_by(ScriptExecution.started_at.desc())\
            .all()
        
        # Assert
        assert len(history) == 5
        assert history[0].input_data['iteration'] == 0  # Plus récent en premier
        assert all(exec.status == 'completed' for exec in history)
    
    @pytest.mark.integration
    def test_database_constraints(self, db_session):
        """Test contraintes base de données"""
        # Test contrainte unique email
        user1 = User(email='test@example.com', username='user1', role='user_metier')
        user2 = User(email='test@example.com', username='user2', role='user_metier')
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        # Assert - Doit échouer sur email unique
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    @pytest.mark.integration
    def test_cascade_delete(self, db_session, sample_script_data):
        """Test suppression en cascade"""
        # Arrange - Crée script avec exécutions
        script = PythonScript(**sample_script_data)
        db_session.add(script)
        db_session.commit()
        
        execution = ScriptExecution(
            script_id=script.id,
            executor_id='test-user-123',
            space_id='space-001',
            status='completed'
        )
        db_session.add(execution)
        db_session.commit()
        
        script_id = script.id
        
        # Act - Supprime script
        db_session.delete(script)
        db_session.commit()
        
        # Assert - Exécutions supprimées aussi
        remaining_executions = db_session.query(ScriptExecution)\
            .filter(ScriptExecution.script_id == script_id)\
            .count()
        
        assert remaining_executions == 0


# tests/integration/test_external_apis.py
import pytest
import requests_mock
from unittest.mock import patch

from src.integrations.api_manager import APIManager
from src.integrations.connectors import EcommerceConnector

class TestExternalAPIIntegration:
    """Tests intégration APIs externes"""
    
    @pytest.fixture
    def api_manager(self, redis_client):
        """APIManager avec Redis fake"""
        return APIManager(redis_client)
    
    @pytest.mark.integration
    def test_api_call_with_retry(self, api_manager):
        """Test appel API avec retry automatique"""
        # Configure endpoint  
        api_manager.register_endpoint({
            'name': 'test_api',
            'base_url': 'https://api.test.com',
            'auth_type': 'api_key',
            'credentials': {'api_key': 'test-key'},
            'retry_attempts': 3
        })
        
        with requests_mock.Mocker() as m:
            # Premier appel échoue, deuxième réussit
            m.get('https://api.test.com/data', [
                {'status_code': 500, 'text': 'Server Error'},
                {'status_code': 200, 'json': {'data': 'success'}}
            ])
            
            # Act
            response = api_manager.make_request('test_api', 'data')
            
            # Assert
            assert response['data']['data'] == 'success'
            assert response['metadata']['attempt'] == 2
    
    @pytest.mark.integration
    def test_api_caching(self, api_manager):
        """Test cache API responses"""
        # Configure endpoint
        api_manager.register_endpoint({
            'name': 'cacheable_api',
            'base_url': 'https://api.cacheable.com',
            'cache_ttl': 300
        })
        
        with requests_mock.Mocker() as m:
            m.get('https://api.cacheable.com/data', 
                  json={'timestamp': '2025-09-02T10:00:00Z'})
            
            # Premier appel
            response1 = api_manager.make_request('cacheable_api', 'data')
            
            # Deuxième appel (doit venir du cache)
            response2 = api_manager.make_request('cacheable_api', 'data')
            
            # Assert
            assert response1['data'] == response2['data']
            assert response2['metadata']['from_cache'] is True
            assert m.call_count == 1  # Un seul appel réel
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_rate_limiting(self, api_manager):
        """Test limitation taux requêtes"""
        import time
        
        # Configure endpoint avec limite basse
        api_manager.register_endpoint({
            'name': 'limited_api',
            'base_url': 'https://api.limited.com',
            'rate_limit': 2  # 2 requêtes par minute
        })
        
        with requests_mock.Mocker() as m:
            m.get('https://api.limited.com/data', json={'data': 'ok'})
            
            start_time = time.time()
            
            # 3 appels rapides
            for i in range(3):
                api_manager.make_request('limited_api', 'data', use_cache=False)
            
            end_time = time.time()
            
            # Assert - Le 3ème appel doit avoir attendu
            assert (end_time - start_time) > 60  # Plus d'une minute


# tests/integration/test_workflow_execution.py
import pytest
from unittest.mock import AsyncMock, Mock
import asyncio

from src.workflow.engine import WorkflowEngine
from src.workflow.steps import PythonScriptStep, APICallStep
from src.integrations.python_executor import PythonExecutor

class TestWorkflowIntegration:
    """Tests intégration workflow complet"""
    
    @pytest.fixture
    def workflow_engine(self):
        return WorkflowEngine()
    
    @pytest.fixture
    def python_executor(self, redis_client):
        return PythonExecutor(redis_client)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, workflow_engine, python_executor):
        """Test workflow E2E - Script Python + API"""
        
        # Étape 1: Script Python d'analyse
        python_step = PythonScriptStep(
            step_name="price_analysis",
            script_code="""
import pandas as pd

# Analyse données prix
data = context.get('price_data', [])
df = pd.DataFrame(data)

if not df.empty:
    result = {
        'mean_price': float(df['price'].mean()),
        'max_price': float(df['price'].max()),
        'min_price': float(df['price'].min()),
        'total_products': len(df)
    }
else:
    result = {'error': 'No data'}

context['analysis_result'] = result
""",
            executor=python_executor
        )
        
        # Étape 2: Appel API notification
        api_step = APICallStep(
            step_name="send_notification",
            endpoint_url="https://hooks.slack.com/webhook",
            method="POST",
            payload_template={
                "text": "Analyse terminée: {{analysis_result.total_products}} produits analysés"
            }
        )
        
        # Configure workflow
        workflow_engine.add_step(python_step)
        workflow_engine.add_step(api_step)
        
        # Contexte initial
        initial_context = {
            'price_data': [
                {'product': 'A', 'price': 100.0},
                {'product': 'B', 'price': 150.0},
                {'product': 'C', 'price': 75.0}
            ]
        }
        
        # Mock appel API
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'ok': True}
            
            # Act
            result = await workflow_engine.execute_workflow(initial_context)
        
        # Assert
        assert result['status'].value == 'completed'
        assert 'analysis_result' in result['context']
        assert result['context']['analysis_result']['total_products'] == 3
        assert result['context']['analysis_result']['mean_price'] == pytest.approx(108.33, rel=1e-2)
        
        # Vérifie appel API
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "3 produits analysés" in call_args[1]['json']['text']
```

### Tests End-to-End (E2E)

#### Tests Interface Utilisateur
```python
# tests/e2e/test_user_workflows.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class TestUserWorkflowsE2E:
    """Tests E2E workflows utilisateur complets"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Driver Selenium pour tests E2E"""
        options = Options()
        options.add_argument("--headless")  # Mode headless pour CI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        
        yield driver
        driver.quit()
    
    @pytest.fixture
    def login_user(self, driver):
        """Connecte utilisateur test"""
        driver.get("http://localhost:3000/login")
        
        # Saisit credentials
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        
        email_field.send_keys("test@example.com")
        password_field.send_keys("testpassword")
        
        # Clique connexion
        login_button = driver.find_element(By.ID, "login-button")
        login_button.click()
        
        # Attend redirection dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_script_creation_workflow(self, driver, login_user):
        """Test workflow complet création et exécution script"""
        
        # 1. Navigation vers création script
        create_script_btn = driver.find_element(By.ID, "create-script-btn")
        create_script_btn.click()
        
        # Attend ouverture modal
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "script-modal"))
        )
        
        # 2. Remplissage formulaire
        name_field = driver.find_element(By.ID, "script-name")
        description_field = driver.find_element(By.ID, "script-description")
        code_editor = driver.find_element(By.CLASS_NAME, "code-editor")
        
        name_field.send_keys("Test E2E Script")
        description_field.send_keys("Script créé via tests E2E")
        
        # Saisit code dans éditeur
        test_code = """
import pandas as pd

def analyze_data(data):
    df = pd.DataFrame(data)
    return {
        'count': len(df),
        'sum': df['value'].sum() if 'value' in df.columns else 0
    }

result = analyze_data([{'value': 10}, {'value': 20}])
print(f"Résultat: {result}")
"""
        
        # Simule saisie dans Monaco Editor (plus complexe)
        driver.execute_script(f"""
            window.monacoEditor.setValue(`{test_code}`);
        """)
        
        # 3. Sauvegarde script
        save_button = driver.find_element(By.ID, "save-script-btn")
        save_button.click()
        
        # Attend confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        assert "Script créé avec succès" in success_message.text
        
        # 4. Retour liste scripts
        driver.get("http://localhost:3000/scripts")
        
        # Vérifie script dans liste
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Test E2E Script')]"))
        )
        
        script_row = driver.find_element(By.XPATH, "//tr[contains(., 'Test E2E Script')]")
        assert script_row is not None
        
        # 5. Exécution script
        execute_button = script_row.find_element(By.CLASS_NAME, "execute-btn")
        execute_button.click()
        
        # Attend modal exécution
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "execution-modal"))
        )
        
        # Clique exécuter
        run_button = driver.find_element(By.ID, "run-script-btn")
        run_button.click()
        
        # Attend résultats (peut prendre du temps)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "execution-results"))
        )
        
        # 6. Vérification résultats
        results_section = driver.find_element(By.ID, "execution-results")
        assert "Résultat:" in results_section.text
        assert "count" in results_section.text
        
        # Vérifie statut succès
        status_badge = driver.find_element(By.CLASS_NAME, "status-badge")
        assert "completed" in status_badge.get_attribute("class").lower()
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_dashboard_metrics_display(self, driver, login_user):
        """Test affichage métriques dashboard"""
        
        # Navigation dashboard
        driver.get("http://localhost:3000/dashboard")
        
        # Attend chargement métriques
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "metrics-grid"))
        )
        
        # Vérifie cartes métriques
        metrics_cards = driver.find_elements(By.CLASS_NAME, "metric-card")
        assert len(metrics_cards) >= 4  # Au moins 4 métriques
        
        # Vérifie contenu cartes
        for card in metrics_cards:
            title = card.find_element(By.CLASS_NAME, "metric-title")
            value = card.find_element(By.CLASS_NAME, "metric-value")
            
            assert title.text.strip() != ""
            assert value.text.strip() != ""
            assert value.text.strip() != "-"  # Pas de valeur manquante
        
        # Vérifie graphiques
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "chart-container"))
        )
        
        charts = driver.find_elements(By.CLASS_NAME, "chart-container")
        assert len(charts) >= 2  # Au moins 2 graphiques
        
        # Vérifie que graphiques sont rendus
        for chart in charts:
            canvas_or_svg = chart.find_elements(By.TAG_NAME, "canvas") or chart.find_elements(By.TAG_NAME, "svg")
            assert len(canvas_or_svg) > 0  # Graphique rendu
    
    @pytest.mark.e2e
    def test_responsive_design(self, driver, login_user):
        """Test design responsive"""
        
        # Test sur différentes tailles
        screen_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667),    # Mobile
        ]
        
        for width, height in screen_sizes:
            driver.set_window_size(width, height)
            time.sleep(1)  # Laisse temps adaptation
            
            driver.get("http://localhost:3000/dashboard")
            
            # Vérifie éléments navigation visibles
            nav_menu = driver.find_element(By.CLASS_NAME, "navigation")
            assert nav_menu.is_displayed()
            
            # Vérifie menu hamburger sur mobile
            if width < 768:
                hamburger = driver.find_element(By.CLASS_NAME, "mobile-menu-toggle")
                assert hamburger.is_displayed()
            
            # Vérifie pas de débordement horizontal
            body_width = driver.execute_script("return document.body.scrollWidth")
            assert body_width <= width + 20  # Tolérance 20px


# Configuration pytest pour E2E
# pytest.ini
[tool:pytest]
markers =
    unit: Tests unitaires rapides
    integration: Tests d'intégration
    e2e: Tests end-to-end
    slow: Tests lents (>30s)
    security: Tests sécurité
    performance: Tests performance

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Options par défaut
addopts = 
    -v 
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
    
# Couverture code
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

# Parallélisation
addopts = -n auto

# Timeout tests
timeout = 300
```

### Pipeline de Tests Automatisés

#### Configuration GitHub Actions Tests
```yaml
# .github/workflows/test-pipeline.yml
name: Tests Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    name: Tests Unitaires
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -m "unit" \
          --cov=src \
          --cov-report=xml \
          --junitxml=junit.xml \
          -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-${{ matrix.python-version }}

  integration-tests:
    name: Tests Intégration
    runs-on: ubuntu-latest
    needs: unit-tests
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run migrations
      env:
        DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_db
      run: |
        python manage.py migrate
    
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest tests/integration/ -m "integration" \
          --junitxml=integration-junit.xml \
          -v

  e2e-tests:
    name: Tests E2E
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm install
    
    - name: Start application
      run: |
        python main.py &
        npm run dev &
        sleep 30  # Attend démarrage
    
    - name: Install Chrome
      uses: browser-actions/setup-chrome@latest
    
    - name: Install ChromeDriver
      uses: nanasess/setup-chromedriver@master
    
    - name: Run E2E tests
      run: |
        pytest tests/e2e/ -m "e2e" \
          --junitxml=e2e-junit.xml \
          -v

  security-tests:
    name: Tests Sécurité
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install security tools
      run: |
        pip install bandit safety semgrep
    
    - name: Run Bandit security scan
      run: |
        bandit -r src/ -f json -o bandit-report.json
    
    - name: Run Safety vulnerability check
      run: |
        safety check --json --output safety-report.json
    
    - name: Run Semgrep SAST
      env:
        SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
      run: |
        semgrep --config=auto src/
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json

  performance-tests:
    name: Tests Performance
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup K6
      run: |
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    
    - name: Start test environment
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 60
    
    - name: Run performance tests
      run: |
        k6 run tests/performance/load-test.js \
          --out json=performance-results.json
    
    - name: Upload performance results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: performance-results.json

  test-report:
    name: Rapport Tests
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, e2e-tests, security-tests]
    if: always()
    
    steps:
    - name: Download all artifacts
      uses: actions/download-artifact@v3
    
    - name: Generate test report
      run: |
        echo "# 📊 Rapport de Tests" >> test-report.md
        echo "" >> test-report.md
        echo "## Résumé" >> test-report.md
        
        if [ "${{ needs.unit-tests.result }}" = "success" ]; then
          echo "✅ Tests unitaires: SUCCÈS" >> test-report.md
        else
          echo "❌ Tests unitaires: ÉCHEC" >> test-report.md
        fi
        
        if [ "${{ needs.integration-tests.result }}" = "success" ]; then
          echo "✅ Tests intégration: SUCCÈS" >> test-report.md
        else
          echo "❌ Tests intégration: ÉCHEC" >> test-report.md
        fi
        
        if [ "${{ needs.e2e-tests.result }}" = "success" ]; then
          echo "✅ Tests E2E: SUCCÈS" >> test-report.md
        else
          echo "❌ Tests E2E: ÉCHEC" >> test-report.md
        fi
        
        cat test-report.md
    
    - name: Comment PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = fs.readFileSync('test-report.md', 'utf8');
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: report
          });
```

Cette stratégie complète de tests et validation assure la qualité, la sécurité et les performances de l'espace métier Perplexity AI à tous les niveaux, avec une automatisation intégrée dans le pipeline CI/CD.