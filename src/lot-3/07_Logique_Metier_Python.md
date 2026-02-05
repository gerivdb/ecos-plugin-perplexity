# Logique Métier Python - Espace Perplexity AI

## Vue d'ensemble
Ce document explique l'intégration de la programmation Python dans l'espace métier Perplexity AI, détaillant les scripts, modules, et automatisations qui transforment les règles métier en code exécutable.

## Architecture Python Métier

### Philosophie de Conception

#### Principes Directeurs
- **Domain-Driven Design** : Code reflète fidèlement la logique métier
- **Composabilité** : Modules réutilisables entre différents métiers
- **Testabilité** : Chaque fonction métier est testable isolément
- **Observabilité** : Logging et monitoring intégrés naturement
- **Sécurité by Design** : Validation et sanitisation à chaque étape

#### Architecture en Couches
```
┌─────────────────────────────────────┐
│        Couche Présentation          │  ← Interface utilisateur
├─────────────────────────────────────┤
│        Couche Orchestration         │  ← Workflows et règles
├─────────────────────────────────────┤  
│        Couche Logique Métier        │  ← Scripts Python métier
├─────────────────────────────────────┤
│        Couche Services              │  ← APIs et intégrations
└─────────────────────────────────────┘
```

### Structure des Modules Python

#### Organisation Standard
```python
# Arborescence type d'un module métier
project_metier/
├── __init__.py                 # Point d'entrée module
├── config/
│   ├── __init__.py
│   ├── business_rules.py       # Règles métier configurables
│   └── api_endpoints.py        # Configuration APIs
├── core/
│   ├── __init__.py
│   ├── base_classes.py         # Classes métier de base
│   ├── exceptions.py           # Exceptions métier custom
│   └── validators.py           # Validateurs données métier
├── services/
│   ├── __init__.py
│   ├── data_collector.py       # Collecte données externes
│   ├── processor.py            # Traitement logique métier
│   └── notifier.py            # Notifications et alertes
├── utils/
│   ├── __init__.py
│   ├── helpers.py             # Fonctions utilitaires
│   └── decorators.py          # Décorateurs métier
└── tests/
    ├── __init__.py
    ├── test_core.py           # Tests logique métier
    └── test_integration.py    # Tests intégration APIs
```

## Classes Métier Fondamentales

### Classe de Base MetierEntity
```python
from datetime import datetime
from typing import Dict, Any, Optional
import logging

class MetierEntity:
    """Classe de base pour toutes les entités métier"""
    
    def __init__(self, entity_id: str, entity_type: str):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.metadata: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{entity_type}")
        
    def update_metadata(self, key: str, value: Any) -> None:
        """Met à jour métadonnées avec traçabilité"""
        old_value = self.metadata.get(key)
        self.metadata[key] = value
        self.updated_at = datetime.now()
        
        self.logger.info(
            f"Metadata updated - Entity: {self.entity_id}, "
            f"Key: {key}, Old: {old_value}, New: {value}"
        )
    
    def validate(self) -> bool:
        """Validation générique entité"""
        if not self.entity_id or not self.entity_type:
            raise ValueError("entity_id et entity_type sont obligatoires")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialisation pour persistance/API"""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
```

