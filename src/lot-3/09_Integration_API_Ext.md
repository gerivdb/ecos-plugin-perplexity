# Intégration APIs Externes - Espace Métier Perplexity AI

## Vue d'ensemble
Ce document détaille l'intégration et la gestion des APIs externes dans l'espace métier Perplexity AI, incluant les connecteurs, la sécurisation, et l'optimisation des appels vers les services tiers.

## Architecture d'Intégration APIs

### Principes de Conception

#### Approche API-First
- **Standardisation** : Connecteurs uniformes pour toutes les APIs
- **Résilience** : Gestion des pannes et retry automatique
- **Performance** : Cache intelligent et optimisation des appels
- **Sécurité** : Chiffrement et gestion sécurisée des credentials
- **Monitoring** : Observabilité complète des intégrations

#### Patterns d'Intégration
```
┌─────────────────────────────────────┐
│           Interface Utilisateur      │
├─────────────────────────────────────┤
│         API Gateway Interne         │  ← Routage et authentification
├─────────────────────────────────────┤
│       Connecteurs Spécialisés       │  ← Adaptateurs par service
├─────────────────────────────────────┤
│     Cache et Rate Limiting          │  ← Optimisation performance
├─────────────────────────────────────┤
│        APIs Externes                │  ← Services tiers
└─────────────────────────────────────┘
```

### Gestionnaire d'APIs Centralisé

