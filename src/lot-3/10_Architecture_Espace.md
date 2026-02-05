# Architecture Espace - Espace Métier Perplexity AI

## Vue d'ensemble
Ce document présente l'architecture technique détaillée de l'espace métier Perplexity AI, incluant les diagrammes, les composants, les flux de données et les décisions de conception.

## Architecture Globale du Système

### Vue d'Ensemble Haut Niveau

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESPACE MÉTIER PERPLEXITY AI                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 COUCHE PRÉSENTATION                         │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │ Interface   │ │ Dashboards  │ │ API REST Publique   │  │ │
│  │  │ Utilisateur │ │ Interactifs │ │ & Webhooks          │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↕                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              COUCHE ORCHESTRATION MÉTIER                   │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │ Workflow    │ │ Rules       │ │ Event Sourcing      │  │ │
│  │  │ Engine      │ │ Engine      │ │ & CQRS              │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↕                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               COUCHE TRAITEMENT PYTHON                     │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │ Sandbox     │ │ Script      │ │ ML/AI Processing    │  │ │
│  │  │ Sécurisé    │ │ Executor    │ │ Engine              │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↕                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              COUCHE INTÉGRATION & DONNÉES                  │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │ API         │ │ Message     │ │ Data Lake           │  │ │
│  │  │ Gateway     │ │ Queue       │ │ & Warehouse         │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↕                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                COUCHE INFRASTRUCTURE                       │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │ │
│  │  │ Container   │ │ Monitoring  │ │ Security &          │  │ │
│  │  │ Platform    │ │ & Logging   │ │ Identity            │  │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Microservices

#### Services Core Métier
```yaml
# Configuration architecture microservices
services:
  # Service Orchestrateur Principal
  orchestrator-service:
    image: perplexity-orchestrator:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=${POSTGRES_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    resources:
      limits:
        cpu: "1000m"
        memory: "2Gi"
      requests:
        cpu: "500m"
        memory: "1Gi"
    
  # Service Exécution Python
  python-executor:
    image: perplexity-python-executor:latest
    ports:
      - "8081:8080"
    environment:
      - SANDBOX_TYPE=container
      - MAX_EXECUTION_TIME=300
      - MAX_MEMORY=1024m
    volumes:
      - ./sandbox-storage:/app/sandbox
    security_opt:
      - seccomp:unconfined
    
  # Service Gestion APIs
  api-gateway:
    image: perplexity-api-gateway:latest
    ports:
      - "8000:8080"
    environment:
      - RATE_LIMIT_GLOBAL=1000
      - CACHE_TTL_DEFAULT=300
    depends_on:
      - redis
      - postgres
    
  # Service Analytics & Monitoring
  analytics-service:
    image: perplexity-analytics:latest
    ports:
      - "8082:8080"
    environment:
      - METRICS_RETENTION_DAYS=90
      - ALERTING_ENABLED=true
    
  # Bases de données
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: perplexity_metier
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    
  # Message Queue
  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: ${MQ_USER}
      RABBITMQ_DEFAULT_PASS: ${MQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
```

### Modèle de Données

#### Schéma Base de Données Principal
```sql
-- Schéma PostgreSQL pour l'espace métier

-- Table des utilisateurs et rôles
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user_metier',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Index pour optimisation
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

-- Table des espaces métier
CREATE TABLE business_spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    business_type VARCHAR(100), -- 'pricing', 'booking', 'music', etc.
    configuration JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des scripts Python
CREATE TABLE python_scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    author_id UUID REFERENCES users(id),
    space_id UUID REFERENCES business_spaces(id),
    code TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'validated', 'deprecated'
    metadata JSONB,
    dependencies JSONB, -- Liste des librairies
    resource_requirements JSONB, -- CPU, mémoire, timeout
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour recherche performante
CREATE INDEX idx_scripts_space_id ON python_scripts(space_id);
CREATE INDEX idx_scripts_author ON python_scripts(author_id);
CREATE INDEX idx_scripts_status ON python_scripts(status);

-- Table historique exécutions
CREATE TABLE script_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID REFERENCES python_scripts(id),
    executor_id UUID REFERENCES users(id),
    space_id UUID REFERENCES business_spaces(id),
    status VARCHAR(50) NOT NULL, -- 'running', 'completed', 'failed'
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    resource_usage JSONB, -- CPU, mémoire utilisés
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Partitionnement par mois pour performance
CREATE TABLE script_executions_y2025m09 PARTITION OF script_executions
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

-- Table des règles métier
CREATE TABLE business_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    space_id UUID REFERENCES business_spaces(id),
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(100), -- 'pricing', 'validation', 'alert'
    condition_logic JSONB NOT NULL,
    action_logic JSONB NOT NULL,
    priority INTEGER DEFAULT 1,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des intégrations API
CREATE TABLE api_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    space_id UUID REFERENCES business_spaces(id),
    name VARCHAR(255) NOT NULL,
    endpoint_url VARCHAR(500) NOT NULL,
    auth_type VARCHAR(50), -- 'api_key', 'oauth2', 'basic'
    auth_credentials BYTEA, -- Chiffré
    rate_limit INTEGER,
    cache_ttl INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    last_health_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table métriques et monitoring
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(100) NOT NULL,
    space_id UUID REFERENCES business_spaces(id),
    metric_data JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Partitionnement par jour pour métriques
CREATE TABLE system_metrics_y2025m09d02 PARTITION OF system_metrics
    FOR VALUES FROM ('2025-09-02') TO ('2025-09-03');

-- Table audit trail
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    space_id UUID REFERENCES business_spaces(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Index pour requêtes d'audit
CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_action ON audit_log(action);
```