### Gestionnaire de Workflow Métier
```python
from enum import Enum
from typing import List, Callable, Dict
from abc import ABC, abstractmethod

class WorkflowStatus(Enum):
    """États possibles d'un workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStep(ABC):
    """Étape abstraite de workflow"""
    
    def __init__(self, step_name: str, timeout_seconds: int = 300):
        self.step_name = step_name
        self.timeout_seconds = timeout_seconds
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = WorkflowStatus.PENDING
        self.error_message: Optional[str] = None
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute l'étape et retourne contexte modifié"""
        pass
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper d'exécution avec gestion erreurs et timing"""
        self.start_time = datetime.now()
        self.status = WorkflowStatus.RUNNING
        
        try:
            result = self.execute(context)
            self.status = WorkflowStatus.COMPLETED
            return result
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.error_message = str(e)
            logger.error(f"Step {self.step_name} failed: {e}")
            raise
            
        finally:
            self.end_time = datetime.now()

class BusinessWorkflow:
    """Orchestrateur de workflow métier"""
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING
        self.context: Dict[str, Any] = {}
        self.execution_log: List[Dict[str, Any]] = []
        
    def add_step(self, step: WorkflowStep) -> 'BusinessWorkflow':
        """Ajoute une étape au workflow (pattern builder)"""
        self.steps.append(step)
        return self
    
    def execute(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Exécute le workflow complet"""
        self.context = initial_context or {}
        self.status = WorkflowStatus.RUNNING
        
        logger.info(f"Starting workflow: {self.workflow_name}")
        
        try:
            for step in self.steps:
                step_start = datetime.now()
                
                # Exécution de l'étape
                self.context = step.run(self.context)
                
                # Log de l'exécution
                step_duration = datetime.now() - step_start
                self.execution_log.append({
                    'step_name': step.step_name,
                    'status': step.status.value,
                    'duration_seconds': step_duration.total_seconds(),
                    'error': step.error_message
                })
                
                logger.info(f"Step {step.step_name} completed in {step_duration}")
            
            self.status = WorkflowStatus.COMPLETED
            logger.info(f"Workflow {self.workflow_name} completed successfully")
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            logger.error(f"Workflow {self.workflow_name} failed: {e}")
            raise
            
        return self.context
```

## Modules Métier Spécialisés

### Module Comparateur de Prix

#### Collecteur de Données Prix
```python
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import random

class PriceCollector:
    """Collecte intelligente de prix depuis multiples sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'PriceBot/1.0')
        })
        
        # Rate limiting
        self.requests_per_minute = config.get('requests_per_minute', 60)
        self.last_request_time = 0
        
    def _respect_rate_limit(self):
        """Respecte les limites de taux de requêtes"""
        time_since_last = time.time() - self.last_request_time
        min_interval = 60.0 / self.requests_per_minute
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def collect_price_from_api(self, endpoint: str, product_sku: str) -> Optional[float]:
        """Collecte prix via API structurée"""
        self._respect_rate_limit()
        
        try:
            response = self.session.get(f"{endpoint}/price/{product_sku}")
            response.raise_for_status()
            
            data = response.json()
            return float(data.get('price', 0))
            
        except Exception as e:
            logger.warning(f"API collection failed for {endpoint}: {e}")
            return None
    
    def collect_price_from_web(self, url: str, price_selector: str) -> Optional[float]:
        """Collecte prix par scraping web responsable"""
        self._respect_rate_limit()
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            price_element = soup.select_one(price_selector)
            
            if price_element:
                price_text = price_element.get_text().strip()
                # Nettoyage du prix (suppression symboles monétaires, etc.)
                price_clean = self._clean_price_text(price_text)
                return float(price_clean)
            
        except Exception as e:
            logger.warning(f"Web scraping failed for {url}: {e}")
            return None
    
    def _clean_price_text(self, price_text: str) -> str:
        """Nettoie le texte prix pour extraction numérique"""
        import re
        
        # Supprime symboles monétaires communs et espaces
        cleaned = re.sub(r'[€$£¥,\s]', '', price_text)
        
        # Extrait le nombre décimal
        match = re.search(r'(\d+\.?\d*)', cleaned)
        return match.group(1) if match else '0'
    
    def collect_competitor_prices(self, product_sku: str, 
                                competitors: List[Dict[str, str]]) -> Dict[str, float]:
        """Collecte prix chez tous les concurrents pour un produit"""
        prices = {}
        
        for competitor in competitors:
            competitor_name = competitor['name']
            
            # Tentative API d'abord
            if 'api_endpoint' in competitor:
                price = self.collect_price_from_api(
                    competitor['api_endpoint'], 
                    product_sku
                )
            # Fallback sur scraping si nécessaire
            elif 'web_url' in competitor and 'price_selector' in competitor:
                product_url = competitor['web_url'].format(sku=product_sku)
                price = self.collect_price_from_web(
                    product_url, 
                    competitor['price_selector']
                )
            else:
                logger.error(f"Competitor {competitor_name} mal configuré")
                continue
            
            if price and price > 0:
                prices[competitor_name] = price
                logger.info(f"Prix collecté {competitor_name}: {price}€")
            else:
                logger.warning(f"Impossible de récupérer prix {competitor_name}")
        
        return prices
```