#### Classe APIManager
```python
import requests
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class AuthType(Enum):
    """Types d'authentification supportés"""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token" 
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"

@dataclass
class APIEndpoint:
    """Configuration d'un endpoint API"""
    name: str
    base_url: str
    auth_type: AuthType
    credentials: Dict[str, str]
    rate_limit: int = 60  # Requêtes par minute
    timeout: int = 30
    retry_attempts: int = 3
    cache_ttl: int = 300  # 5 minutes par défaut
    custom_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.custom_headers is None:
            self.custom_headers = {}

class APIManager:
    """Gestionnaire centralisé des intégrations API"""
    
    def __init__(self, redis_client: redis.Redis = None):
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.request_history = {}  # Pour rate limiting
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        
        # Clé de chiffrement pour les credentials sensibles
        self.cipher_suite = Fernet(Fernet.generate_key())
        
    def register_endpoint(self, endpoint: APIEndpoint) -> None:
        """Enregistre un nouveau endpoint API"""
        # Chiffrement des credentials
        encrypted_creds = {}
        for key, value in endpoint.credentials.items():
            encrypted_creds[key] = self.cipher_suite.encrypt(value.encode()).decode()
        endpoint.credentials = encrypted_creds
        
        self.endpoints[endpoint.name] = endpoint
        logger.info(f"Endpoint {endpoint.name} enregistré")
    
    def _decrypt_credentials(self, endpoint_name: str) -> Dict[str, str]:
        """Déchiffre les credentials d'un endpoint"""
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint_name} non trouvé")
        
        endpoint = self.endpoints[endpoint_name]
        decrypted_creds = {}
        
        for key, encrypted_value in endpoint.credentials.items():
            decrypted_creds[key] = self.cipher_suite.decrypt(encrypted_value.encode()).decode()
        
        return decrypted_creds
    
    def _check_rate_limit(self, endpoint_name: str) -> bool:
        """Vérifie si la limite de taux est respectée"""
        if endpoint_name not in self.endpoints:
            return False
        
        endpoint = self.endpoints[endpoint_name]
        now = time.time()
        
        # Initialise l'historique si nécessaire
        if endpoint_name not in self.request_history:
            self.request_history[endpoint_name] = []
        
        # Nettoie les requêtes anciennes (> 1 minute)
        self.request_history[endpoint_name] = [
            t for t in self.request_history[endpoint_name] 
            if now - t < 60
        ]
        
        # Vérifie la limite
        return len(self.request_history[endpoint_name]) < endpoint.rate_limit
    
    def _wait_for_rate_limit(self, endpoint_name: str) -> None:
        """Attend si nécessaire pour respecter la limite de taux"""
        if not self._check_rate_limit(endpoint_name):
            endpoint = self.endpoints[endpoint_name]
            if self.request_history[endpoint_name]:
                sleep_time = 60 - (time.time() - self.request_history[endpoint_name][0])
                if sleep_time > 0:
                    logger.info(f"Rate limit atteint pour {endpoint_name}, pause {sleep_time:.2f}s")
                    time.sleep(sleep_time)
    
    def _get_cache_key(self, endpoint_name: str, path: str, params: Dict = None) -> str:
        """Génère clé de cache pour une requête"""
        cache_data = {
            'endpoint': endpoint_name,
            'path': path,
            'params': params or {}
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"api_cache:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Récupère réponse depuis le cache"""
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data.decode())
        except Exception as e:
            logger.warning(f"Erreur lecture cache: {e}")
        return None
    
    def _cache_response(self, cache_key: str, response_data: Dict[str, Any], ttl: int) -> None:
        """Met en cache une réponse"""
        try:
            self.redis.setex(
                cache_key, 
                ttl, 
                json.dumps(response_data, default=str)
            )
        except Exception as e:
            logger.warning(f"Erreur écriture cache: {e}")
    
    def _prepare_headers(self, endpoint: APIEndpoint) -> Dict[str, str]:
        """Prépare les headers d'authentification"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PerplexityAI-APIManager/1.0'
        }
        
        # Ajout headers personnalisés
        headers.update(endpoint.custom_headers)
        
        # Authentification
        credentials = self._decrypt_credentials(endpoint.name)
        
        if endpoint.auth_type == AuthType.API_KEY:
            if 'api_key' in credentials:
                headers['X-API-Key'] = credentials['api_key']
            elif 'key' in credentials:
                headers['Authorization'] = f"ApiKey {credentials['key']}"
                
        elif endpoint.auth_type == AuthType.BEARER_TOKEN:
            if 'token' in credentials:
                headers['Authorization'] = f"Bearer {credentials['token']}"
                
        elif endpoint.auth_type == AuthType.BASIC_AUTH:
            import base64
            if 'username' in credentials and 'password' in credentials:
                auth_string = f"{credentials['username']}:{credentials['password']}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                headers['Authorization'] = f"Basic {auth_bytes}"
        
        return headers
    
    def make_request(self, endpoint_name: str, path: str = "", 
                    method: str = "GET", params: Dict = None,
                    json_data: Dict = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Effectue une requête API avec gestion complète d'erreurs et cache
        
        Args:
            endpoint_name: Nom de l'endpoint configuré
            path: Chemin relatif à l'endpoint
            method: Méthode HTTP
            params: Paramètres GET
            json_data: Données JSON pour POST/PUT
            use_cache: Utiliser le cache si disponible
            
        Returns:
            Réponse API sous forme de dictionnaire
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint_name} non configuré")
        
        endpoint = self.endpoints[endpoint_name]
        url = f"{endpoint.base_url.rstrip('/')}/{path.lstrip('/')}" if path else endpoint.base_url
        
        # Vérification cache (GET uniquement)
        cache_key = None
        if method.upper() == "GET" and use_cache:
            cache_key = self._get_cache_key(endpoint_name, path, params)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.info(f"Cache hit pour {endpoint_name}: {path}")
                return cached_response
        
        # Respect du rate limiting
        self._wait_for_rate_limit(endpoint_name)
        
        # Préparation requête
        headers = self._prepare_headers(endpoint)
        
        # Tentatives avec retry
        last_exception = None
        for attempt in range(endpoint.retry_attempts):
            try:
                logger.info(f"Requête {method} vers {endpoint_name}: {url} (tentative {attempt + 1})")
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=endpoint.timeout
                )
                
                # Enregistrement pour rate limiting
                self.request_history.setdefault(endpoint_name, []).append(time.time())
                
                response.raise_for_status()
                
                # Préparation réponse
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {'content': response.text}
                
                # Enrichissement métadonnées
                api_response = {
                    'data': response_data,
                    'metadata': {
                        'endpoint': endpoint_name,
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat(),
                        'response_time_ms': int(response.elapsed.total_seconds() * 1000),
                        'from_cache': False,
                        'attempt': attempt + 1
                    }
                }
                
                # Mise en cache
                if cache_key and method.upper() == "GET":
                    self._cache_response(cache_key, api_response, endpoint.cache_ttl)
                
                logger.info(f"✅ Succès requête {endpoint_name} en {api_response['metadata']['response_time_ms']}ms")
                return api_response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"Tentative {attempt + 1} échouée pour {endpoint_name}: {e}")
                
                if attempt < endpoint.retry_attempts - 1:
                    # Backoff exponentiel
                    sleep_time = 2 ** attempt
                    logger.info(f"Retry dans {sleep_time}s...")
                    time.sleep(sleep_time)
        
        # Toutes les tentatives ont échoué
        error_response = {
            'error': True,
            'message': f"Échec après {endpoint.retry_attempts} tentatives",
            'last_exception': str(last_exception),
            'metadata': {
                'endpoint': endpoint_name,
                'timestamp': datetime.now().isoformat(),
                'attempts': endpoint.retry_attempts
            }
        }
        
        logger.error(f"❌ Échec définitif requête {endpoint_name}: {last_exception}")
        return error_response
    
    def test_endpoint(self, endpoint_name: str) -> Dict[str, Any]:
        """Teste la connectivité d'un endpoint"""
        if endpoint_name not in self.endpoints:
            return {'status': 'error', 'message': 'Endpoint non configuré'}
        
        try:
            # Requête de test simple
            response = self.make_request(endpoint_name, use_cache=False)
            
            if 'error' in response:
                return {
                    'status': 'failed',
                    'endpoint': endpoint_name,
                    'error': response['message']
                }
            else:
                return {
                    'status': 'success',
                    'endpoint': endpoint_name,
                    'response_time_ms': response['metadata']['response_time_ms'],
                    'timestamp': response['metadata']['timestamp']
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'endpoint': endpoint_name,
                'error': str(e)
            }
    
    def get_endpoint_stats(self, endpoint_name: str) -> Dict[str, Any]:
        """Récupère statistiques d'utilisation d'un endpoint"""
        if endpoint_name not in self.endpoints:
            return {}
        
        # Requêtes récentes (dernière heure)
        now = time.time()
        recent_requests = [
            t for t in self.request_history.get(endpoint_name, [])
            if now - t < 3600  # Dernière heure
        ]
        
        return {
            'endpoint_name': endpoint_name,
            'requests_last_hour': len(recent_requests),
            'requests_last_minute': len([t for t in recent_requests if now - t < 60]),
            'rate_limit': self.endpoints[endpoint_name].rate_limit,
            'rate_limit_remaining': max(0, self.endpoints[endpoint_name].rate_limit - len([t for t in recent_requests if now - t < 60])),
            'last_request': max(recent_requests) if recent_requests else None
        }
```