#### Modèle de Données NoSQL (MongoDB/DocumentDB)
```javascript
// Collection: business_workflows
{
  "_id": ObjectId("..."),
  "space_id": "uuid",
  "workflow_name": "string",
  "version": "1.0",
  "steps": [
    {
      "step_id": "string",
      "step_type": "python_script | api_call | decision",
      "configuration": {
        "script_id": "uuid",
        "timeout": 300,
        "retry_count": 3
      },
      "dependencies": ["step1", "step2"],
      "error_handling": "continue | stop | retry"
    }
  ],
  "triggers": {
    "schedule": "0 9 * * *", // Cron
    "events": ["price_change", "stock_low"],
    "manual": true
  },
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}

// Collection: execution_contexts
{
  "_id": ObjectId("..."),
  "execution_id": "uuid",
  "workflow_id": "uuid", 
  "current_step": "string",
  "context_data": {
    "variables": {
      "product_id": "PROD123",
      "current_price": 99.99
    },
    "intermediate_results": {
      "step1_output": {...}
    }
  },
  "status": "running | completed | failed",
  "started_at": ISODate("..."),
  "updated_at": ISODate("...")
}

// Collection: cached_api_responses
{
  "_id": ObjectId("..."),
  "cache_key": "md5_hash",
  "endpoint_name": "string",
  "request_params": {...},
  "response_data": {...},
  "cached_at": ISODate("..."),
  "expires_at": ISODate("..."),
  "hit_count": 0
}
```

### Architecture Sécurité

#### Modèle de Sécurité Zero Trust
```yaml
# Configuration sécurité
security:
  authentication:
    providers:
      - name: "azure_ad"
        type: "saml"
        config:
          entity_id: "urn:perplexity:metier"
          sso_url: "https://login.microsoftonline.com/..."
          certificate: "${SAML_CERT}"
      
      - name: "internal_oauth2"
        type: "oauth2"
        config:
          issuer: "https://auth.perplexity.com"
          client_id: "${OAUTH_CLIENT_ID}"
          client_secret: "${OAUTH_CLIENT_SECRET}"
  
  authorization:
    model: "rbac" # Role-Based Access Control
    roles:
      user_metier:
        permissions:
          - "scripts:execute:approved"
          - "data:read:own"
          - "reports:create"
        resource_limits:
          max_script_execution_time: 30
          max_memory_mb: 512
          concurrent_executions: 2
      
      expert_metier:
        inherits: ["user_metier"]
        permissions:
          - "scripts:create"
          - "scripts:modify:own"
          - "workflows:manage"
          - "integrations:configure"
        resource_limits:
          max_script_execution_time: 300
          max_memory_mb: 2048
          concurrent_executions: 5
      
      admin:
        permissions:
          - "*" # Tous droits
        resource_limits:
          max_script_execution_time: 1800
          max_memory_mb: 8192
          concurrent_executions: 10
  
  data_protection:
    encryption:
      at_rest:
        algorithm: "AES-256-GCM"
        key_rotation_days: 90
      in_transit:
        min_tls_version: "1.3"
        cipher_suites: ["TLS_AES_256_GCM_SHA384"]
    
    data_classification:
      levels:
        - "public"
        - "internal" 
        - "confidential"
        - "restricted"
      
      policies:
        confidential:
          - "encrypt_at_rest"
          - "audit_all_access"
          - "restrict_export"
        restricted:
          - "encrypt_at_rest"
          - "encrypt_in_memory"
          - "require_mfa"
          - "geo_restrict"
  
  network:
    firewall:
      ingress:
        - port: 443
          protocol: "HTTPS"
          sources: ["0.0.0.0/0"]
        - port: 8080
          protocol: "HTTP"
          sources: ["10.0.0.0/8"] # Internal only
      
      egress:
        - destinations: ["api.partner1.com"]
          ports: [443]
          protocol: "HTTPS"
        - destinations: ["*.googleapis.com"]
          ports: [443]
          protocol: "HTTPS"
    
    vpn:
      required_for:
        - "admin_access"
        - "production_deployment"
      provider: "wireguard"
```

