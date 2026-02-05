# Procédures CI/CD - Espace Métier Perplexity AI

## Vue d'ensemble
Ce document détaille les processus d'intégration continue et de déploiement continu (CI/CD) pour l'espace métier Perplexity AI, incluant les pipelines, l'automatisation, les tests et les stratégies de déploiement.

## Stratégie CI/CD Globale

### Philosophie DevOps

#### Principes Directeurs
- **Infrastructure as Code** : Toute l'infrastructure versionnée et reproductible
- **Déploiement Automatisé** : Zéro intervention manuelle pour les déploiements
- **Testing First** : Tests automatisés à chaque étape
- **Monitoring Continu** : Observabilité intégrée dès le développement
- **Rollback Rapide** : Capacité de retour arrière en moins de 5 minutes

#### Architecture Pipeline
```
┌─────────────────────────────────────────────────────────────────┐
│                      PIPELINE CI/CD                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Code Push → Build → Test → Security → Deploy → Monitor        │
│      ↓         ↓      ↓        ↓        ↓        ↓             │
│   GitHub   Docker  Unit    SAST/     K8s     Prometheus        │
│  Actions   Build   Tests    DAST    Deploy    Grafana          │
│                                                                 │
│  Environments: DEV → STAGING → PROD                            │
│  Gates:       Auto    Manual    Auto (with approval)          │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration Repository Structure

#### Organisation Git Repository
```
perplexity-metier/
├── .github/
│   ├── workflows/
│   │   ├── ci-pipeline.yml
│   │   ├── cd-pipeline.yml  
│   │   ├── security-scan.yml
│   │   └── release.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── src/
│   ├── orchestrator/
│   ├── python-executor/
│   ├── api-gateway/
│   └── analytics/
├── infrastructure/
│   ├── terraform/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── prod/
│   │   ├── modules/
│   │   └── shared/
│   ├── kubernetes/
│   │   ├── base/
│   │   ├── overlays/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── prod/
│   └── helm/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── performance/
│   └── security/
├── docs/
├── scripts/
└── docker/
```

### Pipeline de Build et Tests

#### Configuration GitHub Actions - CI Pipeline
```yaml
# .github/workflows/ci-pipeline.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  code-quality:
    name: Code Quality & Security
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
        pip install black flake8 mypy bandit safety
    
    - name: Code formatting check
      run: black --check --diff src/
    
    - name: Linting
      run: flake8 src/ --max-line-length=88 --exclude=migrations/
    
    - name: Type checking
      run: mypy src/ --ignore-missing-imports
    
    - name: Security scan - Bandit
      run: bandit -r src/ -f json -o bandit-report.json
    
    - name: Dependency vulnerability scan
      run: safety check --json --output safety-report.json
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json

  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: code-quality
    
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ \
          --cov=src/ \
          --cov-report=xml \
          --cov-report=html \
          --junitxml=test-results.xml \
          --cov-fail-under=80
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.python-version }}
        path: |
          test-results.xml
          htmlcov/

  integration-tests:
    name: Integration Tests  
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
    
    - name: Run database migrations
      env:
        DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_db
      run: |
        python manage.py migrate
    
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://postgres:testpass@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest tests/integration/ \
          --junitxml=integration-test-results.xml \
          -v
    
    - name: Upload integration test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: integration-test-results
        path: integration-test-results.xml

  build-images:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    
    strategy:
      matrix:
        service: [orchestrator, python-executor, api-gateway, analytics]
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./docker/Dockerfile.${{ matrix.service }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        platforms: linux/amd64,linux/arm64

  security-scan:
    name: Container Security Scan
    runs-on: ubuntu-latest
    needs: build-images
    
    strategy:
      matrix:
        service: [orchestrator, python-executor, api-gateway, analytics]
    
    steps:
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: '${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service }}:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-results-${{ matrix.service }}.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results-${{ matrix.service }}.sarif'

  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    needs: build-images
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup K6
      run: |
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    
    - name: Start test environment
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30
    
    - name: Run performance tests
      run: |
        k6 run tests/performance/load-test.js \
          --out json=performance-results.json \
          --summary-trend-stats="min,med,avg,p(95),p(99),max"
    
    - name: Upload performance results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: performance-results.json
    
    - name: Cleanup test environment
      if: always()
      run: docker-compose -f docker-compose.test.yml down
```

#### Pipeline de Déploiement CD
```yaml
# .github/workflows/cd-pipeline.yml
name: CD Pipeline

on:
  workflow_run:
    workflows: ["CI Pipeline"]
    branches: [main]
    types: [completed]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy-dev:
    name: Deploy to Development
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    environment: development
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: 1.5.0
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: eu-west-1
    
    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region eu-west-1 --name perplexity-dev-cluster
    
    - name: Deploy infrastructure
      run: |
        cd infrastructure/terraform/environments/dev
        terraform init
        terraform plan -out=tfplan
        terraform apply tfplan
    
    - name: Deploy to Kubernetes
      run: |
        cd infrastructure/kubernetes
        kubectl apply -k overlays/dev/
        
        # Update images avec les nouvelles versions
        kubectl set image deployment/orchestrator \
          orchestrator=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-orchestrator:${{ github.sha }} \
          -n perplexity-dev
        
        kubectl set image deployment/python-executor \
          python-executor=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-python-executor:${{ github.sha }} \
          -n perplexity-dev
    
    - name: Wait for deployment
      run: |
        kubectl rollout status deployment/orchestrator -n perplexity-dev --timeout=300s
        kubectl rollout status deployment/python-executor -n perplexity-dev --timeout=300s
    
    - name: Run smoke tests
      run: |
        kubectl run smoke-test --rm -i --restart=Never \
          --image=curlimages/curl \
          -- curl -f http://orchestrator-service.perplexity-dev.svc.cluster.local:8080/health

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: deploy-dev
    environment: staging
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Setup tools
      uses: ./.github/actions/setup-deployment-tools
    
    - name: Deploy to staging
      run: |
        cd infrastructure/terraform/environments/staging
        terraform init
        terraform plan -out=tfplan
        terraform apply tfplan
        
        cd ../../../kubernetes
        kubectl apply -k overlays/staging/
        
        # Blue-Green deployment pour staging
        kubectl patch deployment orchestrator \
          -p '{"spec":{"template":{"spec":{"containers":[{"name":"orchestrator","image":"'${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-orchestrator:${{ github.sha }}'"}]}}}}' \
          -n perplexity-staging
    
    - name: Run integration tests against staging
      run: |
        cd tests/integration
        python -m pytest \
          --base-url=https://staging.perplexity.ai \
          --junitxml=staging-test-results.xml

  deploy-prod:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Setup tools
      uses: ./.github/actions/setup-deployment-tools
    
    - name: Create release
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: v${{ github.run_number }}
        release_name: Release v${{ github.run_number }}
        draft: false
        prerelease: false
    
    - name: Deploy to production with canary
      run: |
        cd infrastructure/terraform/environments/prod
        terraform init
        terraform plan -out=tfplan
        terraform apply tfplan
        
        # Déploiement canary (10% du trafic)
        cd ../../../kubernetes
        kubectl apply -f canary-deployment.yaml
        
        # Attendre validation métriques
        sleep 300
        
        # Si OK, déploiement complet
        kubectl apply -k overlays/prod/
    
    - name: Verify production deployment
      run: |
        # Health checks
        curl -f https://api.perplexity.ai/health
        
        # Tests de fumée production
        cd tests/smoke
        python -m pytest --base-url=https://api.perplexity.ai
    
    - name: Rollback on failure
      if: failure()
      run: |
        kubectl rollout undo deployment/orchestrator -n perplexity-prod
        kubectl rollout undo deployment/python-executor -n perplexity-prod
```

### Infrastructure as Code

#### Configuration Terraform
```hcl
# infrastructure/terraform/environments/prod/main.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }
  
  backend "s3" {
    bucket         = "perplexity-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = "production"
      Project     = "perplexity-metier"
      ManagedBy   = "terraform"
    }
  }
}

