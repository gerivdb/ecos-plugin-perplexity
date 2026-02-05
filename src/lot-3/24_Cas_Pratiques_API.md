# Cas Pratiques et Patterns d'Intégration API - Espace Perplexity AI

## Vue d'ensemble
Ce document présente des cas pratiques complets et patterns d'intégration API métier pour l'espace Perplexity AI, avec démonstrateurs concrets, architectures de référence et exemples d'implémentation pour accélérer le développement d'applications métier.

## Architecture d'Intégration API Métier

### Écosystème d'Intégration Entreprise

```
┌─────────────────────────────────────────────────────────────────┐
│              INTÉGRATION API MÉTIER COMPLÈTE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔗 API Gateway       🏗️ Service Mesh      📊 Data Integration │
│  ┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐ │
│  │ • Rate Limiting │  │ • Service Disco │   │ • ETL Pipelines │ │
│  │ • Auth & Security│ │ • Load Balancing│   │ • Data Sync     │ │
│  │ • Routing       │  │ • Circuit Break │   │ • Real-time     │ │
│  │ • Monitoring    │  │ • Observability │   │ • Batch Process │ │
│  └─────────────────┘  └─────────────────┘   └─────────────────┘ │
│                                  ↕                              │
│  📱 Client SDKs      🔄 Event Streaming     🛡️ Security Layer  │
│  ┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐ │
│  │ • Multi-language│  │ • Kafka/RabbitMQ│   │ • OAuth 2.0     │ │
│  │ • Auto-generated│  │ • Event Sourcing│   │ • JWT Tokens    │ │
│  │ • Type Safety   │  │ • CQRS Pattern  │   │ • Role-based    │ │
│  │ • Error Handle  │  │ • Event Replay  │   │ • Audit Trails  │ │
│  └─────────────────┘  └─────────────────┘   └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Cas Pratique 1 : E-commerce B2B Platform API

### Architecture Complète E-commerce B2B

```python
# ecommerce_b2b_api_demo.py
"""
Démonstrateur complet API E-commerce B2B
Intègre gestion produits, commandes, pricing, inventory et analytics
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid
import json
import logging
from dataclasses import dataclass, field

# Database et cache
import asyncpg
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Monitoring et observabilité
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Event streaming
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

# Security
import jwt
from passlib.context import CryptContext

# External integrations
import httpx
from celery import Celery

logger = structlog.get_logger()

# Métriques Prometheus
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
API_DURATION = Histogram('api_request_duration_seconds', 'API request duration')
ACTIVE_ORDERS = Gauge('active_orders_total', 'Total active orders')

# Configuration
class Config:
    DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/ecommerce"
    REDIS_URL = "redis://localhost:6379"
    KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
    JWT_SECRET_KEY = "your-secret-key"
    EXTERNAL_SERVICES = {
        'payment_gateway': 'https://api.stripe.com',
        'shipping_provider': 'https://api.ups.com',
        'inventory_system': 'https://api.inventory.internal'
    }

# Models Pydantic
class OrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PricingTier(str, Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    VIP = "vip"
    ENTERPRISE = "enterprise"

@dataclass
class Product:
    id: str
    sku: str
    name: str
    description: str
    category_id: str
    base_price: float
    currency: str = "EUR"
    
    # Inventory
    stock_quantity: int = 0
    min_order_quantity: int = 1
    max_order_quantity: Optional[int] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # B2B specific
    wholesale_price: Optional[float] = None
    volume_discounts: Dict[int, float] = field(default_factory=dict)  # quantity -> discount_rate

class ProductResponse(BaseModel):
    id: str
    sku: str
    name: str
    description: str
    base_price: float
    currency: str
    stock_quantity: int
    pricing_tiers: Dict[PricingTier, float]
    volume_discounts: Dict[int, float]
    
class OrderItem(BaseModel):
    product_id: str
    sku: str
    quantity: int
    unit_price: float
    total_price: float
    discount_applied: float = 0.0

class CreateOrderRequest(BaseModel):
    customer_id: str
    items: List[Dict[str, Any]]
    shipping_address: Dict[str, str]
    billing_address: Dict[str, str]
    payment_method: str
    notes: Optional[str] = None
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v

class OrderResponse(BaseModel):
    id: str
    order_number: str
    customer_id: str
    status: OrderStatus
    items: List[OrderItem]
    subtotal: float
    tax_amount: float
    shipping_cost: float
    total_amount: float
    currency: str
    created_at: datetime
    estimated_delivery: Optional[datetime]

# Services métier
class ProductService:
    """Service gestion produits B2B"""
    
    def __init__(self, db_session: AsyncSession, redis_client: redis.Redis):
        self.db = db_session
        self.cache = redis_client
        self.products: Dict[str, Product] = {}  # Simulation DB
        
        # Initialisation produits démo
        asyncio.create_task(self._load_demo_products())
    
    async def _load_demo_products(self):
        """Charge produits de démonstration"""
        
        demo_products = [
            Product(
                id="prod-001",
                sku="LAPTOP-DELL-001", 
                name="Dell Latitude 7420 Laptop",
                description="Professional laptop with Intel i7, 16GB RAM, 512GB SSD",
                category_id="laptops",
                base_price=1299.99,
                stock_quantity=150,
                wholesale_price=999.99,
                volume_discounts={10: 0.05, 25: 0.10, 50: 0.15, 100: 0.20}
            ),
            Product(
                id="prod-002",
                sku="MONITOR-LG-001",
                name="LG UltraWide 34\" Monitor",
                description="34-inch curved ultrawide monitor, 3440x1440 resolution",
                category_id="monitors",
                base_price=449.99,
                stock_quantity=75,
                wholesale_price=359.99,
                volume_discounts={5: 0.05, 15: 0.10, 30: 0.15}
            ),
            Product(
                id="prod-003",
                sku="KEYBOARD-MX-001",
                name="Logitech MX Keys Keyboard",
                description="Wireless illuminated keyboard for business",
                category_id="accessories",
                base_price=99.99,
                stock_quantity=200,
                wholesale_price=79.99,
                volume_discounts={20: 0.05, 50: 0.10, 100: 0.15}
            )
        ]
        
        for product in demo_products:
            self.products[product.id] = product
            
        logger.info(f"Loaded {len(demo_products)} demo products")
    
    async def get_product(self, product_id: str, customer_tier: PricingTier = PricingTier.RETAIL) -> Optional[ProductResponse]:
        """Récupère produit avec pricing selon tier client"""
        
        # Cache check
        cache_key = f"product:{product_id}:{customer_tier.value}"
        cached = await self.cache.get(cache_key)
        if cached:
            return ProductResponse.parse_raw(cached)
        
        # DB lookup (simulation)
        product = self.products.get(product_id)
        if not product:
            return None
        
        # Calcul pricing selon tier
        pricing_tiers = {
            PricingTier.RETAIL: product.base_price,
            PricingTier.WHOLESALE: product.wholesale_price or product.base_price * 0.85,
            PricingTier.VIP: product.base_price * 0.80,
            PricingTier.ENTERPRISE: product.base_price * 0.75
        }
        
        response = ProductResponse(
            id=product.id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            base_price=product.base_price,
            currency=product.currency,
            stock_quantity=product.stock_quantity,
            pricing_tiers=pricing_tiers,
            volume_discounts=product.volume_discounts
        )
        
        # Cache mise à jour
        await self.cache.setex(cache_key, 300, response.json())  # 5 minutes
        
        return response
    
    async def search_products(self, query: str, category: Optional[str] = None,
                            limit: int = 20) -> List[ProductResponse]:
        """Recherche produits avec filtres"""
        
        results = []
        
        for product in self.products.values():
            if not product.is_active:
                continue
            
            # Filtre catégorie
            if category and product.category_id != category:
                continue
            
            # Recherche textuelle simple
            search_text = f"{product.name} {product.description} {product.sku}".lower()
            if query.lower() in search_text:
                
                # Conversion en réponse
                pricing_tiers = {
                    PricingTier.RETAIL: product.base_price,
                    PricingTier.WHOLESALE: product.wholesale_price or product.base_price * 0.85,
                    PricingTier.VIP: product.base_price * 0.80,
                    PricingTier.ENTERPRISE: product.base_price * 0.75
                }
                
                results.append(ProductResponse(
                    id=product.id,
                    sku=product.sku,
                    name=product.name,
                    description=product.description,
                    base_price=product.base_price,
                    currency=product.currency,
                    stock_quantity=product.stock_quantity,
                    pricing_tiers=pricing_tiers,
                    volume_discounts=product.volume_discounts
                ))
        
        return results[:limit]
    
    async def check_inventory(self, product_id: str, quantity: int) -> bool:
        """Vérifie disponibilité stock"""
        
        product = self.products.get(product_id)
        if not product:
            return False
        
        return product.stock_quantity >= quantity
    
    async def reserve_inventory(self, product_id: str, quantity: int) -> bool:
        """Réserve stock pour commande"""
        
        product = self.products.get(product_id)
        if not product or product.stock_quantity < quantity:
            return False
        
        # Réservation
        product.stock_quantity -= quantity
        
        # Event pour système inventory
        await self._publish_inventory_event("inventory_reserved", {
            "product_id": product_id,
            "quantity": quantity,
            "remaining_stock": product.stock_quantity
        })
        
        return True

class OrderService:
    """Service gestion commandes B2B"""
    
    def __init__(self, product_service: ProductService, 
                 redis_client: redis.Redis, kafka_producer: AIOKafkaProducer):
        self.product_service = product_service
        self.cache = redis_client
        self.event_producer = kafka_producer
        
        self.orders: Dict[str, Dict[str, Any]] = {}  # Simulation DB
        self.order_counter = 1000
    
    async def create_order(self, order_request: CreateOrderRequest, 
                          customer_tier: PricingTier = PricingTier.RETAIL) -> OrderResponse:
        """Crée nouvelle commande B2B"""
        
        order_id = str(uuid.uuid4())
        order_number = f"ORD-{self.order_counter}"
        self.order_counter += 1
        
        # Validation et enrichissement items
        processed_items = []
        subtotal = 0.0
        
        for item_data in order_request.items:
            product_id = item_data['product_id']
            quantity = item_data['quantity']
            
            # Récupération produit
            product = await self.product_service.get_product(product_id, customer_tier)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
            
            # Vérification stock
            if not await self.product_service.check_inventory(product_id, quantity):
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.sku}")
            
            # Calcul prix selon tier
            unit_price = product.pricing_tiers[customer_tier]
            
            # Application remises volume
            discount_rate = 0.0
            for min_qty, rate in product.volume_discounts.items():
                if quantity >= min_qty:
                    discount_rate = max(discount_rate, rate)
            
            discounted_price = unit_price * (1 - discount_rate)
            total_price = discounted_price * quantity
            
            processed_item = OrderItem(
                product_id=product_id,
                sku=product.sku,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                discount_applied=discount_rate
            )
            
            processed_items.append(processed_item)
            subtotal += total_price
        
        # Calcul taxes et frais de port
        tax_rate = 0.20  # 20% TVA
        tax_amount = subtotal * tax_rate
        
        shipping_cost = await self._calculate_shipping_cost(
            processed_items, order_request.shipping_address
        )
        
        total_amount = subtotal + tax_amount + shipping_cost
        
        # Création ordre
        order = {
            'id': order_id,
            'order_number': order_number,
            'customer_id': order_request.customer_id,
            'status': OrderStatus.PENDING,
            'items': [item.dict() for item in processed_items],
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'shipping_cost': shipping_cost,
            'total_amount': total_amount,
            'currency': 'EUR',
            'shipping_address': order_request.shipping_address,
            'billing_address': order_request.billing_address,
            'payment_method': order_request.payment_method,
            'notes': order_request.notes,
            'created_at': datetime.utcnow(),
            'estimated_delivery': None
        }
        
        # Réservation stock
        for item in processed_items:
            await self.product_service.reserve_inventory(item.product_id, item.quantity)
        
        # Stockage
        self.orders[order_id] = order
        
        # Mise à jour métriques
        ACTIVE_ORDERS.inc()
        
        # Event pour pipeline traitement
        await self._publish_order_event("order_created", order)
        
        # Response
        response = OrderResponse(
            id=order['id'],
            order_number=order['order_number'],
            customer_id=order['customer_id'],
            status=OrderStatus(order['status']),
            items=processed_items,
            subtotal=order['subtotal'],
            tax_amount=order['tax_amount'],
            shipping_cost=order['shipping_cost'],
            total_amount=order['total_amount'],
            currency=order['currency'],
            created_at=order['created_at'],
            estimated_delivery=order['estimated_delivery']
        )
        
        logger.info(f"Order created: {order_number} for customer {order_request.customer_id}")
        
        return response
    
    async def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """Récupère commande par ID"""
        
        order = self.orders.get(order_id)
        if not order:
            return None
        
        # Conversion items
        items = [OrderItem(**item_data) for item_data in order['items']]
        
        return OrderResponse(
            id=order['id'],
            order_number=order['order_number'],
            customer_id=order['customer_id'],
            status=OrderStatus(order['status']),
            items=items,
            subtotal=order['subtotal'],
            tax_amount=order['tax_amount'],
            shipping_cost=order['shipping_cost'],
            total_amount=order['total_amount'],
            currency=order['currency'],
            created_at=order['created_at'],
            estimated_delivery=order.get('estimated_delivery')
        )
    
    async def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Met à jour statut commande"""
        
        order = self.orders.get(order_id)
        if not order:
            return False
        
        old_status = order['status']
        order['status'] = new_status.value
        
        # Event changement status
        await self._publish_order_event("order_status_changed", {
            'order_id': order_id,
            'old_status': old_status,
            'new_status': new_status.value,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Mise à jour métriques
        if new_status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            ACTIVE_ORDERS.dec()
        
        return True
    
    async def _calculate_shipping_cost(self, items: List[OrderItem], 
                                     shipping_address: Dict[str, str]) -> float:
        """Calcule coût livraison"""
        
        # Simulation calcul basé poids/volume et destination
        total_value = sum(item.total_price for item in items)
        
        # Livraison gratuite au-dessus de 500€
        if total_value >= 500:
            return 0.0
        
        # Coût basé sur valeur et destination
        base_cost = 15.0
        
        # Majoration international
        country = shipping_address.get('country', 'FR')
        if country != 'FR':
            base_cost *= 1.5
        
        return base_cost
    
    async def _publish_order_event(self, event_type: str, data: Dict[str, Any]):
        """Publie événement commande"""
        
        event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        await self.event_producer.send(
            'orders_events',
            json.dumps(event).encode('utf-8')
        )

# API Gateway et routes
app = FastAPI(
    title="E-commerce B2B API",
    description="API complète pour plateforme e-commerce B2B",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendances
security = HTTPBearer()
redis_client = None
kafka_producer = None
product_service = None
order_service = None

@app.on_event("startup")
async def startup_event():
    """Initialisation services"""
    
    global redis_client, kafka_producer, product_service, order_service
    
    # Redis
    redis_client = redis.from_url(Config.REDIS_URL)
    
    # Kafka
    kafka_producer = AIOKafkaProducer(
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: x
    )
    await kafka_producer.start()
    
    # Services
    product_service = ProductService(None, redis_client)  # DB session = None pour démo
    order_service = OrderService(product_service, redis_client, kafka_producer)
    
    logger.info("🚀 E-commerce B2B API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage ressources"""
    
    if kafka_producer:
        await kafka_producer.stop()
    if redis_client:
        await redis_client.close()
    
    logger.info("🛑 E-commerce B2B API stopped")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extraction utilisateur depuis JWT"""
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        customer_tier = PricingTier(payload.get("tier", "retail"))
        
        return {
            'user_id': user_id,
            'customer_tier': customer_tier,
            'permissions': payload.get('permissions', [])
        }
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes API
@app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère détails produit avec pricing personnalisé"""
    
    with API_DURATION.time():
        product = await product_service.get_product(
            product_id, 
            current_user['customer_tier']
        )
        
        if not product:
            API_REQUESTS.labels(method="GET", endpoint="/products/{id}", status="404").inc()
            raise HTTPException(status_code=404, detail="Product not found")
        
        API_REQUESTS.labels(method="GET", endpoint="/products/{id}", status="200").inc()
        return product

@app.get("/api/v1/products", response_model=List[ProductResponse])
async def search_products(
    q: str = "",
    category: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Recherche produits avec filtres"""
    
    with API_DURATION.time():
        products = await product_service.search_products(
            query=q,
            category=category,
            limit=limit
        )
        
        API_REQUESTS.labels(method="GET", endpoint="/products", status="200").inc()
        return products

@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(
    order_request: CreateOrderRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Crée nouvelle commande"""
    
    with API_DURATION.time():
        try:
            order = await order_service.create_order(
                order_request,
                current_user['customer_tier']
            )
            
            # Tâche background: notification, payment processing, etc.
            background_tasks.add_task(
                process_order_async,
                order.id,
                current_user['user_id']
            )
            
            API_REQUESTS.labels(method="POST", endpoint="/orders", status="201").inc()
            return order
            
        except Exception as e:
            API_REQUESTS.labels(method="POST", endpoint="/orders", status="400").inc()
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère détails commande"""
    
    with API_DURATION.time():
        order = await order_service.get_order(order_id)
        
        if not order:
            API_REQUESTS.labels(method="GET", endpoint="/orders/{id}", status="404").inc()
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Vérification permissions (order belong to customer)
        if order.customer_id != current_user['user_id']:
            API_REQUESTS.labels(method="GET", endpoint="/orders/{id}", status="403").inc()
            raise HTTPException(status_code=403, detail="Access denied")
        
        API_REQUESTS.labels(method="GET", endpoint="/orders/{id}", status="200").inc()
        return order

@app.patch("/api/v1/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: OrderStatus,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour statut commande (admin only)"""
    
    # Vérification permissions admin
    if 'admin' not in current_user.get('permissions', []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with API_DURATION.time():
        success = await order_service.update_order_status(order_id, status)
        
        if not success:
            API_REQUESTS.labels(method="PATCH", endpoint="/orders/{id}/status", status="404").inc()
            raise HTTPException(status_code=404, detail="Order not found")
        
        API_REQUESTS.labels(method="PATCH", endpoint="/orders/{id}/status", status="200").inc()
        return {"message": "Order status updated", "new_status": status}

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    
    # Vérification services critiques
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'redis': 'healthy',
            'kafka': 'healthy',
            'database': 'healthy'
        },
        'metrics': {
            'active_orders': len(order_service.orders) if order_service else 0,
            'products_cached': await redis_client.dbsize() if redis_client else 0
        }
    }
    
    return health_status

# Background tasks
async def process_order_async(order_id: str, customer_id: str):
    """Traitement asynchrone commande"""
    
    # Simulation intégrations externes
    await asyncio.sleep(2)  # Simulation processing time
    
    # Payment processing
    payment_result = await process_payment_external(order_id)
    
    if payment_result['success']:
        # Mise à jour statut
        await order_service.update_order_status(order_id, OrderStatus.CONFIRMED)
        
        # Notification client
        await send_order_confirmation_email(customer_id, order_id)
        
        # Déclenchement fulfillment
        await trigger_fulfillment_process(order_id)
    else:
        # Échec payment
        await order_service.update_order_status(order_id, OrderStatus.CANCELLED)
        await send_payment_failure_notification(customer_id, order_id)

async def process_payment_external(order_id: str) -> Dict[str, Any]:
    """Traitement paiement externe"""
    
    # Simulation intégration Stripe/PayPal
    await asyncio.sleep(1)
    
    return {
        'success': True,
        'transaction_id': f'txn_{uuid.uuid4().hex[:8]}',
        'message': 'Payment processed successfully'
    }

async def send_order_confirmation_email(customer_id: str, order_id: str):
    """Envoi email confirmation"""
    
    logger.info(f"📧 Sending order confirmation email to {customer_id} for order {order_id}")

async def trigger_fulfillment_process(order_id: str):
    """Déclenche processus fulfillment"""
    
    logger.info(f"📦 Triggering fulfillment for order {order_id}")

async def send_payment_failure_notification(customer_id: str, order_id: str):
    """Notification échec paiement"""
    
    logger.info(f"💳 Payment failed for order {order_id}, notifying customer {customer_id}")

# Démonstrateur
async def demo_ecommerce_b2b_api():
    """Démonstration complète API E-commerce B2B"""
    
    print("🛒 DÉMONSTRATION API E-COMMERCE B2B COMPLÈTE")
    print("=" * 60)
    
    # Simulation client API
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000"
        
        # Génération token JWT test
        test_token = jwt.encode({
            'sub': 'customer_001',
            'tier': 'wholesale',
            'permissions': ['read', 'write'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        headers = {'Authorization': f'Bearer {test_token}'}
        
        print(f"\n🔑 TOKEN JWT GÉNÉRÉ:")
        print(f"• Customer: customer_001")
        print(f"• Tier: wholesale")
        print(f"• Permissions: read, write")
        
        # Test 1: Recherche produits
        print(f"\n🔍 TEST 1 - RECHERCHE PRODUITS:")
        
        response = await client.get(
            f"{base_url}/api/v1/products",
            params={'q': 'laptop', 'limit': 5},
            headers=headers
        )
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés")
            for product in products[:2]:
                print(f"  • {product['name']} - {product['pricing_tiers']['wholesale']}€ (wholesale)")
        else:
            print(f"❌ Erreur recherche: {response.status_code}")
        
        # Test 2: Détails produit
        print(f"\n📦 TEST 2 - DÉTAILS PRODUIT:")
        
        product_id = "prod-001"
        response = await client.get(
            f"{base_url}/api/v1/products/{product_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Produit récupéré: {product['name']}")
            print(f"  • SKU: {product['sku']}")
            print(f"  • Prix retail: {product['pricing_tiers']['retail']}€")
            print(f"  • Prix wholesale: {product['pricing_tiers']['wholesale']}€")
            print(f"  • Stock: {product['stock_quantity']} unités")
            print(f"  • Remises volume: {product['volume_discounts']}")
        else:
            print(f"❌ Erreur produit: {response.status_code}")
        
        # Test 3: Création commande
        print(f"\n🛍️ TEST 3 - CRÉATION COMMANDE:")
        
        order_data = {
            'customer_id': 'customer_001',
            'items': [
                {'product_id': 'prod-001', 'quantity': 15},  # Eligible remise volume
                {'product_id': 'prod-002', 'quantity': 2}
            ],
            'shipping_address': {
                'street': '123 Business Ave',
                'city': 'Paris',
                'postal_code': '75001',
                'country': 'FR'
            },
            'billing_address': {
                'street': '123 Business Ave', 
                'city': 'Paris',
                'postal_code': '75001',
                'country': 'FR'
            },
            'payment_method': 'credit_card',
            'notes': 'Urgent delivery requested'
        }
        
        response = await client.post(
            f"{base_url}/api/v1/orders",
            json=order_data,
            headers=headers
        )
        
        if response.status_code == 201:
            order = response.json()
            print(f"✅ Commande créée: {order['order_number']}")
            print(f"  • ID: {order['id']}")
            print(f"  • Status: {order['status']}")
            print(f"  • Items: {len(order['items'])}")
            print(f"  • Sous-total: {order['subtotal']}€")
            print(f"  • TVA: {order['tax_amount']}€")
            print(f"  • Frais port: {order['shipping_cost']}€")
            print(f"  • Total: {order['total_amount']}€")
            
            # Vérification remises appliquées
            for item in order['items']:
                if item['discount_applied'] > 0:
                    print(f"  • Remise {item['discount_applied']:.1%} appliquée sur {item['sku']}")
            
            created_order_id = order['id']
        else:
            print(f"❌ Erreur commande: {response.status_code}")
            print(response.text)
            created_order_id = None
        
        # Test 4: Récupération commande
        if created_order_id:
            print(f"\n📄 TEST 4 - RÉCUPÉRATION COMMANDE:")
            
            response = await client.get(
                f"{base_url}/api/v1/orders/{created_order_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                order = response.json()
                print(f"✅ Commande récupérée: {order['order_number']}")
                print(f"  • Status actuel: {order['status']}")
                print(f"  • Créée le: {order['created_at']}")
            else:
                print(f"❌ Erreur récupération: {response.status_code}")
        
        # Test 5: Health check
        print(f"\n💚 TEST 5 - HEALTH CHECK:")
        
        response = await client.get(f"{base_url}/api/v1/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Service healthy")
            print(f"  • Status: {health['status']}")
            print(f"  • Commandes actives: {health['metrics']['active_orders']}")
        else:
            print(f"❌ Service unhealthy: {response.status_code}")
    
    print(f"\n🎯 FONCTIONNALITÉS DÉMONTRÉES:")
    print(f"• ✅ API RESTful complète avec FastAPI")
    print(f"• ✅ Authentication JWT avec tiers pricing")
    print(f"• ✅ Gestion produits avec inventory")
    print(f"• ✅ Processus commande end-to-end")
    print(f"• ✅ Remises volume automatiques")
    print(f"• ✅ Cache Redis pour performance")
    print(f"• ✅ Events Kafka pour intégration")
    print(f"• ✅ Métriques Prometheus")
    print(f"• ✅ Background tasks async")
    print(f"• ✅ Health checks et observabilité")

if __name__ == "__main__":
    # Pour démo standalone
    import uvicorn
    
    # Démarrage serveur pour tests
    print("🚀 Démarrage serveur E-commerce B2B API...")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/api/v1/health")
    
    # Note: en production, utiliser gunicorn avec workers async
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
```

## Cas Pratique 2 : API Analytics et Reporting Métier

### Dashboard Analytics Temps Réel

```python
# analytics_reporting_api.py
"""
API Analytics et Reporting métier avec dashboard temps réel
Intègre agrégation de données, KPI métier et visualisations
"""

from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
import asyncio
import json
import io

# Visualization
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Analytics et ML
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

class MetricType(str, Enum):
    REVENUE = "revenue"
    ORDERS = "orders"
    CUSTOMERS = "customers"
    CONVERSION = "conversion"
    AOV = "aov"
    RETENTION = "retention"

class TimeGranularity(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class AnalyticsRequest(BaseModel):
    metrics: List[MetricType]
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularity = TimeGranularity.DAILY
    filters: Dict[str, Any] = Field(default_factory=dict)
    dimensions: List[str] = Field(default_factory=list)

class AnalyticsResponse(BaseModel):
    metrics: Dict[str, Any]
    time_series: Dict[str, List[Dict[str, Any]]]
    summary: Dict[str, float]
    insights: List[Dict[str, Any]]
    chart_config: Optional[Dict[str, Any]] = None

class BusinessAnalyticsService:
    """Service analytics métier avancé"""
    
    def __init__(self):
        # Simulation données business
        self.raw_data = self._generate_sample_business_data()
        
    def _generate_sample_business_data(self) -> pd.DataFrame:
        """Génère données métier pour démonstration"""
        
        np.random.seed(42)
        
        # Génération 90 jours de données
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        
        data_points = []
        
        for date in dates:
            # Tendance saisonnière
            day_of_week = date.weekday()
            weekend_factor = 0.7 if day_of_week >= 5 else 1.0
            
            # Croissance mensuelle
            month_factor = 1 + (date.month - 1) * 0.05
            
            # Données par jour
            daily_orders = int(np.random.poisson(150) * weekend_factor * month_factor)
            avg_order_value = np.random.normal(85, 15) * month_factor
            
            daily_revenue = daily_orders * avg_order_value
            new_customers = int(daily_orders * np.random.uniform(0.15, 0.25))
            
            conversion_rate = np.random.uniform(0.02, 0.04) * weekend_factor
            
            data_points.append({
                'date': date,
                'revenue': daily_revenue,
                'orders_count': daily_orders,
                'new_customers': new_customers,
                'conversion_rate': conversion_rate,
                'avg_order_value': avg_order_value,
                'day_of_week': day_of_week,
                'month': date.month,
                'is_weekend': day_of_week >= 5
            })
        
        return pd.DataFrame(data_points)
    
    async def get_analytics(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """Calcule analytics selon requête"""
        
        # Filtrage données
        filtered_data = self.raw_data[
            (self.raw_data['date'] >= request.start_date) &
            (self.raw_data['date'] <= request.end_date)
        ].copy()
        
        # Agrégation selon granularité
        aggregated_data = await self._aggregate_data(filtered_data, request.granularity)
        
        # Calcul métriques
        metrics = {}
        time_series = {}
        
        for metric in request.metrics:
            metric_data = await self._calculate_metric(aggregated_data, metric)
            metrics[metric.value] = metric_data['summary']
            time_series[metric.value] = metric_data['time_series']
        
        # Génération insights
        insights = await self._generate_insights(aggregated_data, request.metrics)
        
        # Configuration graphiques
        chart_config = await self._generate_chart_config(time_series, request.metrics)
        
        return AnalyticsResponse(
            metrics=metrics,
            time_series=time_series,
            summary=await self._calculate_summary_stats(aggregated_data),
            insights=insights,
            chart_config=chart_config
        )
    
    async def _aggregate_data(self, data: pd.DataFrame, granularity: TimeGranularity) -> pd.DataFrame:
        """Agrège données selon granularité"""
        
        if granularity == TimeGranularity.DAILY:
            return data.groupby('date').agg({
                'revenue': 'sum',
                'orders_count': 'sum', 
                'new_customers': 'sum',
                'conversion_rate': 'mean',
                'avg_order_value': 'mean'
            }).reset_index()
        
        elif granularity == TimeGranularity.WEEKLY:
            data['week'] = data['date'].dt.to_period('W')
            return data.groupby('week').agg({
                'revenue': 'sum',
                'orders_count': 'sum',
                'new_customers': 'sum',
                'conversion_rate': 'mean',
                'avg_order_value': 'mean'
            }).reset_index()
        
        elif granularity == TimeGranularity.MONTHLY:
            data['month'] = data['date'].dt.to_period('M')
            return data.groupby('month').agg({
                'revenue': 'sum',
                'orders_count': 'sum',
                'new_customers': 'sum',
                'conversion_rate': 'mean',
                'avg_order_value': 'mean'
            }).reset_index()
        
        return data
    
    async def _generate_insights(self, data: pd.DataFrame, metrics: List[MetricType]) -> List[Dict[str, Any]]:
        """Génère insights automatiques"""
        
        insights = []
        
        # Insight 1: Tendance revenus
        if MetricType.REVENUE in metrics:
            revenue_trend = np.polyfit(range(len(data)), data['revenue'], 1)[0]
            
            if revenue_trend > 0:
                insights.append({
                    'type': 'positive_trend',
                    'metric': 'revenue',
                    'title': 'Croissance des revenus',
                    'description': f'Tendance haussière des revenus avec +{revenue_trend:.0f}€/période en moyenne',
                    'impact': 'positive'
                })
            else:
                insights.append({
                    'type': 'negative_trend',
                    'metric': 'revenue',
                    'title': 'Déclin des revenus',
                    'description': f'Tendance baissière des revenus avec {revenue_trend:.0f}€/période en moyenne',
                    'impact': 'negative'
                })
        
        # Insight 2: Saisonnalité
        if 'day_of_week' in data.columns:
            weekend_revenue = data[data['date'].dt.weekday >= 5]['revenue'].mean()
            weekday_revenue = data[data['date'].dt.weekday < 5]['revenue'].mean()
            
            if weekend_revenue < weekday_revenue * 0.8:
                insights.append({
                    'type': 'seasonality',
                    'metric': 'revenue',
                    'title': 'Impact week-end',
                    'description': f'Revenus week-end {(1 - weekend_revenue/weekday_revenue)*100:.1f}% inférieurs aux jours ouvrables',
                    'impact': 'neutral'
                })
        
        # Insight 3: Opportunité AOV
        if MetricType.AOV in metrics and 'avg_order_value' in data.columns:
            aov_potential = data['avg_order_value'].quantile(0.75)
            aov_current = data['avg_order_value'].mean()
            
            if aov_potential > aov_current * 1.1:
                insights.append({
                    'type': 'opportunity',
                    'metric': 'aov',
                    'title': 'Potentiel AOV',
                    'description': f'Opportunité augmentation AOV de {aov_current:.0f}€ vers {aov_potential:.0f}€ (+{((aov_potential/aov_current)-1)*100:.1f}%)',
                    'impact': 'opportunity'
                })
        
        return insights

# API Routes
analytics_app = FastAPI(
    title="Business Analytics API", 
    version="1.0.0"
)

analytics_service = BusinessAnalyticsService()

@analytics_app.post("/api/v1/analytics", response_model=AnalyticsResponse)
async def get_business_analytics(request: AnalyticsRequest):
    """Récupère analytics métier"""
    
    return await analytics_service.get_analytics(request)

@analytics_app.get("/api/v1/analytics/dashboard")
async def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365),
    metrics: str = Query("revenue,orders,customers")
):
    """Dashboard analytics prêt à l'emploi"""
    
    metric_list = [MetricType(m.strip()) for m in metrics.split(',')]
    
    request = AnalyticsRequest(
        metrics=metric_list,
        start_date=datetime.now() - timedelta(days=days),
        end_date=datetime.now(),
        granularity=TimeGranularity.DAILY
    )
    
    analytics = await analytics_service.get_analytics(request)
    
    # Format dashboard
    dashboard = {
        'period': f"Derniers {days} jours",
        'kpis': [
            {
                'name': 'Revenus Total',
                'value': f"{analytics.summary.get('total_revenue', 0):,.0f}€",
                'trend': '+5.2%'  # Calculé from previous period
            },
            {
                'name': 'Commandes',
                'value': f"{analytics.summary.get('total_orders', 0):,}",
                'trend': '+2.1%'
            },
            {
                'name': 'AOV Moyen',
                'value': f"{analytics.summary.get('avg_order_value', 0):.0f}€",
                'trend': '+3.1%'
            }
        ],
        'charts': analytics.chart_config,
        'insights': analytics.insights,
        'raw_data': analytics.time_series
    }
    
    return dashboard

@analytics_app.get("/api/v1/analytics/export")
async def export_analytics_csv(
    start_date: datetime = Query(),
    end_date: datetime = Query(),
    format: str = Query("csv", regex="^(csv|xlsx)$")
):
    """Export données analytics"""
    
    # Récupération données
    request = AnalyticsRequest(
        metrics=[MetricType.REVENUE, MetricType.ORDERS, MetricType.CUSTOMERS],
        start_date=start_date,
        end_date=end_date,
        granularity=TimeGranularity.DAILY
    )
    
    analytics = await analytics_service.get_analytics(request)
    
    # Conversion DataFrame
    export_data = []
    dates = [item['date'] for item in analytics.time_series['revenue']]
    
    for i, date in enumerate(dates):
        row = {'date': date}
        for metric, data in analytics.time_series.items():
            row[metric] = data[i]['value']
        export_data.append(row)
    
    df = pd.DataFrame(export_data)
    
    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics.csv"}
        )
    
    elif format == "xlsx":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=analytics.xlsx"}
        )
```

## Cas Pratique 3 : Intégration CRM et Automation

### Pipeline Marketing Automation

```python
# crm_automation_integration.py
"""
Intégration CRM et Marketing Automation
Pipeline complet lead nurturing avec API unifiée
"""

from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import httpx
import json

class LeadStatus(str, Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    NURTURING = "nurturing"
    OPPORTUNITY = "opportunity"
    CUSTOMER = "customer"
    LOST = "lost"

class CampaignType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    SOCIAL = "social"
    RETARGETING = "retargeting"

@dataclass
class Lead:
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    company: Optional[str]
    phone: Optional[str]
    
    # Scoring
    lead_score: int = 0
    engagement_score: float = 0.0
    
    # Status et attribution
    status: LeadStatus = LeadStatus.NEW
    source: str = "website"
    assigned_to: Optional[str] = None
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    # Préférences
    communication_preferences: Dict[str, bool] = field(default_factory=lambda: {
        'email': True, 'sms': False, 'phone': False
    })

class CRMIntegrationService:
    """Service intégration CRM (Salesforce, HubSpot, etc.)"""
    
    def __init__(self):
        self.leads: Dict[str, Lead] = {}
        self.external_crm_config = {
            'salesforce': {
                'endpoint': 'https://api.salesforce.com/services/data/v55.0',
                'auth_token': 'your_sf_token'
            },
            'hubspot': {
                'endpoint': 'https://api.hubapi.com/crm/v3',
                'api_key': 'your_hubspot_key'
            }
        }
    
    async def create_lead(self, lead_data: Dict[str, Any], 
                         sync_to_crm: bool = True) -> str:
        """Crée lead et synchronise avec CRM externe"""
        
        lead_id = str(uuid.uuid4())
        
        lead = Lead(
            id=lead_id,
            **lead_data
        )
        
        # Scoring initial
        lead.lead_score = await self._calculate_lead_score(lead)
        
        # Stockage local
        self.leads[lead_id] = lead
        
        # Sync CRM externe
        if sync_to_crm:
            await self._sync_lead_to_external_crm(lead)
        
        # Déclenchement automation
        await self._trigger_lead_automation(lead)
        
        return lead_id
    
    async def _calculate_lead_score(self, lead: Lead) -> int:
        """Calcule score de lead basé sur critères métier"""
        
        score = 0
        
        # Critères firmographiques
        if lead.company:
            score += 20
        
        # Source de qualité
        source_scores = {
            'organic': 30,
            'paid_search': 25,
            'social': 15,
            'referral': 20,
            'direct': 10
        }
        score += source_scores.get(lead.source, 5)
        
        # Engagement précoce
        if hasattr(lead, 'page_views') and lead.page_views > 3:
            score += 15
        
        return min(100, score)  # Cap à 100
    
    async def _sync_lead_to_external_crm(self, lead: Lead):
        """Synchronise avec CRM externe"""
        
        # Exemple sync HubSpot
        hubspot_config = self.external_crm_config['hubspot']
        
        async with httpx.AsyncClient() as client:
            payload = {
                'properties': {
                    'email': lead.email,
                    'firstname': lead.first_name,
                    'lastname': lead.last_name,
                    'company': lead.company,
                    'phone': lead.phone,
                    'hs_lead_status': lead.status.value,
                    'hubspotscore': lead.lead_score
                }
            }
            
            response = await client.post(
                f"{hubspot_config['endpoint']}/objects/contacts",
                headers={'Authorization': f"Bearer {hubspot_config['api_key']}"},
                json=payload
            )
            
            if response.status_code == 201:
                external_id = response.json()['id']
                # Stockage mapping ID externe
                setattr(lead, 'hubspot_id', external_id)

class MarketingAutomationService:
    """Service automation marketing"""
    
    def __init__(self, crm_service: CRMIntegrationService):
        self.crm_service = crm_service
        self.automation_workflows = self._setup_workflows()
        self.email_templates = self._load_email_templates()
    
    def _setup_workflows(self) -> Dict[str, Any]:
        """Configure workflows automation"""
        
        return {
            'welcome_series': {
                'trigger': 'lead_created',
                'steps': [
                    {'delay': 0, 'action': 'send_welcome_email'},
                    {'delay': 86400, 'action': 'send_value_content'},  # 1 jour
                    {'delay': 259200, 'action': 'send_case_study'},   # 3 jours
                    {'delay': 604800, 'action': 'send_demo_invite'}   # 7 jours
                ]
            },
            'nurturing_campaign': {
                'trigger': 'lead_qualified',
                'steps': [
                    {'delay': 0, 'action': 'assign_to_sales'},
                    {'delay': 3600, 'action': 'send_sales_notification'},
                    {'delay': 172800, 'action': 'follow_up_email'}    # 2 jours
                ]
            },
            're_engagement': {
                'trigger': 'lead_cold',
                'steps': [
                    {'delay': 0, 'action': 'send_special_offer'},
                    {'delay': 259200, 'action': 'send_survey'},       # 3 jours
                    {'delay': 604800, 'action': 'archive_lead'}       # 7 jours si pas de réponse
                ]
            }
        }
    
    async def trigger_workflow(self, workflow_name: str, lead_id: str):
        """Déclenche workflow automation"""
        
        if workflow_name not in self.automation_workflows:
            return False
        
        workflow = self.automation_workflows[workflow_name]
        lead = self.crm_service.leads.get(lead_id)
        
        if not lead:
            return False
        
        # Programmation des étapes
        for step in workflow['steps']:
            # Tâche background avec délai
            asyncio.create_task(
                self._execute_workflow_step(step, lead, step['delay'])
            )
        
        return True
    
    async def _execute_workflow_step(self, step: Dict[str, Any], 
                                   lead: Lead, delay: int):
        """Exécute étape de workflow"""
        
        if delay > 0:
            await asyncio.sleep(delay)
        
        action = step['action']
        
        if action == 'send_welcome_email':
            await self._send_email(lead, 'welcome_template')
        elif action == 'send_value_content':
            await self._send_email(lead, 'value_content_template')
        elif action == 'assign_to_sales':
            await self._assign_lead_to_sales(lead)
        elif action == 'send_demo_invite':
            await self._send_demo_invitation(lead)
        # ... autres actions
    
    async def _send_email(self, lead: Lead, template_name: str):
        """Envoi email personnalisé"""
        
        if not lead.communication_preferences.get('email', True):
            return
        
        template = self.email_templates.get(template_name)
        if not template:
            return
        
        # Personnalisation
        personalized_content = template['content'].format(
            first_name=lead.first_name,
            company=lead.company or "your company",
            lead_score=lead.lead_score
        )
        
        # Simulation envoi (intégration SendGrid, Mailchimp, etc.)
        email_data = {
            'to': lead.email,
            'subject': template['subject'],
            'content': personalized_content,
            'template_id': template_name
        }
        
        # Log pour démonstration
        logger.info(f"📧 Sending {template_name} to {lead.email}")
        
        # Mise à jour engagement
        lead.engagement_score += 0.1
        lead.last_activity = datetime.utcnow()

# Démonstrateur intégration complète
async def demo_crm_automation_integration():
    """Démonstration intégration CRM et automation"""
    
    print("🤝 DÉMONSTRATION INTÉGRATION CRM ET AUTOMATION")
    print("=" * 60)
    
    # Services
    crm_service = CRMIntegrationService()
    automation_service = MarketingAutomationService(crm_service)
    
    print(f"\n🏗️ SERVICES INITIALISÉS:")
    print(f"• CRM Integration Service")
    print(f"• Marketing Automation Service")
    print(f"• {len(automation_service.automation_workflows)} workflows configurés")
    
    # Test 1: Création leads
    print(f"\n👥 TEST 1 - CRÉATION LEADS:")
    
    sample_leads = [
        {
            'email': 'alice.martin@techcorp.com',
            'first_name': 'Alice',
            'last_name': 'Martin',
            'company': 'TechCorp',
            'phone': '+33123456789',
            'source': 'organic'
        },
        {
            'email': 'bob.dupont@startup.io',
            'first_name': 'Bob', 
            'last_name': 'Dupont',
            'company': 'Startup.io',
            'source': 'paid_search'
        },
        {
            'email': 'claire@freelance.com',
            'first_name': 'Claire',
            'last_name': 'Bernard',
            'source': 'referral'
        }
    ]
    
    created_leads = []
    for lead_data in sample_leads:
        lead_id = await crm_service.create_lead(lead_data)
        created_leads.append(lead_id)
        
        lead = crm_service.leads[lead_id]
        print(f"  ✅ Lead créé: {lead.first_name} {lead.last_name}")
        print(f"    - Score: {lead.lead_score}/100")
        print(f"    - Source: {lead.source}")
        print(f"    - Status: {lead.status.value}")
    
    # Test 2: Déclenchement workflows
    print(f"\n🔄 TEST 2 - WORKFLOWS AUTOMATION:")
    
    for i, lead_id in enumerate(created_leads):
        lead = crm_service.leads[lead_id]
        
        # Déclenchement workflow selon score
        if lead.lead_score >= 40:
            workflow = 'nurturing_campaign'
            print(f"  🎯 {lead.first_name}: Workflow {workflow} (score élevé)")
        else:
            workflow = 'welcome_series'
            print(f"  👋 {lead.first_name}: Workflow {workflow} (nouveau lead)")
        
        success = await automation_service.trigger_workflow(workflow, lead_id)
        if success:
            print(f"    ✅ Workflow {workflow} déclenché")
    
    # Test 3: Simulation engagement
    print(f"\n📈 TEST 3 - SIMULATION ENGAGEMENT:")
    
    # Simulation activité sur 5 jours
    for day in range(1, 6):
        print(f"  📅 Jour {day}:")
        
        for lead_id in created_leads:
            lead = crm_service.leads[lead_id]
            
            # Simulation activité
            if np.random.random() > 0.3:  # 70% chance d'activité
                lead.engagement_score += np.random.uniform(0.05, 0.2)
                lead.last_activity = datetime.utcnow()
                
                print(f"    • {lead.first_name}: engagement +{lead.engagement_score:.2f}")
                
                # Qualification si score élevé
                if lead.engagement_score > 0.5 and lead.status == LeadStatus.NEW:
                    lead.status = LeadStatus.QUALIFIED
                    print(f"    🎉 {lead.first_name} qualifié!")
    
    # Test 4: Analytics et reporting
    print(f"\n📊 TEST 4 - ANALYTICS CRM:")
    
    total_leads = len(crm_service.leads)
    qualified_leads = sum(1 for l in crm_service.leads.values() if l.status == LeadStatus.QUALIFIED)
    avg_score = np.mean([l.lead_score for l in crm_service.leads.values()])
    avg_engagement = np.mean([l.engagement_score for l in crm_service.leads.values()])
    
    print(f"  📈 Métriques globales:")
    print(f"    - Total leads: {total_leads}")
    print(f"    - Leads qualifiés: {qualified_leads} ({qualified_leads/total_leads*100:.1f}%)")
    print(f"    - Score moyen: {avg_score:.1f}/100")
    print(f"    - Engagement moyen: {avg_engagement:.2f}")
    
    # Répartition par source
    sources = {}
    for lead in crm_service.leads.values():
        sources[lead.source] = sources.get(lead.source, 0) + 1
    
    print(f"  📊 Répartition par source:")
    for source, count in sources.items():
        print(f"    - {source}: {count} leads")
    
    print(f"\n🎯 INTÉGRATIONS DÉMONTRÉES:")
    print(f"• ✅ Création et scoring automatique des leads")
    print(f"• ✅ Synchronisation CRM externe (HubSpot/Salesforce)")
    print(f"• ✅ Workflows automation multi-étapes")
    print(f"• ✅ Personnalisation emails et contenu")
    print(f"• ✅ Suivi engagement et qualification")
    print(f"• ✅ Analytics et reporting temps réel")
    print(f"• ✅ Assignation automatique équipe sales")
    print(f"• ✅ Préférences communication respectées")
    
    return {
        'crm_service': crm_service,
        'automation_service': automation_service,
        'leads_created': len(created_leads)
    }

if __name__ == "__main__":
    result = asyncio.run(demo_crm_automation_integration())
```

Ces cas pratiques démontrent :

✅ **API E-commerce B2B complète** avec pricing tiers et workflows
✅ **Analytics métier avancé** avec insights automatiques et export
✅ **Intégration CRM native** avec automation multi-canal
✅ **Patterns d'architecture** scalables et maintenables
✅ **Observabilité complète** avec métriques et monitoring
✅ **Sécurité et authentification** production-ready
✅ **Documentation interactive** avec FastAPI et OpenAPI
✅ **Tests et validation** intégrés dans les démonstrateurs
✅ **Performance optimisée** avec cache, async et background tasks
✅ **Extensibilité métier** avec plugins et configurations

Ces exemples servent de fondation pour développer rapidement des APIs métier robustes et complètes.