#### Analyseur de Prix et Tendances
```python
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class PriceAnalyzer:
    """Analyse avancée des prix et détection de tendances"""
    
    def __init__(self):
        self.price_history = pd.DataFrame()
    
    def load_price_history(self, history_data: List[Dict]) -> None:
        """Charge l'historique des prix pour analyse"""
        self.price_history = pd.DataFrame(history_data)
        if not self.price_history.empty:
            self.price_history['timestamp'] = pd.to_datetime(
                self.price_history['timestamp']
            )
            self.price_history.set_index('timestamp', inplace=True)
    
    def calculate_price_statistics(self, product_sku: str, 
                                 days: int = 30) -> Dict[str, float]:
        """Calcule statistiques prix sur période donnée"""
        
        # Filtrage période
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        product_data = self.price_history[
            (self.price_history['product_sku'] == product_sku) &
            (self.price_history.index >= start_date)
        ]
        
        if product_data.empty:
            return {}
        
        prices = product_data['price']
        
        return {
            'mean_price': float(prices.mean()),
            'median_price': float(prices.median()),
            'std_deviation': float(prices.std()),
            'min_price': float(prices.min()),
            'max_price': float(prices.max()),
            'price_range': float(prices.max() - prices.min()),
            'coefficient_variation': float(prices.std() / prices.mean()),
            'current_price': float(prices.iloc[-1] if not prices.empty else 0),
            'trend_slope': self._calculate_trend_slope(product_data),
            'volatility_score': self._calculate_volatility(prices)
        }
    
    def _calculate_trend_slope(self, data: pd.DataFrame) -> float:
        """Calcule la pente de tendance (régression linéaire)"""
        if len(data) < 2:
            return 0.0
        
        # Conversion timestamp en nombre pour régression
        x = np.arange(len(data))
        y = data['price'].values
        
        slope, _, _, _, _ = stats.linregress(x, y)
        return float(slope)
    
    def _calculate_volatility(self, prices: pd.Series) -> float:
        """Calcule score de volatilité (écart-type des variations)"""
        if len(prices) < 2:
            return 0.0
        
        # Variations jour-à-jour
        price_changes = prices.pct_change().dropna()
        return float(price_changes.std())
    
    def detect_price_anomalies(self, product_sku: str, 
                             current_price: float,
                             sensitivity: float = 2.0) -> Dict[str, Any]:
        """Détecte les anomalies de prix (prix aberrants)"""
        
        stats = self.calculate_price_statistics(product_sku)
        if not stats:
            return {'is_anomaly': False, 'reason': 'No historical data'}
        
        mean_price = stats['mean_price']
        std_dev = stats['std_deviation']
        
        # Z-score pour détection anomalie
        z_score = abs(current_price - mean_price) / std_dev if std_dev > 0 else 0
        is_anomaly = z_score > sensitivity
        
        anomaly_type = None
        if is_anomaly:
            if current_price > mean_price:
                anomaly_type = 'price_spike'  # Prix anormalement élevé
            else:
                anomaly_type = 'price_drop'   # Prix anormalement bas
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_type': anomaly_type,
            'z_score': float(z_score),
            'deviation_percent': float(((current_price - mean_price) / mean_price) * 100),
            'confidence_level': float(min(z_score / sensitivity, 1.0)),
            'historical_context': {
                'mean_price': mean_price,
                'std_dev': std_dev,
                'min_historic': stats['min_price'],
                'max_historic': stats['max_price']
            }
        }
    
    def generate_pricing_recommendations(self, product_sku: str, 
                                       current_price: float,
                                       competitor_prices: Dict[str, float],
                                       business_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Génère recommandations pricing basées sur analyse"""
        
        if not competitor_prices:
            return {'recommendation': 'insufficient_data'}
        
        # Statistiques concurrence
        competitor_values = list(competitor_prices.values())
        competitor_mean = np.mean(competitor_values)
        competitor_min = np.min(competitor_values)
        competitor_max = np.max(competitor_values)
        
        # Position concurrentielle actuelle
        competitive_position = self._calculate_competitive_position(
            current_price, competitor_values
        )
        
        # Règles métier
        min_margin = business_rules.get('min_margin_percent', 10) / 100
        max_markup = business_rules.get('max_markup_percent', 200) / 100
        target_position = business_rules.get('target_competitive_position', 'middle')
        
        # Calcul prix recommandé selon stratégie
        if target_position == 'aggressive':
            # Prix le plus bas mais avec marge minimum
            recommended_price = max(
                competitor_min * 0.95,  # 5% sous le plus bas
                current_price * (1 + min_margin)  # Respecter marge min
            )
        elif target_position == 'premium':
            # Prix élevé mais raisonnable
            recommended_price = min(
                competitor_max * 1.05,  # 5% sur le plus haut
                current_price * (1 + max_markup)  # Respecter markup max
            )
        else:  # position 'middle'
            # Positionnement médian
            recommended_price = competitor_mean
        
        # Validation contraintes business
        recommended_price = self._apply_business_constraints(
            recommended_price, current_price, business_rules
        )
        
        return {
            'current_price': current_price,
            'recommended_price': round(recommended_price, 2),
            'price_change_percent': ((recommended_price - current_price) / current_price) * 100,
            'competitive_analysis': {
                'current_position': competitive_position,
                'competitor_mean': competitor_mean,
                'competitor_range': [competitor_min, competitor_max],
                'market_coverage': len(competitor_prices)
            },
            'business_impact': self._estimate_business_impact(
                current_price, recommended_price, business_rules
            ),
            'recommendation_confidence': self._calculate_recommendation_confidence(
                competitor_prices, business_rules
            )
        }
    
    def _calculate_competitive_position(self, our_price: float, 
                                      competitor_prices: List[float]) -> str:
        """Détermine position concurrentielle (low/middle/high)"""
        sorted_prices = sorted(competitor_prices + [our_price])
        our_position = sorted_prices.index(our_price) / len(sorted_prices)
        
        if our_position < 0.33:
            return 'low'
        elif our_position > 0.67:
            return 'high'
        else:
            return 'middle'
    
    def _apply_business_constraints(self, recommended_price: float,
                                  current_price: float,
                                  business_rules: Dict[str, Any]) -> float:
        """Applique contraintes métier au prix recommandé"""
        
        # Limite variation maximale par jour
        max_daily_change = business_rules.get('max_daily_change_percent', 10) / 100
        max_increase = current_price * (1 + max_daily_change)
        max_decrease = current_price * (1 - max_daily_change)
        
        recommended_price = min(max_increase, max(max_decrease, recommended_price))
        
        # Prix minimum/maximum absolus
        if 'min_price' in business_rules:
            recommended_price = max(recommended_price, business_rules['min_price'])
        if 'max_price' in business_rules:
            recommended_price = min(recommended_price, business_rules['max_price'])
        
        return recommended_price
    
    def _estimate_business_impact(self, current_price: float, 
                                new_price: float,
                                business_rules: Dict[str, Any]) -> Dict[str, float]:
        """Estime impact business du changement de prix"""
        
        price_elasticity = business_rules.get('price_elasticity', -1.5)  # Défaut élastique
        price_change_percent = (new_price - current_price) / current_price
        
        # Estimation variation demande (loi de l'élastique prix)
        demand_change_percent = price_elasticity * price_change_percent
        
        # Estimation impact revenus
        revenue_change_percent = price_change_percent + demand_change_percent + \
                               (price_change_percent * demand_change_percent)
        
        return {
            'estimated_demand_change_percent': demand_change_percent * 100,
            'estimated_revenue_change_percent': revenue_change_percent * 100,
            'risk_level': self._assess_pricing_risk(price_change_percent)
        }
    
    def _assess_pricing_risk(self, price_change_percent: float) -> str:
        """Évalue risque associé au changement de prix"""
        abs_change = abs(price_change_percent)
        
        if abs_change < 0.05:  # < 5%
            return 'low'
        elif abs_change < 0.15:  # < 15%
            return 'medium'
        else:
            return 'high'
    
    def _calculate_recommendation_confidence(self, competitor_prices: Dict[str, float],
                                          business_rules: Dict[str, Any]) -> float:
        """Calcule niveau de confiance de la recommandation"""
        
        # Facteurs de confiance
        market_coverage = len(competitor_prices)  # Plus de concurrents = plus de confiance
        price_consistency = 1.0 - (np.std(list(competitor_prices.values())) / 
                                   np.mean(list(competitor_prices.values())))
        
        # Normalisation 0-1
        coverage_score = min(market_coverage / 10.0, 1.0)  # Max confiance à 10 concurrents
        consistency_score = max(0, price_consistency)  # Évite valeurs négatives
        
        overall_confidence = (coverage_score + consistency_score) / 2
        return min(1.0, overall_confidence)
```