# EKS Cluster
module "eks" {
  source = "../../modules/eks"
  
  cluster_name     = "perplexity-prod"
  cluster_version  = "1.28"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  node_groups = {
    main = {
      instance_types = ["m5.xlarge"]
      min_size      = 3
      max_size      = 10
      desired_size  = 5
      
      k8s_labels = {
        "workload-type" = "general"
      }
    }
    
    python_executor = {
      instance_types = ["c5.2xlarge"]
      min_size      = 2
      max_size      = 20
      desired_size  = 5
      
      k8s_labels = {
        "workload-type" = "python-executor"
      }
      
      taints = {
        "python-executor" = {
          key    = "workload-type"
          value  = "python-executor"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier = "perplexity-prod-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  
  allocated_storage     = 500
  max_allocated_storage = 2000
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = "perplexity_prod"
  username = "perplexity"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"
  
  performance_insights_enabled = true
  monitoring_interval         = 60
  
  skip_final_snapshot = false
  final_snapshot_identifier = "perplexity-prod-db-final-snapshot"
  
  tags = {
    Name = "perplexity-prod-database"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "perplexity-prod-cache-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "perplexity-prod-redis"
  description               = "Redis cluster for Perplexity production"
  
  node_type                 = "cache.r6g.xlarge"
  port                      = 6379
  parameter_group_name      = "default.redis7"
  
  num_cache_clusters        = 3
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  snapshot_retention_limit = 7
  snapshot_window         = "03:00-05:00"
  
  tags = {
    Name = "perplexity-prod-redis"
  }
}

# S3 pour stockage artefacts
resource "aws_s3_bucket" "artifacts" {
  bucket = "perplexity-prod-artifacts"
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  default     = "eu-west-1"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}
```

#### Configuration Kubernetes avec Kustomize
```yaml
# infrastructure/kubernetes/base/orchestrator/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator
  labels:
    app: orchestrator
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orchestrator
      version: v1
  template:
    metadata:
      labels:
        app: orchestrator
        version: v1
    spec:
      serviceAccountName: orchestrator
      containers:
      - name: orchestrator
        image: ghcr.io/company/perplexity-metier-orchestrator:latest
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8090
          name: metrics
        
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
        
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1001
          capabilities:
            drop:
            - ALL
          seccompProfile:
            type: RuntimeDefault

---
# infrastructure/kubernetes/overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: perplexity-prod

replicas:
- name: orchestrator
  count: 5
- name: python-executor
  count: 8
- name: api-gateway
  count: 3

images:
- name: ghcr.io/company/perplexity-metier-orchestrator
  newTag: v1.0.0
- name: ghcr.io/company/perplexity-metier-python-executor
  newTag: v1.0.0

patchesStrategicMerge:
- production-resources.yaml
- production-hpa.yaml

configMapGenerator:
- name: app-config
  literals:
  - ENVIRONMENT=production
  - LOG_LEVEL=INFO
  - METRICS_ENABLED=true

secretGenerator:
- name: database-secret
  literals:
  - url=postgresql://user:pass@prod-db:5432/perplexity
- name: redis-secret
  literals:
  - url=redis://prod-redis:6379/0
```

### Monitoring et Observabilité CI/CD

#### Configuration Prometheus pour CI/CD
```yaml
# infrastructure/monitoring/prometheus/rules/cicd.yaml
groups:
- name: cicd.rules
  rules:
  
  # Métriques déploiements
  - alert: DeploymentFailure
    expr: increase(deployment_failures_total[5m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Échec de déploiement détecté"
      description: "Un déploiement a échoué dans l'environnement {{ $labels.environment }}"
  
  - alert: HighDeploymentDuration
    expr: deployment_duration_seconds > 1800 # 30 minutes
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Déploiement anormalement long"
      description: "Le déploiement prend plus de 30 minutes dans {{ $labels.environment }}"
  
  # Métriques qualité code
  - alert: LowCodeCoverage
    expr: code_coverage_percentage < 80
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Couverture de code insuffisante"
      description: "La couverture de code est de {{ $value }}% (< 80%)"
  
  - alert: SecurityVulnerabilities
    expr: security_vulnerabilities_critical > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Vulnérabilités critiques détectées"
      description: "{{ $value }} vulnérabilités critiques trouvées dans le code"
  
  # Métriques performance
  - alert: PerformanceRegression
    expr: |
      (
        avg_over_time(api_response_time_p95[1h]) - 
        avg_over_time(api_response_time_p95[1h] offset 24h)
      ) > 500 # 500ms de dégradation
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Régression de performance détectée"
      description: "Le temps de réponse P95 a augmenté de {{ $value }}ms"
```

#### Dashboard Grafana CI/CD
```json
{
  "dashboard": {
    "title": "CI/CD Pipeline Dashboard",
    "panels": [
      {
        "title": "Déploiements par Environnement",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(deployments_total[24h])) by (environment)",
            "legendFormat": "{{ environment }}"
          }
        ]
      },
      {
        "title": "Taux de Succès des Déploiements",
        "type": "gauge",
        "targets": [
          {
            "expr": "sum(rate(deployments_success_total[24h])) / sum(rate(deployments_total[24h])) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "min": 0,
            "max": 100,
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 90},
                {"color": "green", "value": 95}
              ]
            }
          }
        }
      },
      {
        "title": "Durée Moyenne des Déploiements",
        "type": "timeseries",
        "targets": [
          {
            "expr": "avg(deployment_duration_seconds) by (environment)",
            "legendFormat": "{{ environment }}"
          }
        ]
      },
      {
        "title": "Couverture de Code",
        "type": "stat",
        "targets": [
          {
            "expr": "code_coverage_percentage"
          }
        ]
      }
    ]
  }
}
```

### Scripts d'Automatisation

#### Script de Rollback Automatique
```bash
#!/bin/bash
# scripts/rollback.sh

set -euo pipefail

ENVIRONMENT=${1:-staging}
NAMESPACE="perplexity-${ENVIRONMENT}"
TIMEOUT=${2:-300}

echo "🔄 Début rollback environnement: ${ENVIRONMENT}"

# Fonction de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Vérification prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    if ! command -v kubectl &> /dev/null; then
        log "❌ kubectl non trouvé"
        exit 1
    fi
    