### Architecture Performance et Scalabilité

#### Stratégie de Mise à l'Échelle
```yaml
# Configuration auto-scaling Kubernetes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orchestrator
  template:
    metadata:
      labels:
        app: orchestrator
    spec:
      containers:
      - name: orchestrator
        image: perplexity-orchestrator:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orchestrator-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orchestrator-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### Architecture Cache Multi-Niveaux
```python
# Configuration cache intelligent
class MultiLevelCache:
    """Cache multi-niveaux pour optimisation performance"""
    
    def __init__(self):
        # Niveau 1: Cache in-memory (très rapide, petite taille)
        self.l1_cache = {}  # Dict Python simple
        self.l1_max_size = 1000
        self.l1_ttl = 60  # 1 minute
        
        # Niveau 2: Redis (rapide, taille moyenne)
        self.l2_cache = redis.Redis(host='redis-cache', port=6379)
        self.l2_default_ttl = 300  # 5 minutes
        
        # Niveau 3: Base de données (lent, grande taille)
        self.l3_cache = self._connect_db()
        self.l3_default_ttl = 3600  # 1 heure
    
    def get(self, key: str) -> Optional[Any]:
        """Récupération avec cascade de cache"""
        # Tentative L1
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            if entry['expires'] > time.time():
                return entry['data']
            else:
                del self.l1_cache[key]
        
        # Tentative L2
        try:
            l2_data = self.l2_cache.get(f"l2:{key}")
            if l2_data:
                data = json.loads(l2_data.decode())
                # Promotion vers L1
                self._set_l1(key, data, self.l1_ttl)
                return data
        except Exception:
            pass
        
        # Tentative L3
        try:
            l3_data = self._get_from_db(key)
            if l3_data:
                # Promotion vers L2 et L1
                self._set_l2(key, l3_data, self.l2_default_ttl)
                self._set_l1(key, l3_data, self.l1_ttl)
                return l3_data
        except Exception:
            pass
        
        return None
    
    def set(self, key: str, data: Any, ttl: int = None) -> None:
        """Mise à jour tous niveaux"""
        ttl = ttl or self.l2_default_ttl
        
        # Stockage L1
        self._set_l1(key, data, min(ttl, self.l1_ttl))
        
        # Stockage L2
        self._set_l2(key, data, ttl)
        
        # Stockage L3 (async pour performance)
        self._async_set_l3(key, data, ttl)
    
    def _set_l1(self, key: str, data: Any, ttl: int) -> None:
        """Stockage cache L1 avec éviction LRU"""
        if len(self.l1_cache) >= self.l1_max_size:
            # Éviction du plus ancien
            oldest_key = min(self.l1_cache.keys(), 
                           key=lambda k: self.l1_cache[k]['accessed'])
            del self.l1_cache[oldest_key]
        
        self.l1_cache[key] = {
            'data': data,
            'expires': time.time() + ttl,
            'accessed': time.time()
        }
    
    def _set_l2(self, key: str, data: Any, ttl: int) -> None:
        """Stockage cache L2 Redis"""
        try:
            serialized = json.dumps(data, default=str)
            self.l2_cache.setex(f"l2:{key}", ttl, serialized)
        except Exception as e:
            logger.warning(f"Erreur cache L2: {e}")