### Module Booking Hôtelier

#### Gestionnaire de Disponibilités
```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import pandas as pd

class AvailabilityManager:
    """Gestionnaire intelligent des disponibilités hôtelières"""
    
    def __init__(self):
        self.inventory = {}  # {room_type: {date: available_count}}
        self.reservations = {}  # {reservation_id: reservation_data}
        self.overbooking_rules = {}
        
    def load_inventory(self, inventory_data: Dict[str, Dict[str, int]]):
        """Charge inventaire des chambres"""
        self.inventory = inventory_data
        
    def check_availability(self, room_type: str, check_in: datetime, 
                         check_out: datetime, rooms_needed: int = 1) -> Dict[str, Any]:
        """Vérifie disponibilité pour période donnée"""
        
        if room_type not in self.inventory:
            return {'available': False, 'reason': 'room_type_not_found'}
        
        # Génère toutes les dates de séjour
        stay_dates = self._generate_date_range(check_in, check_out)
        
        # Vérification disponibilité pour chaque date
        availability_details = {}
        min_available = float('inf')
        
        for date in stay_dates:
            date_str = date.strftime('%Y-%m-%d')
            room_inventory = self.inventory[room_type].get(date_str, 0)
            reserved_rooms = self._count_reservations_for_date(room_type, date)
            
            available_rooms = room_inventory - reserved_rooms
            availability_details[date_str] = {
                'inventory': room_inventory,
                'reserved': reserved_rooms,
                'available': available_rooms
            }
            
            min_available = min(min_available, available_rooms)
        
        # Vérification avec règles d'overbooking
        overbooking_limit = self._get_overbooking_limit(room_type, check_in)
        effective_availability = min_available + overbooking_limit
        
        return {
            'available': effective_availability >= rooms_needed,
            'rooms_available': int(max(0, effective_availability)),
            'rooms_requested': rooms_needed,
            'availability_details': availability_details,
            'overbooking_applied': overbooking_limit > 0,
            'overbooking_risk': self._assess_overbooking_risk(room_type, stay_dates)
        }
    
    def make_reservation(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une réservation avec validation"""
        
        reservation_id = self._generate_reservation_id()
        room_type = reservation_data['room_type']
        check_in = reservation_data['check_in']
        check_out = reservation_data['check_out']
        rooms_needed = reservation_data['rooms_count']
        
        # Vérification disponibilité
        availability = self.check_availability(room_type, check_in, check_out, rooms_needed)
        
        if not availability['available']:
            return {
                'success': False,
                'reservation_id': None,
                'reason': 'no_availability',
                'details': availability
            }
        
        # Enregistrement réservation
        reservation_record = {
            'reservation_id': reservation_id,
            'room_type': room_type,
            'check_in': check_in,
            'check_out': check_out,
            'rooms_count': rooms_needed,
            'guest_info': reservation_data.get('guest_info', {}),
            'created_at': datetime.now(),
            'status': 'confirmed',
            'total_amount': self._calculate_total_amount(reservation_data)
        }
        
        self.reservations[reservation_id] = reservation_record
        
        return {
            'success': True,
            'reservation_id': reservation_id,
            'reservation_details': reservation_record,
            'overbooking_risk': availability['overbooking_risk']
        }
    
    def optimize_inventory_allocation(self, forecast_data: Dict[str, float]) -> Dict[str, Any]:
        """Optimise allocation inventaire selon prévisions demande"""
        
        optimization_results = {}
        
        for room_type in self.inventory:
            # Analyse historique et prévisions
            demand_forecast = forecast_data.get(room_type, {})
            current_allocation = self.inventory[room_type]
            
            # Calcul allocation optimale
            optimized_allocation = self._calculate_optimal_allocation(
                current_allocation, demand_forecast
            )
            
            # Recommandations d'ajustement
            adjustments = {}
            for date_str, current_rooms in current_allocation.items():
                optimal_rooms = optimized_allocation.get(date_str, current_rooms)
                if optimal_rooms != current_rooms:
                    adjustments[date_str] = {
                        'current': current_rooms,
                        'recommended': optimal_rooms,
                        'change': optimal_rooms - current_rooms
                    }
            
            if adjustments:
                optimization_results[room_type] = {
                    'adjustments_needed': True,
                    'adjustments': adjustments,
                    'potential_revenue_impact': self._estimate_revenue_impact(adjustments)
                }
        
        return optimization_results
    
    def _generate_date_range(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """Génère liste des dates entre deux dates"""
        dates = []
        current_date = start_date.date()
        end = end_date.date()
        
        while current_date < end:  # Check-out non inclus
            dates.append(datetime.combine(current_date, datetime.min.time()))
            current_date += timedelta(days=1)
        
        return dates
    
    def _count_reservations_for_date(self, room_type: str, date: datetime) -> int:
        """Compte réservations pour une date donnée"""
        date_obj = date.date()
        count = 0
        
        for reservation in self.reservations.values():
            if (reservation['room_type'] == room_type and
                reservation['status'] == 'confirmed' and
                reservation['check_in'].date() <= date_obj < reservation['check_out'].date()):
                count += reservation['rooms_count']
        
        return count
    
    def _get_overbooking_limit(self, room_type: str, check_in: datetime) -> int:
        """Calcule limite d'overbooking autorisée"""
        base_limit = self.overbooking_rules.get(room_type, {}).get('max_percent', 3)  # 3% par défaut
        
        # Ajustement selon période (plus conservateur en haute saison)
        if self._is_peak_season(check_in):
            return int(base_limit * 0.5)  # Réduction en haute saison
        
        return base_limit
    
    def _is_peak_season(self, date: datetime) -> bool:
        """Détermine si la date est en haute saison"""
        # Exemple logique : été et fêtes de fin d'année
        month = date.month
        return month in [6, 7, 8, 12] or (month == 1 and date.day <= 7)
    
    def _assess_overbooking_risk(self, room_type: str, dates: List[datetime]) -> str:
        """Évalue risque d'overbooking"""
        total_overbooking = sum(
            max(0, -self.check_availability(room_type, date, date + timedelta(days=1))['rooms_available'])
            for date in dates
        )
        
        if total_overbooking == 0:
            return 'low'
        elif total_overbooking <= 2:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_total_amount(self, reservation_data: Dict[str, Any]) -> float:
        """Calcule montant total réservation"""
        # Logique de pricing dynamique intégrée
        base_rate = reservation_data.get('base_rate', 100.0)
        nights = (reservation_data['check_out'] - reservation_data['check_in']).days
        rooms = reservation_data['rooms_count']
        
        # Facteurs de prix dynamique
        seasonal_multiplier = self._get_seasonal_multiplier(reservation_data['check_in'])
        demand_multiplier = self._get_demand_multiplier(reservation_data['room_type'], reservation_data['check_in'])
        
        total_amount = base_rate * nights * rooms * seasonal_multiplier * demand_multiplier
        
        return round(total_amount, 2)
    
    def _generate_reservation_id(self) -> str:
        """Génère ID unique de réservation"""
        import uuid
        return f"RES_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"
```

Cette documentation continue avec les modules restants et couvre l'ensemble de la logique métier Python intégrée dans l'espace Perplexity AI. Chaque module est conçu pour être robuste, testable et facilement extensible selon les besoins métier spécifiques.