    if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        log "❌ Namespace ${NAMESPACE} non trouvé"
        exit 1
    fi
    
    log "✅ Prérequis OK"
}

# Rollback des déploiements
rollback_deployments() {
    log "Rollback des déploiements..."
    
    deployments=$(kubectl get deployments -n "${NAMESPACE}" -o name)
    
    for deployment in $deployments; do
        log "Rollback ${deployment}..."
        
        if kubectl rollout undo "${deployment}" -n "${NAMESPACE}"; then
            log "✅ Rollback ${deployment} initié"
        else
            log "❌ Échec rollback ${deployment}"
            return 1
        fi
    done
}

# Attente stabilisation
wait_for_rollout() {
    log "Attente stabilisation des déploiements..."
    
    deployments=$(kubectl get deployments -n "${NAMESPACE}" -o name)
    
    for deployment in $deployments; do
        log "Attente ${deployment}..."
        
        if kubectl rollout status "${deployment}" -n "${NAMESPACE}" --timeout="${TIMEOUT}s"; then
            log "✅ ${deployment} stable"
        else
            log "❌ ${deployment} non stable après ${TIMEOUT}s"
            return 1
        fi
    done
}

# Health checks
run_health_checks() {
    log "Vérification santé des services..."
    
    services=("orchestrator" "python-executor" "api-gateway")
    
    for service in "${services[@]}"; do
        log "Health check ${service}..."
        
        if kubectl run health-check-${service} \
            --rm -i --restart=Never \
            --image=curlimages/curl \
            -- curl -f "http://${service}-service.${NAMESPACE}.svc.cluster.local:8080/health"; then
            log "✅ ${service} healthy"
        else
            log "❌ ${service} non healthy"
            return 1
        fi
    done
}