### Connecteurs Spécialisés par Secteur

#### Connecteur E-commerce
```python
from typing import List
import pandas as pd

class EcommerceAPIConnector:
    """Connecteur spécialisé APIs e-commerce"""
    
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self._setup_ecommerce_endpoints()
    
    def _setup_ecommerce_endpoints(self) -> None:
        """Configure les endpoints e-commerce courants"""
        
        # Shopify
        shopify_endpoint = APIEndpoint(
            name="shopify",
            base_url="https://{shop_name}.myshopify.com/admin/api/2023-07",
            auth_type=AuthType.CUSTOM,
            credentials={"api_password": "YOUR_PRIVATE_APP_PASSWORD"},
            rate_limit=40,  # Shopify: 2 calls/second
            custom_headers={"X-Shopify-Access-Token": ""}
        )
        self.api_manager.register_endpoint(shopify_endpoint)
        
        # WooCommerce
        woocommerce_endpoint = APIEndpoint(
            name="woocommerce",
            base_url="https://yourstore.com/wp-json/wc/v3",
            auth_type=AuthType.BASIC_AUTH,
            credentials={"username": "consumer_key", "password": "consumer_secret"},
            rate_limit=100
        )
        self.api_manager.register_endpoint(woocommerce_endpoint)
        
        # Amazon MWS
        amazon_endpoint = APIEndpoint(
            name="amazon_mws",
            base_url="https://mws.amazonservices.com",
            auth_type=AuthType.CUSTOM,
            credentials={
                "access_key": "YOUR_ACCESS_KEY",
                "secret_key": "YOUR_SECRET_KEY",
                "merchant_id": "YOUR_MERCHANT_ID"
            },
            rate_limit=180  # Amazon: 3 calls/second
        )
        self.api_manager.register_endpoint(amazon_endpoint)
    
    def get_products(self, platform: str, limit: int = 50, **filters) -> List[Dict[str, Any]]:
        """Récupère liste produits depuis plateforme e-commerce"""
        
        if platform == "shopify":
            return self._get_shopify_products(limit, **filters)
        elif platform == "woocommerce":
            return self._get_woocommerce_products(limit, **filters)
        else:
            raise ValueError(f"Plateforme {platform} non supportée")
    
    def _get_shopify_products(self, limit: int, **filters) -> List[Dict[str, Any]]:
        """Récupère produits Shopify"""
        params = {"limit": min(limit, 250)}  # Limite Shopify
        params.update(filters)
        
        response = self.api_manager.make_request("shopify", "products.json", params=params)
        
        if "error" in response:
            return []
        
        return response.get("data", {}).get("products", [])
    
    def _get_woocommerce_products(self, limit: int, **filters) -> List[Dict[str, Any]]:
        """Récupère produits WooCommerce"""
        params = {"per_page": min(limit, 100)}  # Limite WooCommerce
        params.update(filters)
        
        response = self.api_manager.make_request("woocommerce", "products", params=params)
        
        if "error" in response:
            return []
        
        return response.get("data", [])
    
    def update_product_price(self, platform: str, product_id: str, 
                           new_price: float) -> Dict[str, Any]:
        """Met à jour prix d'un produit"""
        
        if platform == "shopify":
            return self._update_shopify_price(product_id, new_price)
        elif platform == "woocommerce":
            return self._update_woocommerce_price(product_id, new_price)
        else:
            raise ValueError(f"Plateforme {platform} non supportée")
    
    def _update_shopify_price(self, product_id: str, new_price: float) -> Dict[str, Any]:
        """Met à jour prix Shopify"""
        update_data = {
            "product": {
                "id": product_id,
                "variants": [{"price": str(new_price)}]
            }
        }
        
        response = self.api_manager.make_request(
            "shopify", 
            f"products/{product_id}.json",
            method="PUT",
            json_data=update_data
        )
        
        return response
    
    def get_orders(self, platform: str, date_from: datetime = None, 
                  date_to: datetime = None) -> List[Dict[str, Any]]:
        """Récupère commandes sur période"""
        
        params = {}
        if date_from:
            params['created_at_min'] = date_from.isoformat()
        if date_to:
            params['created_at_max'] = date_to.isoformat()
        
        if platform == "shopify":
            response = self.api_manager.make_request("shopify", "orders.json", params=params)
            return response.get("data", {}).get("orders", [])
            
        elif platform == "woocommerce":
            params.update({'after': date_from.isoformat() if date_from else None,
                          'before': date_to.isoformat() if date_to else None})
            response = self.api_manager.make_request("woocommerce", "orders", params=params)
            return response.get("data", [])
        
        return []
    
    def analyze_sales_performance(self, platform: str, days: int = 30) -> Dict[str, Any]:
        """Analyse performance ventes"""
        
        date_from = datetime.now() - timedelta(days=days)
        orders = self.get_orders(platform, date_from)
        
        if not orders:
            return {'error': 'Aucune commande trouvée'}
        
        # Conversion en DataFrame pour analyse
        df_orders = pd.DataFrame(orders)
        
        # Calculs métriques
        total_revenue = df_orders['total_price'].astype(float).sum()
        total_orders = len(df_orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Analyse par jour
        df_orders['created_date'] = pd.to_datetime(df_orders['created_at']).dt.date
        daily_sales = df_orders.groupby('created_date').agg({
            'total_price': ['count', 'sum']
        }).round(2)
        
        return {
            'period_days': days,
            'total_revenue': round(total_revenue, 2),
            'total_orders': total_orders,
            'avg_order_value': round(avg_order_value, 2),
            'daily_sales': daily_sales.to_dict(),
            'top_products': self._get_top_products_from_orders(df_orders)
        }
    
    def _get_top_products_from_orders(self, df_orders: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extrait top produits depuis commandes"""
        # Simplifié - dépend de la structure des données commandes
        products = []
        
        for _, order in df_orders.iterrows():
            for item in order.get('line_items', []):
                products.append({
                    'product_id': item.get('product_id'),
                    'name': item.get('name', ''),
                    'quantity': item.get('quantity', 0),
                    'price': item.get('price', 0)
                })
        
        if products:
            df_products = pd.DataFrame(products)
            top_products = df_products.groupby(['product_id', 'name']).agg({
                'quantity': 'sum',
                'price': 'mean'
            }).sort_values('quantity', ascending=False).head(10)
            
            return top_products.reset_index().to_dict('records')
        
        return []
```