```

### Architecture Observabilité

#### Configuration Monitoring Complet
```yaml
# Configuration Prometheus + Grafana
monitoring:
  prometheus:
    scrape_configs:
      - job_name: 'orchestrator'
        static_configs:
          - targets: ['orchestrator-service:8080']
        metrics_path: '/metrics'
        scrape_interval: 15s
      
      - job_name: 'python-executor'
        static_configs:
          - targets: ['python-executor:8080']
        metrics_path: '/metrics'
        scrape_interval: 15s
    
    alerting_rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreur élevé détecté"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Temps de réponse élevé"
  
  grafana:
    dashboards:
      business_metrics:
        panels:
          - title: "Scripts Exécutés par Heure"
            type: "graph"
            targets:
              - expr: "rate(script_executions_total[1h])"
          
          - title: "Taux de Succès Exécutions"
            type: "stat"
            targets:
              - expr: "script_executions_success_rate"
          
          - title: "Top Utilisateurs Actifs"
            type: "table"
            targets:
              - expr: "topk(10, sum by (user_id) (user_activity_total))"
      
      technical_metrics:
        panels:
          - title: "Utilisation CPU par Service"
            type: "graph"
            targets:
              - expr: "rate(cpu_usage_seconds_total[5m]) by (service)"
          
          - title: "Utilisation Mémoire"
            type: "graph" 
            targets:
              - expr: "memory_usage_bytes by (service)"
  
  logging:
    structured: true
    format: "json"
    level: "info"
    fields:
      - "timestamp"
      - "level"
      - "service"
      - "user_id"
      - "space_id"
      - "request_id"
      - "message"
    
    aggregation:
      tool: "elasticsearch"
      retention_days: 90
      indices:
        - pattern: "logs-application-*"
          policy: "hot-warm-cold"
        - pattern: "logs-audit-*"
          policy: "hot-cold"
          retention_days: 2555  # 7 ans pour conformité
```

### Patterns d'Architecture

#### Event Sourcing pour Traçabilité
```python
from dataclasses import dataclass
from typing import List, Any
from datetime import datetime
import json

@dataclass
class DomainEvent:
    """Événement métier de base"""
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    user_id: str
    version: int

class EventStore:
    """Store d'événements pour Event Sourcing"""
    
    def __init__(self, connection):
        self.connection = connection
        self._setup_event_store()
    
    def _setup_event_store(self):
        """Initialise le schema event store"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS event_store (
            event_id UUID PRIMARY KEY,
            event_type VARCHAR(255) NOT NULL,
            aggregate_id UUID NOT NULL,
            aggregate_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            user_id UUID NOT NULL,
            version INTEGER NOT NULL,
            UNIQUE(aggregate_id, version)
        );
        
        CREATE INDEX IF NOT EXISTS idx_event_store_aggregate 
            ON event_store(aggregate_id, version);
        CREATE INDEX IF NOT EXISTS idx_event_store_type 
            ON event_store(event_type);
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(create_table_sql)
    
    def append_event(self, event: DomainEvent) -> None:
        """Ajoute un événement au store"""
        insert_sql = """
        INSERT INTO event_store 
        (event_id, event_type, aggregate_id, aggregate_type, 
         event_data, timestamp, user_id, version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(insert_sql, (
                event.event_id,
                event.event_type,
                event.aggregate_id,
                event.aggregate_type,
                json.dumps(event.event_data),
                event.timestamp,
                event.user_id,
                event.version
            ))
        
        self.connection.commit()
    
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[DomainEvent]:
        """Récupère événements pour un agrégat"""
        select_sql = """
        SELECT event_id, event_type, aggregate_id, aggregate_type,
               event_data, timestamp, user_id, version
        FROM event_store 
        WHERE aggregate_id = %s AND version > %s
        ORDER BY version ASC
        """
        
        events = []
        with self.connection.cursor() as cursor:
            cursor.execute(select_sql, (aggregate_id, from_version))
            
            for row in cursor.fetchall():
                events.append(DomainEvent(
                    event_id=row[0],
                    event_type=row[1],
                    aggregate_id=row[2],
                    aggregate_type=row[3],
                    event_data=json.loads(row[4]),
                    timestamp=row[5],
                    user_id=row[6],
                    version=row[7]
                ))
        
        return events

# Exemple événements métier
class ScriptExecutionEvents:
    """Événements liés à l'exécution de scripts"""
    
    @staticmethod
    def script_execution_started(script_id: str, user_id: str, input_data: Dict) -> DomainEvent:
        return DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type="ScriptExecutionStarted",
            aggregate_id=script_id,
            aggregate_type="PythonScript",
            event_data={
                "input_data": input_data,
                "started_by": user_id
            },
            timestamp=datetime.now(),
            user_id=user_id,
            version=1
        )
    
    @staticmethod
    def script_execution_completed(script_id: str, user_id: str, 
                                 output_data: Dict, execution_time_ms: int) -> DomainEvent:
        return DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type="ScriptExecutionCompleted", 
            aggregate_id=script_id,
            aggregate_type="PythonScript",
            event_data={
                "output_data": output_data,
                "execution_time_ms": execution_time_ms,
                "success": True
            },
            timestamp=datetime.now(),
            user_id=user_id,
            version=2
        )