# Notification
send_notification() {
    local status=$1
    local message="Rollback ${ENVIRONMENT}: ${status}"
    
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST "${SLACK_WEBHOOK_URL}" \
            -H 'Content-type: application/json' \
            --data "{\"text\":\"${message}\"}"
    fi
    
    log "📢 Notification envoyée: ${message}"
}

# Main
main() {
    log "🚀 Début rollback automatique"
    
    check_prerequisites
    
    if rollback_deployments && wait_for_rollout && run_health_checks; then
        log "✅ Rollback réussi"
        send_notification "SUCCESS"
        exit 0
    else
        log "❌ Rollback échoué"
        send_notification "FAILED"
        exit 1
    fi
}

# Gestion signaux
trap 'log "Script interrompu"; exit 130' INT TERM

main "$@"
```

#### Script de Release Automatique
```python
#!/usr/bin/env python3
# scripts/release.py
"""
Script de release automatique
Gère versioning, changelog, et déploiement
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime
from pathlib import Path

class ReleaseManager:
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.version_file = self.project_root / "VERSION"
        self.changelog_file = self.project_root / "CHANGELOG.md"
    
    def get_current_version(self) -> str:
        """Récupère version actuelle"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "0.0.0"
    
    def bump_version(self, bump_type: str = "patch") -> str:
        """Incrémente version selon type (major, minor, patch)"""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        self.version_file.write_text(new_version)
        
        print(f"📈 Version: {current} → {new_version}")
        return new_version
    
    def generate_changelog(self, version: str) -> None:
        """Génère changelog depuis commits Git"""
        print("📝 Génération changelog...")
        
        # Récupère commits depuis dernier tag
        try:
            last_tag = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                text=True
            ).strip()
            commit_range = f"{last_tag}..HEAD"
        except subprocess.CalledProcessError:
            commit_range = "HEAD"
        
        # Récupère liste commits
        commits = subprocess.check_output([
            "git", "log", commit_range,
            "--pretty=format:%H|%s|%an|%ad",
            "--date=short"
        ], text=True).strip().split('\n')
        
        if not commits or commits == ['']:
            print("⚠️  Aucun nouveau commit trouvé")
            return
        
        # Parse commits par catégorie
        features = []
        fixes = []
        others = []
        
        for commit in commits:
            if '|' not in commit:
                continue
                
            hash_commit, subject, author, date = commit.split('|', 3)
            
            if subject.startswith('feat'):
                features.append(f"- {subject} ({hash_commit[:8]})")
            elif subject.startswith('fix'):
                fixes.append(f"- {subject} ({hash_commit[:8]})")
            else:
                others.append(f"- {subject} ({hash_commit[:8]})")
        
        # Génère entrée changelog
        changelog_entry = f"""
## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

"""
        
        if features:
            changelog_entry += "### ✨ Nouvelles Fonctionnalités\n"
            changelog_entry += '\n'.join(features) + '\n\n'
        
        if fixes:
            changelog_entry += "### 🐛 Corrections\n"
            changelog_entry += '\n'.join(fixes) + '\n\n'
        
        if others:
            changelog_entry += "### 🔧 Autres\n"
            changelog_entry += '\n'.join(others) + '\n\n'
        
        # Met à jour CHANGELOG.md
        if self.changelog_file.exists():
            current_changelog = self.changelog_file.read_text()
            # Insère nouvelle entrée après header
            lines = current_changelog.split('\n')
            header_end = 0
            for i, line in enumerate(lines):
                if line.startswith('## ['):
                    header_end = i
                    break
            
            new_changelog = '\n'.join(lines[:header_end]) + changelog_entry + '\n'.join(lines[header_end:])
        else:
            new_changelog = f"# Changelog\n{changelog_entry}"
        
        self.changelog_file.write_text(new_changelog)
        print(f"✅ Changelog mis à jour: {len(features + fixes + others)} commits")
    
    def create_git_tag(self, version: str) -> None:
        """Crée tag Git pour la version"""
        print(f"🏷️  Création tag v{version}...")
        
        subprocess.run([
            "git", "add", str(self.version_file), str(self.changelog_file)
        ], check=True)
        
        subprocess.run([
            "git", "commit", "-m", f"chore: release v{version}"
        ], check=True)
        
        subprocess.run([
            "git", "tag", "-a", f"v{version}", 
            "-m", f"Release v{version}"
        ], check=True)
        
        print(f"✅ Tag v{version} créé")
    
    def push_release(self) -> None:
        """Push release vers repository"""
        print("🚀 Push de la release...")
        
        subprocess.run(["git", "push"], check=True)
        subprocess.run(["git", "push", "--tags"], check=True)
        
        print("✅ Release pushée")
    
    def trigger_deployment(self, version: str) -> None:
        """Déclenche déploiement via GitHub Actions"""
        print(f"🎯 Déclenchement déploiement {self.environment}...")
        
        # Crée workflow dispatch event
        if "GITHUB_TOKEN" in os.environ:
            import requests
            
            headers = {
                "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "event_type": "deploy",
                "client_payload": {
                    "version": version,
                    "environment": self.environment
                }
            }
            
            response = requests.post(
                f"https://api.github.com/repos/{os.environ.get('GITHUB_REPOSITORY', 'company/perplexity-metier')}/dispatches",
                headers=headers,
                json=data
            )
            
            if response.status_code == 204:
                print("✅ Déploiement déclenché")
            else:
                print(f"❌ Erreur déclenchement: {response.status_code}")
        else:
            print("⚠️  GITHUB_TOKEN non défini, déploiement manuel requis")
    
    def create_release(self, bump_type: str = "patch") -> None:
        """Processus complet de release"""
        print(f"🚀 Début release {bump_type} pour {self.environment}")
        
        try:
            # Vérifications préliminaires
            subprocess.run(["git", "status", "--porcelain"], 
                         check=True, capture_output=True, text=True)
            
            # Récupère dernières modifications
            subprocess.run(["git", "pull"], check=True)
            
            # Bump version et génère changelog
            version = self.bump_version(bump_type)
            self.generate_changelog(version)
            
            # Commit et tag
            self.create_git_tag(version)
            
            # Push
            self.push_release()
            
            # Déclenche déploiement
            self.trigger_deployment(version)
            
            print(f"🎉 Release v{version} terminée avec succès!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur release: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionnaire de release automatique")
    parser.add_argument("bump_type", choices=["major", "minor", "patch"], 
                       default="patch", nargs="?",
                       help="Type d'incrémentation version")
    parser.add_argument("--environment", "-e", default="production",
                       help="Environnement de déploiement")
    
    args = parser.parse_args()
    
    release_manager = ReleaseManager(args.environment)
    release_manager.create_release(args.bump_type)

if __name__ == "__main__":
    main()
```

Ces procédures CI/CD assurent un déploiement fiable, sécurisé et automatisé de l'espace métier Perplexity AI, avec une traçabilité complète et des mécanismes de rollback rapides en cas de problème.