#### Connecteur Marketing Digital
```python
class MarketingAPIConnector:
    """Connecteur spécialisé APIs marketing digital"""
    
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self._setup_marketing_endpoints()
    
    def _setup_marketing_endpoints(self) -> None:
        """Configure endpoints marketing"""
        
        # Google Ads
        google_ads_endpoint = APIEndpoint(
            name="google_ads",
            base_url="https://googleads.googleapis.com/v14",
            auth_type=AuthType.OAUTH2,
            credentials={
                "access_token": "YOUR_ACCESS_TOKEN",
                "refresh_token": "YOUR_REFRESH_TOKEN",
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET"
            },
            rate_limit=1000
        )
        self.api_manager.register_endpoint(google_ads_endpoint)
        
        # Facebook Ads
        facebook_endpoint = APIEndpoint(
            name="facebook_ads",
            base_url="https://graph.facebook.com/v18.0",
            auth_type=AuthType.API_KEY,
            credentials={"api_key": "YOUR_ACCESS_TOKEN"},
            rate_limit=200
        )
        self.api_manager.register_endpoint(facebook_endpoint)
        
        # Google Analytics
        analytics_endpoint = APIEndpoint(
            name="google_analytics",
            base_url="https://analyticsreporting.googleapis.com/v4",
            auth_type=AuthType.OAUTH2,
            credentials={
                "access_token": "YOUR_ACCESS_TOKEN",
                "refresh_token": "YOUR_REFRESH_TOKEN"
            },
            rate_limit=100
        )
        self.api_manager.register_endpoint(analytics_endpoint)
    
    def get_campaign_performance(self, platform: str, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Récupère performance campagnes"""
        
        if platform == "google_ads":
            return self._get_google_ads_performance(date_range)
        elif platform == "facebook_ads":
            return self._get_facebook_ads_performance(date_range)
        else:
            raise ValueError(f"Plateforme {platform} non supportée")
    
    def _get_google_ads_performance(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Performance Google Ads"""
        query_data = {
            "query": f"""
                SELECT 
                    campaign.name,
                    campaign.id,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign
                WHERE segments.date BETWEEN '{date_range['start_date']}' AND '{date_range['end_date']}'
            """
        }
        
        response = self.api_manager.make_request(
            "google_ads", 
            f"customers/{self.customer_id}/googleAds:search",
            method="POST",
            json_data=query_data
        )
        
        return response
    
    def _get_facebook_ads_performance(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Performance Facebook Ads"""
        params = {
            'fields': 'campaign_name,impressions,clicks,spend,actions',
            'time_range': json.dumps({
                'since': date_range['start_date'],
                'until': date_range['end_date']
            }),
            'level': 'campaign'
        }
        
        response = self.api_manager.make_request(
            "facebook_ads",
            f"act_{self.ad_account_id}/insights",
            params=params
        )
        
        return response
    
    def optimize_campaign_budget(self, platform: str, campaign_id: str, 
                                new_budget: float) -> Dict[str, Any]:
        """Optimise budget campagne"""
        
        if platform == "google_ads":
            return self._update_google_ads_budget(campaign_id, new_budget)
        elif platform == "facebook_ads":
            return self._update_facebook_budget(campaign_id, new_budget)
    
    def get_audience_insights(self, platform: str, audience_id: str = None) -> Dict[str, Any]:
        """Récupère insights audience"""
        
        if platform == "facebook_ads":
            params = {'fields': 'age,gender,country,interests'}
            if audience_id:
                path = f"{audience_id}/insights"
            else:
                path = "insights"
            
            response = self.api_manager.make_request("facebook_ads", path, params=params)
            return response
        
        return {'error': 'Plateforme non supportée pour insights audience'}
```