```

#### CQRS (Command Query Responsibility Segregation)
```python
from abc import ABC, abstractmethod

class Command(ABC):
    """Commande de base"""
    pass

class Query(ABC):
    """Requête de base"""
    pass

class CommandHandler(ABC):
    """Handler de commande"""
    
    @abstractmethod
    def handle(self, command: Command) -> Any:
        pass

class QueryHandler(ABC):
    """Handler de requête"""
    
    @abstractmethod
    def handle(self, query: Query) -> Any:
        pass

# Commandes métier
@dataclass
class CreateScriptCommand(Command):
    name: str
    code: str
    author_id: str
    space_id: str
    metadata: Dict[str, Any]

@dataclass
class ExecuteScriptCommand(Command):
    script_id: str
    executor_id: str
    input_data: Dict[str, Any]

# Requêtes métier  
@dataclass
class GetScriptsBySpaceQuery(Query):
    space_id: str
    user_id: str
    limit: int = 50
    offset: int = 0

@dataclass
class GetScriptExecutionHistoryQuery(Query):
    script_id: str
    user_id: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

# Handlers
class CreateScriptCommandHandler(CommandHandler):
    """Handler création script"""
    
    def __init__(self, event_store: EventStore, repository):
        self.event_store = event_store
        self.repository = repository
    
    def handle(self, command: CreateScriptCommand) -> str:
        # Validation métier
        if not self._validate_script_name(command.name):
            raise ValueError("Nom de script invalide")
        
        # Création agrégat
        script_id = str(uuid.uuid4())
        
        # Événement métier
        event = DomainEvent(
            event_id=str(uuid.uuid4()),
            event_type="ScriptCreated",
            aggregate_id=script_id,
            aggregate_type="PythonScript",
            event_data={
                "name": command.name,
                "code": command.code,
                "author_id": command.author_id,
                "space_id": command.space_id,
                "metadata": command.metadata
            },
            timestamp=datetime.now(),
            user_id=command.author_id,
            version=1
        )
        
        # Persistance
        self.event_store.append_event(event)
        
        return script_id

class GetScriptsBySpaceQueryHandler(QueryHandler):
    """Handler requête scripts par espace"""
    
    def __init__(self, read_model_db):
        self.read_model_db = read_model_db
    
    def handle(self, query: GetScriptsBySpaceQuery) -> List[Dict[str, Any]]:
        # Requête optimisée sur modèle de lecture
        sql = """
        SELECT s.id, s.name, s.description, s.status,
               s.created_at, u.username as author_name
        FROM scripts_read_model s
        JOIN users u ON s.author_id = u.id
        WHERE s.space_id = %s 
        AND s.status != 'deleted'
        ORDER BY s.updated_at DESC
        LIMIT %s OFFSET %s
        """
        
        with self.read_model_db.cursor() as cursor:
            cursor.execute(sql, (query.space_id, query.limit, query.offset))
            return [dict(row) for row in cursor.fetchall()]

# Bus de commandes et requêtes
class MessageBus:
    """Bus centralisé pour commands et queries"""
    
    def __init__(self):
        self.command_handlers: Dict[type, CommandHandler] = {}
        self.query_handlers: Dict[type, QueryHandler] = {}
    
    def register_command_handler(self, command_type: type, handler: CommandHandler):
        self.command_handlers[command_type] = handler
    
    def register_query_handler(self, query_type: type, handler: QueryHandler):
        self.query_handlers[query_type] = handler
    
    def send_command(self, command: Command) -> Any:
        handler = self.command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"Pas de handler pour {type(command)}")
        
        return handler.handle(command)
    
    def send_query(self, query: Query) -> Any:
        handler = self.query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"Pas de handler pour {type(query)}")
        
        return handler.handle(query)
```

Cette architecture modulaire et scalable permet à l'espace métier Perplexity AI de gérer efficacement la croissance, maintenir les performances et assurer la traçabilité complète des opérations métier.