### Système de Monitoring et Alerting

#### Moniteur de Santé APIs
```python
import threading
from datetime import datetime
import schedule

class APIHealthMonitor:
    """Moniteur de santé des APIs avec alerting"""
    
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self.health_history = {}
        self.alert_thresholds = {
            'response_time_ms': 5000,  # 5 secondes
            'error_rate_percent': 10,   # 10%
            'consecutive_failures': 3
        }
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def start_monitoring(self, check_interval_minutes: int = 5) -> None:
        """Démarre monitoring automatique"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Programmation des checks
        schedule.every(check_interval_minutes).minutes.do(self._check_all_endpoints)
        
        # Thread de monitoring
        self.monitoring_thread = threading.Thread(target=self._run_monitoring)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info(f"Monitoring démarré avec intervalle {check_interval_minutes} min")
    
    def stop_monitoring(self) -> None:
        """Arrête le monitoring"""
        self.monitoring_active = False
        schedule.clear()
        
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        logger.info("Monitoring arrêté")
    
    def _run_monitoring(self) -> None:
        """Boucle de monitoring"""
        while self.monitoring_active:
            schedule.run_pending()
            time.sleep(1)
    
    def _check_all_endpoints(self) -> None:
        """Vérifie santé de tous les endpoints"""
        logger.info("🔍 Vérification santé APIs...")
        
        for endpoint_name in self.api_manager.endpoints.keys():
            health_status = self._check_endpoint_health(endpoint_name)
            self._record_health_status(endpoint_name, health_status)
            self._evaluate_alerts(endpoint_name, health_status)
    
    def _check_endpoint_health(self, endpoint_name: str) -> Dict[str, Any]:
        """Vérifie santé d'un endpoint spécifique"""
        start_time = time.time()
        
        try:
            test_result = self.api_manager.test_endpoint(endpoint_name)
            response_time = (time.time() - start_time) * 1000  # en ms
            
            return {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint_name,
                'status': test_result['status'],
                'response_time_ms': response_time,
                'error_message': test_result.get('error', None)
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint_name,
                'status': 'error',
                'response_time_ms': (time.time() - start_time) * 1000,
                'error_message': str(e)
            }
    
    def _record_health_status(self, endpoint_name: str, health_status: Dict[str, Any]) -> None:
        """Enregistre statut de santé"""
        if endpoint_name not in self.health_history:
            self.health_history[endpoint_name] = []
        
        # Garde seulement les 100 derniers checks
        self.health_history[endpoint_name].append(health_status)
        if len(self.health_history[endpoint_name]) > 100:
            self.health_history[endpoint_name] = self.health_history[endpoint_name][-100:]
    
    def _evaluate_alerts(self, endpoint_name: str, current_status: Dict[str, Any]) -> None:
        """Évalue et déclenche alertes si nécessaire"""
        history = self.health_history.get(endpoint_name, [])
        
        # Alerte temps de réponse élevé
        if current_status['response_time_ms'] > self.alert_thresholds['response_time_ms']:
            self._send_alert('high_response_time', endpoint_name, current_status)
        
        # Alerte taux d'erreur élevé
        if len(history) >= 10:
            recent_errors = [s for s in history[-10:] if s['status'] != 'success']
            error_rate = (len(recent_errors) / 10) * 100
            
            if error_rate > self.alert_thresholds['error_rate_percent']:
                self._send_alert('high_error_rate', endpoint_name, {
                    'error_rate_percent': error_rate,
                    'recent_errors': recent_errors
                })
        
        # Alerte échecs consécutifs
        consecutive_failures = 0
        for status in reversed(history):
            if status['status'] != 'success':
                consecutive_failures += 1
            else:
                break
        
        if consecutive_failures >= self.alert_thresholds['consecutive_failures']:
            self._send_alert('consecutive_failures', endpoint_name, {
                'consecutive_failures': consecutive_failures,
                'last_success': self._get_last_success_time(history)
            })
    
    def _send_alert(self, alert_type: str, endpoint_name: str, details: Dict[str, Any]) -> None:
        """Envoie alerte"""
        alert_message = f"""
        🚨 ALERTE API: {alert_type.upper()}
        
        Endpoint: {endpoint_name}
        Timestamp: {datetime.now().isoformat()}
        
        Détails: {json.dumps(details, indent=2)}
        """
        
        logger.warning(f"ALERTE {alert_type} pour {endpoint_name}")
        
        # Ici on pourrait intégrer avec systèmes d'alerting
        # (Slack, email, PagerDuty, etc.)
    
    def get_health_dashboard(self) -> Dict[str, Any]:
        """Génère dashboard santé APIs"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'endpoints': {}
        }
        
        for endpoint_name, history in self.health_history.items():
            if not history:
                continue
                
            recent_history = history[-20:]  # 20 derniers checks
            success_count = len([h for h in recent_history if h['status'] == 'success'])
            
            dashboard['endpoints'][endpoint_name] = {
                'current_status': history[-1]['status'],
                'uptime_percent': (success_count / len(recent_history)) * 100,
                'avg_response_time_ms': sum(h['response_time_ms'] for h in recent_history) / len(recent_history),
                'last_check': history[-1]['timestamp'],
                'total_checks': len(history)
            }
        
        return dashboard
    
    def _get_last_success_time(self, history: List[Dict[str, Any]]) -> Optional[str]:
        """Trouve timestamp du dernier succès"""
        for status in reversed(history):
            if status['status'] == 'success':
                return status['timestamp']
        return None

# Exemple d'utilisation complète
def exemple_integration_apis():
    """Exemple complet d'intégration et monitoring APIs"""
    
    # Initialisation
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    api_manager = APIManager(redis_client)
    
    # Configuration connecteurs
    ecommerce_connector = EcommerceAPIConnector(api_manager)
    marketing_connector = MarketingAPIConnector(api_manager)
    
    # Monitoring
    health_monitor = APIHealthMonitor(api_manager)
    health_monitor.start_monitoring(check_interval_minutes=2)
    
    # Tests de connectivité
    print("🧪 Tests de connectivité...")
    for endpoint_name in api_manager.endpoints.keys():
        test_result = api_manager.test_endpoint(endpoint_name)
        print(f"  {endpoint_name}: {test_result['status']}")
    
    # Exemples d'utilisation
    print("\n📊 Récupération données e-commerce...")
    try:
        products = ecommerce_connector.get_products("shopify", limit=10)
        print(f"  Produits récupérés: {len(products)}")
        
        sales_analysis = ecommerce_connector.analyze_sales_performance("shopify", days=7)
        print(f"  CA 7 derniers jours: {sales_analysis.get('total_revenue', 0)}€")
        
    except Exception as e:
        print(f"  Erreur e-commerce: {e}")
    
    # Dashboard santé
    print("\n🏥 Dashboard santé APIs...")
    dashboard = health_monitor.get_health_dashboard()
    for endpoint, health in dashboard['endpoints'].items():
        print(f"  {endpoint}: {health['current_status']} (uptime: {health['uptime_percent']:.1f}%)")
    
    # Sauvegarde rapport
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'api_health_report_{timestamp}.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"\n✅ Intégrations configurées - Rapport: api_health_report_{timestamp}.json")
    
    return {
        'api_manager': api_manager,
        'connectors': {
            'ecommerce': ecommerce_connector,
            'marketing': marketing_connector
        },
        'monitor': health_monitor,
        'dashboard': dashboard
    }

if __name__ == "__main__":
    results = exemple_integration_apis()
    print("API Integration Setup Complete!")
```

Cette documentation complète couvre l'intégration d'APIs externes avec l'espace Perplexity AI, incluant la sécurisation, la performance, le monitoring et des connecteurs spécialisés pour différents secteurs métier.