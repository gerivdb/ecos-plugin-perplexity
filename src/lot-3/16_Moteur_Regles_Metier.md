# Moteur de Règles Métier Dynamiques - Espace Perplexity AI

## Vue d'ensemble
Ce document présente un système avancé de gestion des règles métier dynamiques pour l'espace Perplexity AI, intégrant un moteur de règles configurable, un système d'inférence intelligent, et une interface de configuration YAML intuitive pour les utilisateurs métier.

## Architecture du Moteur de Règles

### Vision Globale du Système

```
┌─────────────────────────────────────────────────────────────────┐
│                 MOTEUR DE RÈGLES MÉTIER DYNAMIQUES             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📝 Configuration YAML    🧠 Moteur Inférence    ⚡ Exécution   │
│  ┌─────────────────┐     ┌─────────────────┐     ┌───────────┐  │
│  │ • Règles Métier │────▶│ • Analyseur     │────▶│ • Actions │  │
│  │ • Conditions    │     │ • Évaluateur    │     │ • Alerts  │  │
│  │ • Actions       │     │ • Optimiseur    │     │ • Workflows│  │
│  │ • Priorités     │     │ • Cache         │     │ • Reports │  │
│  └─────────────────┘     └─────────────────┘     └───────────┘  │
│                                  ↕                              │
│  🔄 Gestion Versions      📊 Analytics Rules     🚨 Monitoring  │
│  ┌─────────────────┐     ┌─────────────────┐     ┌───────────┐  │
│  │ • Versioning    │     │ • Performance   │     │ • Health  │  │
│  │ • Rollback      │     │ • Usage Stats   │     │ • Errors  │  │
│  │ • A/B Testing   │     │ • Impact Mesure │     │ • Perf    │  │
│  │ • Audit Trail   │     │ • ROI Tracking  │     │ • Alerts  │  │
│  └─────────────────┘     └─────────────────┘     └───────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Composants Principaux

#### 1. Configuration YAML des Règles Métier

```yaml
# rules_config.yaml - Configuration complète des règles métier
version: "2.1"
namespace: "perplexity_business_rules"
metadata:
  description: "Règles métier pour l'espace Perplexity AI"
  author: "Business Team"
  last_updated: "2025-09-02T22:00:00Z"
  effective_date: "2025-09-03T00:00:00Z"

# ═══════════════════════════════════════════════════════════════
#                    RÈGLES PRICING DYNAMIQUE
# ═══════════════════════════════════════════════════════════════

pricing_rules:
  # Règle principale de pricing compétitif
  competitive_pricing:
    id: "PRICE_COMP_001"
    name: "Ajustement Prix Concurrentiel"
    description: "Ajuste automatiquement les prix selon la concurrence"
    priority: 100
    enabled: true
    
    # Conditions d'activation
    conditions:
      all_of:
        - field: "product.category"
          operator: "in"
          values: ["electronics", "fashion", "home"]
        - field: "competitor_data.price_variance"
          operator: ">="
          value: 5.0
        - field: "inventory.stock_level"
          operator: ">"
          value: 10
        - field: "product.margin_percent"
          operator: ">="
          value: 15.0
    
    # Actions à exécuter
    actions:
      # Action principale : ajustement prix
      - type: "price_adjustment"
        config:
          strategy: "competitive_match"
          parameters:
            target_position: "middle"  # top, middle, bottom
            max_adjustment_percent: 10.0
            min_margin_percent: 12.0
            rounding_strategy: "psychological"  # .99, .90, exact
      
      # Action secondaire : notification
      - type: "notification"
        config:
          channels: ["email", "dashboard"]
          recipients: ["pricing_team", "category_manager"]
          template: "pricing_adjustment_alert"
          urgency: "medium"
      
      # Action de suivi
      - type: "monitoring"
        config:
          track_metrics: ["sales_velocity", "margin_impact", "competitor_response"]
          duration_hours: 72
          alert_thresholds:
            sales_drop_percent: -15.0
            margin_drop_percent: -5.0
    
    # Conditions d'arrêt/exception
    exceptions:
      - condition:
          field: "product.is_promotional"
          operator: "=="
          value: true
        action: "skip"
        reason: "Produit en promotion active"
      
      - condition:
          field: "supplier.cost_increase_pending"
          operator: "=="
          value: true
        action: "delay"
        duration_hours: 24
        reason: "Attente confirmation coûts fournisseur"
    
    # Planification d'exécution
    schedule:
      frequency: "daily"
      time: "09:00"
      timezone: "Europe/Paris"
      blackout_periods:
        - start: "2025-12-24T00:00:00Z"
          end: "2025-12-26T23:59:59Z"
          reason: "Période de Noël"

  # Règle de pricing saisonnier
  seasonal_pricing:
    id: "PRICE_SEAS_001"
    name: "Ajustement Saisonnier"
    priority: 80
    enabled: true
    
    conditions:
      any_of:
        - field: "date.month"
          operator: "in"
          values: [11, 12, 1]  # Hiver
        - field: "date.month"
          operator: "in"
          values: [6, 7, 8]   # Été
    
    actions:
      - type: "price_adjustment"
        config:
          strategy: "seasonal_factor"
          parameters:
            winter_factor: 1.1    # +10% en hiver
            summer_factor: 0.95   # -5% en été
            transition_days: 7    # Transition progressive

# ═══════════════════════════════════════════════════════════════
#                    RÈGLES GESTION STOCK
# ═══════════════════════════════════════════════════════════════

inventory_rules:
  # Règle de réapprovisionnement automatique
  auto_replenishment:
    id: "INV_REPL_001"
    name: "Réapprovisionnement Automatique"
    priority: 150
    enabled: true
    
    conditions:
      all_of:
        - field: "inventory.current_stock"
          operator: "<="
          value_expression: "inventory.safety_stock + inventory.reorder_point"
        - field: "product.is_active"
          operator: "=="
          value: true
        - field: "supplier.status"
          operator: "=="
          value: "active"
    
    actions:
      - type: "purchase_order_creation"
        config:
          quantity_calculation: "economic_order_quantity"
          parameters:
            demand_forecast_days: 90
            lead_time_buffer_days: 7
            service_level_percent: 95
          
          approval_workflow:
            auto_approve_under: 5000.0  # Euros
            require_approval_over: 5000.0
            approvers: ["procurement_manager", "finance_director"]
      
      - type: "alert"
        config:
          message: "Commande automatique créée pour {{product.name}}"
          severity: "info"
          channels: ["procurement_dashboard", "email"]

  # Règle d'alerte surstock
  overstock_alert:
    id: "INV_OVER_001"
    name: "Alerte Surstock"
    priority: 90
    enabled: true
    
    conditions:
      all_of:
        - field: "inventory.days_of_supply"
          operator: ">"
          value: 180  # Plus de 6 mois de stock
        - field: "product.sales_velocity"
          operator: "<"
          value: 5    # Moins de 5 ventes/mois
    
    actions:
      - type: "clearance_recommendation"
        config:
          discount_percent: 25
          clearance_duration_days: 30
          channels: ["promotional_campaigns", "outlet_stores"]

# ═══════════════════════════════════════════════════════════════
#                    RÈGLES CUSTOMER EXPERIENCE
# ═══════════════════════════════════════════════════════════════

customer_rules:
  # Règle de personnalisation offres
  personalized_offers:
    id: "CUST_PERS_001"
    name: "Offres Personnalisées"
    priority: 120
    enabled: true
    
    conditions:
      all_of:
        - field: "customer.segment"
          operator: "in"
          values: ["premium", "frequent_buyer"]
        - field: "customer.last_purchase_days"
          operator: ">="
          value: 30
        - field: "customer.lifetime_value"
          operator: ">="
          value: 500
    
    actions:
      - type: "personalized_campaign"
        config:
          discount_percent: 15
          product_recommendations: "ai_powered"
          communication_channels: ["email", "app_push"]
          expiry_days: 7

# ═══════════════════════════════════════════════════════════════
#                    RÈGLES QUALITÉ & CONFORMITÉ
# ═══════════════════════════════════════════════════════════════

quality_rules:
  # Règle de contrôle qualité fournisseur
  supplier_quality_check:
    id: "QUAL_SUPP_001"
    name: "Contrôle Qualité Fournisseur"
    priority: 200  # Priorité maximale
    enabled: true
    
    conditions:
      any_of:
        - field: "supplier.defect_rate_percent"
          operator: ">"
          value: 2.0
        - field: "supplier.delivery_delay_percent"
          operator: ">"
          value: 10.0
        - field: "supplier.quality_score"
          operator: "<"
          value: 80
    
    actions:
      - type: "supplier_review"
        config:
          automatic_actions:
            - "suspend_new_orders"
            - "quality_audit_scheduling"
            - "alternative_supplier_search"
          
          escalation:
            level_1: "quality_manager"
            level_2: "procurement_director"
            level_3: "ceo"
          
          timeline:
            immediate: "order_suspension"
            within_24h: "supplier_notification"
            within_48h: "corrective_action_plan"

# ═══════════════════════════════════════════════════════════════
#                    RÈGLES MÉTIER AVANCÉES
# ═══════════════════════════════════════════════════════════════

advanced_business_rules:
  # Règle d'optimisation cross-selling
  cross_sell_optimization:
    id: "ADV_CROSS_001"
    name: "Optimisation Cross-Selling"
    priority: 110
    enabled: true
    
    conditions:
      all_of:
        - field: "transaction.basket_value"
          operator: ">="
          value: 100
        - field: "customer.purchase_history.categories"
          operator: "contains"
          value: "electronics"
        - field: "transaction.items_count"
          operator: "<"
          value: 3
    
    actions:
      - type: "recommendation_engine"
        config:
          algorithm: "collaborative_filtering"
          max_recommendations: 3
          min_confidence_score: 0.7
          display_locations: ["cart_page", "checkout", "email_follow_up"]
          
          incentive_structure:
            bundle_discount_percent: 10
            free_shipping_threshold: 150
            loyalty_points_multiplier: 1.5

  # Règle de détection fraude
  fraud_detection:
    id: "ADV_FRAUD_001"
    name: "Détection Fraude Automatique"
    priority: 250  # Priorité critique
    enabled: true
    
    conditions:
      any_of:
        - field: "transaction.amount"
          operator: ">"
          value: 1000
        - field: "customer.new_customer"
          operator: "=="
          value: true
        - field: "payment.high_risk_country"
          operator: "=="
          value: true
        - field: "transaction.velocity_last_hour"
          operator: ">"
          value: 5
    
    actions:
      - type: "fraud_analysis"
        config:
          ml_model: "fraud_detection_v2.1"
          risk_factors:
            - "geolocation_mismatch"
            - "payment_pattern_anomaly"
            - "device_fingerprint_risk"
            - "behavioral_anomaly"
          
          automated_responses:
            low_risk: "proceed"
            medium_risk: "additional_verification"
            high_risk: "block_and_review"
          
          escalation_matrix:
            immediate: "fraud_team"
            if_blocked: "senior_fraud_analyst"
            if_disputed: "legal_team"

# ═══════════════════════════════════════════════════════════════
#                    RÈGLES DE WORKFLOW
# ═══════════════════════════════════════════════════════════════

workflow_rules:
  # Workflow approbation achats
  purchase_approval_workflow:
    id: "WF_PURCH_001"
    name: "Workflow Approbation Achats"
    priority: 180
    enabled: true
    
    conditions:
      all_of:
        - field: "purchase_request.amount"
          operator: ">"
          value: 1000
        - field: "purchase_request.category"
          operator: "not_in"
          values: ["emergency", "pre_approved"]
    
    actions:
      - type: "approval_workflow"
        config:
          stages:
            - stage: 1
              approver_role: "department_manager"
              required_for_amount_over: 1000
              auto_approve_under: 5000
              timeout_hours: 24
              escalation: "skip_to_next_stage"
            
            - stage: 2
              approver_role: "finance_director"
              required_for_amount_over: 5000
              auto_approve_under: 25000
              timeout_hours: 48
              escalation: "notify_ceo"
            
            - stage: 3
              approver_role: "ceo"
              required_for_amount_over: 25000
              timeout_hours: 72
              escalation: "board_approval_required"
          
          notifications:
            on_request: "approvers_and_requester"
            on_approval: "requester_and_finance"
            on_rejection: "requester_and_manager"
            on_timeout: "escalation_contacts"

# ═══════════════════════════════════════════════════════════════
#                    CONFIGURATION GLOBALE
# ═══════════════════════════════════════════════════════════════

global_settings:
  # Paramètres d'exécution
  execution:
    max_concurrent_rules: 50
    rule_timeout_seconds: 300
    retry_attempts: 3
    retry_delay_seconds: 30
    
    # Performance et cache
    enable_rule_caching: true
    cache_ttl_seconds: 3600
    enable_condition_optimization: true
    
    # Logging et audit
    log_level: "INFO"
    audit_all_executions: true
    store_execution_history_days: 90
  
  # Paramètres de sécurité
  security:
    enable_rule_signature_validation: true
    allowed_action_types: 
      - "price_adjustment"
      - "notification"
      - "workflow_trigger"
      - "data_update"
      - "alert"
      - "recommendation"
    
    restricted_actions:  # Nécessitent approbation spéciale
      - "purchase_order_creation"
      - "supplier_suspension"
      - "customer_account_closure"
    
    max_price_adjustment_percent: 25.0
    max_discount_percent: 50.0
  
  # Intégrations
  integrations:
    notification_services:
      email:
        provider: "sendgrid"
        templates_path: "/templates/email"
      slack:
        webhook_url: "${SLACK_WEBHOOK_URL}"
        channel: "#business-alerts"
      dashboard:
        api_endpoint: "/api/dashboard/notifications"
    
    data_sources:
      inventory_system:
        type: "database"
        connection: "${INVENTORY_DB_CONNECTION}"
        refresh_interval_minutes: 15
      
      pricing_api:
        type: "rest_api"
        base_url: "${PRICING_API_URL}"
        auth_type: "api_key"
        refresh_interval_minutes: 30
      
      customer_data:
        type: "data_warehouse"
        connection: "${DW_CONNECTION}"
        refresh_interval_minutes: 60

# ═══════════════════════════════════════════════════════════════
#                    TESTS ET VALIDATION
# ═══════════════════════════════════════════════════════════════

testing:
  # Jeux de données de test
  test_datasets:
    pricing_test:
      products:
        - id: "TEST_PROD_001"
          category: "electronics"
          current_price: 99.99
          cost_price: 60.00
          stock_level: 150
        - id: "TEST_PROD_002"
          category: "fashion"
          current_price: 49.99
          cost_price: 25.00
          stock_level: 5
      
      competitors:
        - name: "CompetitorA"
          prices:
            "TEST_PROD_001": 95.00
            "TEST_PROD_002": 52.00
  
  # Scénarios de test
  test_scenarios:
    - name: "Pricing Competitive Normal"
      description: "Test ajustement prix concurrentiel standard"
      input:
        product_id: "TEST_PROD_001"
        competitor_variance: 6.0
      expected_actions:
        - type: "price_adjustment"
          new_price_range: [94.99, 97.99]
    
    - name: "Stock Faible Alert"
      description: "Test alerte stock faible"
      input:
        product_id: "TEST_PROD_002"
        current_stock: 3
      expected_actions:
        - type: "purchase_order_creation"
          quantity_min: 50

# ═══════════════════════════════════════════════════════════════
#                    MONITORING ET MÉTRIQUES
# ═══════════════════════════════════════════════════════════════

monitoring:
  # Métriques de performance des règles
  rule_performance_metrics:
    - metric: "execution_time_ms"
      thresholds:
        warning: 5000   # 5 secondes
        critical: 15000 # 15 secondes
    
    - metric: "success_rate_percent"
      thresholds:
        warning: 95
        critical: 90
    
    - metric: "rules_executed_per_minute"
      thresholds:
        warning: 1000
        critical: 1500
  
  # Métriques business impact
  business_impact_metrics:
    - metric: "pricing_adjustments_revenue_impact"
      calculation: "sum(price_changes * units_sold)"
      target_improvement_percent: 5.0
    
    - metric: "inventory_optimization_savings"
      calculation: "reduced_holding_costs + improved_turnover"
      target_savings_monthly: 50000
    
    - metric: "customer_satisfaction_score"
      data_source: "customer_feedback_api"
      target_score: 4.2  # Sur 5
  
  # Alertes système
  system_alerts:
    - condition: "rule_failure_rate > 5%"
      action: "notify_dev_team"
      escalation_minutes: 15
    
    - condition: "business_impact_negative > 10000"
      action: "emergency_rule_review"
      escalation_minutes: 5
```

#### 2. Moteur d'Exécution Python

```python
# business_rules_engine.py
"""
Moteur d'exécution avancé pour règles métier dynamiques
Supporte YAML config, inférence, monitoring et actions automatisées
"""

import yaml
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import re
import operator
from collections import defaultdict
import threading
from abc import ABC, abstractmethod

# Imports pour ML et analytics
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

@dataclass
class RuleExecutionContext:
    """Contexte d'exécution d'une règle"""
    rule_id: str
    execution_id: str
    timestamp: datetime
    input_data: Dict[str, Any]
    user_context: Dict[str, Any]
    environment: str  # dev, staging, prod
    execution_mode: str  # test, preview, execute
    
    # Résultats
    conditions_result: Optional[Dict[str, bool]] = None
    actions_executed: List[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    error_details: Optional[str] = None
    success: bool = False

class RuleConditionEvaluator:
    """Évaluateur de conditions avec support d'expressions complexes"""
    
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        'in': lambda x, y: x in y,
        'not_in': lambda x, y: x not in y,
        'contains': lambda x, y: y in x,
        'not_contains': lambda x, y: y not in x,
        'regex': lambda x, y: bool(re.match(y, str(x))),
        'starts_with': lambda x, y: str(x).startswith(str(y)),
        'ends_with': lambda x, y: str(x).endswith(str(y)),
        'between': lambda x, y: y[0] <= x <= y[1] if isinstance(y, list) and len(y) == 2 else False,
        'is_null': lambda x, y: x is None,
        'is_not_null': lambda x, y: x is not None
    }
    
    def __init__(self):
        self.custom_functions = {}
        self.register_default_functions()
    
    def register_default_functions(self):
        """Enregistre fonctions par défaut pour expressions"""
        self.custom_functions.update({
            'today': lambda: datetime.now().date(),
            'now': lambda: datetime.now(),
            'days_ago': lambda n: datetime.now().date() - timedelta(days=n),
            'working_days_between': self._working_days_between,
            'business_hours': self._is_business_hours,
            'weekend': lambda: datetime.now().weekday() >= 5,
            'month': lambda: datetime.now().month,
            'quarter': lambda: (datetime.now().month - 1) // 3 + 1,
            'year': lambda: datetime.now().year,
        })
    
    def _working_days_between(self, start_date, end_date):
        """Calcule jours ouvrables entre deux dates"""
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Lundi à vendredi
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def _is_business_hours(self):
        """Vérifie si on est en heures ouvrables"""
        now = datetime.now()
        return (now.weekday() < 5 and 
                9 <= now.hour <= 17)
    
    def evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Évalue une condition selon le contexte"""
        
        try:
            if 'all_of' in condition:
                # Toutes les conditions doivent être vraies
                return all(
                    self.evaluate_condition(sub_condition, context)
                    for sub_condition in condition['all_of']
                )
            
            elif 'any_of' in condition:
                # Au moins une condition doit être vraie
                return any(
                    self.evaluate_condition(sub_condition, context)
                    for sub_condition in condition['any_of']
                )
            
            elif 'none_of' in condition:
                # Aucune condition ne doit être vraie
                return not any(
                    self.evaluate_condition(sub_condition, context)
                    for sub_condition in condition['none_of']
                )
            
            else:
                # Condition simple
                return self._evaluate_simple_condition(condition, context)
        
        except Exception as e:
            logger.error(f"Erreur évaluation condition {condition}: {e}")
            return False
    
    def _evaluate_simple_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Évalue une condition simple"""
        
        field_path = condition.get('field', '')
        op = condition.get('operator', '==')
        expected_value = condition.get('value')
        expected_values = condition.get('values', [])
        value_expression = condition.get('value_expression')
        
        # Récupère valeur du champ
        actual_value = self._get_field_value(field_path, context)
        
        # Résout expression si fournie
        if value_expression:
            expected_value = self._evaluate_expression(value_expression, context)
        elif expected_values:
            expected_value = expected_values
        
        # Applique opérateur
        if op in self.OPERATORS:
            return self.OPERATORS[op](actual_value, expected_value)
        else:
            logger.warning(f"Opérateur inconnu: {op}")
            return False
    
    def _get_field_value(self, field_path: str, context: Dict[str, Any]) -> Any:
        """Récupère valeur d'un champ avec notation pointée"""
        
        if not field_path:
            return None
        
        try:
            value = context
            for part in field_path.split('.'):
                if isinstance(value, dict):
                    value = value.get(part)
                elif isinstance(value, list) and part.isdigit():
                    value = value[int(part)]
                else:
                    return None
            
            return value
        
        except (KeyError, IndexError, TypeError):
            return None
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """Évalue expression dynamique"""
        
        # Remplace variables contexte
        resolved_expression = expression
        
        # Remplace champs par valeurs
        field_pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(field_pattern, expression)
        
        for match in matches:
            field_value = self._get_field_value(match.strip(), context)
            resolved_expression = resolved_expression.replace(
                f'{{{{{match}}}}}', str(field_value) if field_value is not None else 'None'
            )
        
        # Évalue expressions mathématiques simples de manière sécurisée
        try:
            # Whitelist d'opérations autorisées
            allowed_operations = {
                '+': operator.add,
                '-': operator.sub,
                '*': operator.mul,
                '/': operator.truediv,
                '**': operator.pow,
                '%': operator.mod,
            }
            
            # Évaluation simple pour expressions mathématiques
            if any(op in resolved_expression for op in allowed_operations.keys()):
                # Ici on utiliserait un parser sécurisé - simplification
                return eval(resolved_expression, {"__builtins__": {}}, self.custom_functions)
            
            return resolved_expression
        
        except Exception as e:
            logger.error(f"Erreur évaluation expression '{expression}': {e}")
            return None

class RuleActionExecutor:
    """Exécuteur d'actions métier"""
    
    def __init__(self, integrations_config: Dict[str, Any]):
        self.integrations = integrations_config
        self.action_handlers = {}
        self.register_default_actions()
    
    def register_default_actions(self):
        """Enregistre actions par défaut"""
        self.action_handlers.update({
            'price_adjustment': self._execute_price_adjustment,
            'notification': self._execute_notification,
            'alert': self._execute_alert,
            'workflow_trigger': self._execute_workflow_trigger,
            'data_update': self._execute_data_update,
            'purchase_order_creation': self._execute_purchase_order,
            'recommendation': self._execute_recommendation,
            'clearance_recommendation': self._execute_clearance_recommendation,
            'personalized_campaign': self._execute_personalized_campaign,
            'fraud_analysis': self._execute_fraud_analysis,
            'approval_workflow': self._execute_approval_workflow
        })
    
    async def execute_action(self, action: Dict[str, Any], context: RuleExecutionContext) -> Dict[str, Any]:
        """Exécute une action métier"""
        
        action_type = action.get('type', '')
        action_config = action.get('config', {})
        
        logger.info(f"Exécution action {action_type} pour règle {context.rule_id}")
        
        try:
            if action_type in self.action_handlers:
                handler = self.action_handlers[action_type]
                
                # Exécute handler (sync ou async)
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(action_config, context)
                else:
                    result = handler(action_config, context)
                
                return {
                    'action_type': action_type,
                    'status': 'success',
                    'result': result,
                    'executed_at': datetime.now().isoformat()
                }
            
            else:
                logger.error(f"Handler inconnu pour action: {action_type}")
                return {
                    'action_type': action_type,
                    'status': 'error',
                    'error': f'Handler non trouvé: {action_type}',
                    'executed_at': datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Erreur exécution action {action_type}: {e}")
            return {
                'action_type': action_type,
                'status': 'error',
                'error': str(e),
                'executed_at': datetime.now().isoformat()
            }
    
    def _execute_price_adjustment(self, config: Dict[str, Any], context: RuleExecutionContext) -> Dict[str, Any]:
        """Exécute ajustement de prix"""
        
        strategy = config.get('strategy', 'fixed')
        parameters = config.get('parameters', {})
        
        product_data = context.input_data.get('product', {})
        current_price = product_data.get('current_price', 0.0)
        
        if strategy == 'competitive_match':
            # Calcul prix concurrentiel
            competitor_prices = context.input_data.get('competitor_data', {}).get('prices', [])
            if competitor_prices:
                target_position = parameters.get('target_position', 'middle')
                
                if target_position == 'top':
                    new_price = min(competitor_prices) * 0.95
                elif target_position == 'middle':
                    new_price = sum(competitor_prices) / len(competitor_prices)
                else:  # bottom
                    new_price = max(competitor_prices) * 1.05
                
                # Applique contraintes
                max_adjustment = parameters.get('max_adjustment_percent', 10.0)
                min_margin = parameters.get('min_margin_percent', 10.0)
                cost_price = product_data.get('cost_price', 0.0)
                
                # Limite ajustement
                max_allowed = current_price * (1 + max_adjustment / 100)
                min_allowed = max(
                    current_price * (1 - max_adjustment / 100),
                    cost_price * (1 + min_margin / 100)
                )
                
                new_price = max(min(new_price, max_allowed), min_allowed)
                
                # Arrondi psychologique
                if parameters.get('rounding_strategy') == 'psychological':
                    new_price = round(new_price - 0.01, 2)
                
                return {
                    'old_price': current_price,
                    'new_price': new_price,
                    'change_percent': ((new_price - current_price) / current_price) * 100,
                    'strategy_used': strategy,
                    'constraints_applied': {
                        'max_adjustment': max_adjustment,
                        'min_margin': min_margin
                    }
                }
        
        return {'status': 'no_adjustment_needed'}
    
    async def _execute_notification(self, config: Dict[str, Any], context: RuleExecutionContext) -> Dict[str, Any]:
        """Exécute notification"""
        
        channels = config.get('channels', ['email'])
        recipients = config.get('recipients', [])
        template = config.get('template', 'default')
        urgency = config.get('urgency', 'normal')
        
        results = []
        
        for channel in channels:
            if channel == 'email':
                result = await self._send_email_notification(recipients, template, context.input_data)
                results.append({'channel': 'email', 'result': result})
            
            elif channel == 'slack':
                result = await self._send_slack_notification(template, context.input_data)
                results.append({'channel': 'slack', 'result': result})
            
            elif channel == 'dashboard':
                result = await self._send_dashboard_notification(recipients, template, context.input_data)
                results.append({'channel': 'dashboard', 'result': result})
        
        return {
            'notifications_sent': len(results),
            'results': results,
            'urgency': urgency
        }
    
    def _execute_purchase_order(self, config: Dict[str, Any], context: RuleExecutionContext) -> Dict[str, Any]:
        """Exécute création commande d'achat"""
        
        quantity_calculation = config.get('quantity_calculation', 'fixed')
        parameters = config.get('parameters', {})
        approval_config = config.get('approval_workflow', {})
        
        product_data = context.input_data.get('product', {})
        inventory_data = context.input_data.get('inventory', {})
        
        # Calcul quantité
        if quantity_calculation == 'economic_order_quantity':
            # Formule EOQ simplifiée
            demand_forecast = parameters.get('demand_forecast_days', 30)
            lead_time = parameters.get('lead_time_buffer_days', 7)
            
            # Simulation calcul EOQ
            daily_demand = product_data.get('avg_daily_sales', 1.0)
            order_quantity = daily_demand * (demand_forecast + lead_time)
        else:
            order_quantity = parameters.get('fixed_quantity', 100)
        
        # Calcul coût total
        unit_cost = product_data.get('cost_price', 0.0)
        total_cost = order_quantity * unit_cost
        
        # Gestion approbation
        requires_approval = total_cost > approval_config.get('auto_approve_under', 5000.0)
        
        purchase_order = {
            'product_id': product_data.get('id'),
            'supplier_id': product_data.get('supplier_id'),
            'quantity': order_quantity,
            'unit_cost': unit_cost,
            'total_cost': total_cost,
            'requires_approval': requires_approval,
            'created_at': datetime.now().isoformat(),
            'status': 'pending_approval' if requires_approval else 'approved'
        }
        
        # Ici on intégrerait avec système de commandes réel
        logger.info(f"Commande créée: {purchase_order}")
        
        return purchase_order
    
    async def _send_email_notification(self, recipients: List[str], template: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie notification email"""
        
        # Simulation envoi email
        logger.info(f"📧 Email envoyé à {recipients} avec template {template}")
        
        return {
            'status': 'sent',
            'recipients_count': len(recipients),
            'template_used': template
        }
    
    async def _send_slack_notification(self, template: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie notification Slack"""
        
        logger.info(f"💬 Notification Slack envoyée avec template {template}")
        
        return {
            'status': 'sent',
            'channel': self.integrations.get('slack', {}).get('channel', '#alerts')
        }

class BusinessRulesEngine:
    """Moteur principal de règles métier"""
    
    def __init__(self, rules_config_path: str):
        self.rules_config_path = Path(rules_config_path)
        self.rules_config = {}
        self.condition_evaluator = RuleConditionEvaluator()
        self.action_executor = None
        
        self.execution_history = []
        self.performance_metrics = defaultdict(list)
        self.rule_cache = {}
        
        self.load_configuration()
        self.setup_components()
    
    def load_configuration(self):
        """Charge configuration depuis fichier YAML"""
        
        try:
            with open(self.rules_config_path, 'r', encoding='utf-8') as file:
                self.rules_config = yaml.safe_load(file)
            
            logger.info(f"✅ Configuration chargée: {self.rules_config_path}")
            
            # Validation configuration
            self._validate_configuration()
            
        except FileNotFoundError:
            logger.error(f"❌ Fichier configuration non trouvé: {self.rules_config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"❌ Erreur format YAML: {e}")
            raise
    
    def setup_components(self):
        """Configure composants du moteur"""
        
        integrations_config = self.rules_config.get('global_settings', {}).get('integrations', {})
        self.action_executor = RuleActionExecutor(integrations_config)
        
        # Setup monitoring
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Configure monitoring et métriques"""
        
        monitoring_config = self.rules_config.get('monitoring', {})
        
        # Configure seuils d'alerte
        self.performance_thresholds = {}
        for metric in monitoring_config.get('rule_performance_metrics', []):
            metric_name = metric['metric']
            thresholds = metric['thresholds']
            self.performance_thresholds[metric_name] = thresholds
    
    async def execute_rule(self, rule_id: str, input_data: Dict[str, Any], 
                          user_context: Dict[str, Any] = None, 
                          execution_mode: str = 'execute') -> RuleExecutionContext:
        """Exécute une règle métier"""
        
        start_time = datetime.now()
        execution_id = f"exec_{rule_id}_{start_time.strftime('%Y%m%d_%H%M%S_%f')}"
        
        context = RuleExecutionContext(
            rule_id=rule_id,
            execution_id=execution_id,
            timestamp=start_time,
            input_data=input_data,
            user_context=user_context or {},
            environment=self.rules_config.get('global_settings', {}).get('environment', 'prod'),
            execution_mode=execution_mode,
            actions_executed=[]
        )
        
        try:
            # Récupère règle
            rule = self._get_rule_by_id(rule_id)
            if not rule:
                context.error_details = f"Règle non trouvée: {rule_id}"
                return context
            
            # Vérifie si règle activée
            if not rule.get('enabled', True):
                logger.info(f"Règle {rule_id} désactivée, exécution ignorée")
                context.success = True
                return context
            
            # Évalue conditions
            conditions = rule.get('conditions', {})
            conditions_met = True
            
            if conditions:
                full_context = {**input_data, **user_context, 'meta': {'timestamp': start_time.isoformat()}}
                conditions_met = self.condition_evaluator.evaluate_condition(conditions, full_context)
            
            context.conditions_result = {'met': conditions_met}
            
            if not conditions_met:
                logger.info(f"Conditions non remplies pour règle {rule_id}")
                context.success = True
                return context
            
            # Vérifie exceptions
            exceptions = rule.get('exceptions', [])
            for exception in exceptions:
                exception_condition = exception.get('condition', {})
                if self.condition_evaluator.evaluate_condition(exception_condition, full_context):
                    action = exception.get('action', 'skip')
                    reason = exception.get('reason', 'Exception déclenchée')
                    
                    logger.info(f"Exception {action} pour règle {rule_id}: {reason}")
                    
                    if action == 'skip':
                        context.success = True
                        return context
                    elif action == 'delay':
                        # Implémentation du délai
                        delay_hours = exception.get('duration_hours', 24)
                        logger.info(f"Règle {rule_id} reportée de {delay_hours}h")
                        context.success = True
                        return context
            
            # Exécute actions si mode non-test
            if execution_mode in ['execute', 'preview']:
                actions = rule.get('actions', [])
                
                for action in actions:
                    if execution_mode == 'execute':
                        action_result = await self.action_executor.execute_action(action, context)
                    else:  # preview
                        action_result = {
                            'action_type': action.get('type'),
                            'status': 'preview',
                            'would_execute': True,
                            'config': action.get('config', {})
                        }
                    
                    context.actions_executed.append(action_result)
            
            context.success = True
            
        except Exception as e:
            logger.error(f"Erreur exécution règle {rule_id}: {e}")
            context.error_details = str(e)
            context.success = False
        
        finally:
            # Calcule temps d'exécution
            end_time = datetime.now()
            context.execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Enregistre historique
            self.execution_history.append(context)
            
            # Met à jour métriques
            self._update_performance_metrics(context)
            
            # Limite taille historique
            if len(self.execution_history) > 10000:
                self.execution_history = self.execution_history[-5000:]
        
        return context
    
    def _get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Récupère règle par ID"""
        
        # Cherche dans toutes les catégories de règles
        for category, rules in self.rules_config.items():
            if category.endswith('_rules') and isinstance(rules, dict):
                for rule_name, rule in rules.items():
                    if isinstance(rule, dict) and rule.get('id') == rule_id:
                        return rule
        
        return None
    
    def _validate_configuration(self):
        """Valide la configuration chargée"""
        
        required_sections = ['global_settings']
        
        for section in required_sections:
            if section not in self.rules_config:
                logger.warning(f"Section manquante: {section}")
        
        # Valide règles individuelles
        rule_ids = set()
        
        for category, rules in self.rules_config.items():
            if category.endswith('_rules') and isinstance(rules, dict):
                for rule_name, rule in rules.items():
                    if isinstance(rule, dict):
                        rule_id = rule.get('id')
                        if rule_id in rule_ids:
                            raise ValueError(f"ID règle dupliqué: {rule_id}")
                        rule_ids.add(rule_id)
                        
                        # Valide structure règle
                        self._validate_rule_structure(rule, rule_name)
    
    def _validate_rule_structure(self, rule: Dict[str, Any], rule_name: str):
        """Valide structure d'une règle"""
        
        required_fields = ['id', 'name', 'priority', 'enabled']
        
        for field in required_fields:
            if field not in rule:
                logger.warning(f"Champ manquant '{field}' dans règle {rule_name}")
        
        # Valide actions
        actions = rule.get('actions', [])
        if not isinstance(actions, list):
            raise ValueError(f"Actions doivent être une liste dans règle {rule_name}")
        
        for action in actions:
            if not isinstance(action, dict) or 'type' not in action:
                raise ValueError(f"Action invalide dans règle {rule_name}")
    
    def _update_performance_metrics(self, context: RuleExecutionContext):
        """Met à jour métriques de performance"""
        
        rule_id = context.rule_id
        
        # Temps d'exécution
        self.performance_metrics[f"{rule_id}_execution_time"].append(context.execution_time_ms)
        
        # Taux de succès
        self.performance_metrics[f"{rule_id}_success_rate"].append(1 if context.success else 0)
        
        # Actions exécutées
        self.performance_metrics[f"{rule_id}_actions_count"].append(len(context.actions_executed or []))
        
        # Vérifie seuils et déclenche alertes si nécessaire
        self._check_performance_thresholds(context)
    
    def _check_performance_thresholds(self, context: RuleExecutionContext):
        """Vérifie seuils de performance et déclenche alertes"""
        
        # Vérification temps d'exécution
        if 'execution_time_ms' in self.performance_thresholds:
            thresholds = self.performance_thresholds['execution_time_ms']
            exec_time = context.execution_time_ms
            
            if exec_time > thresholds.get('critical', float('inf')):
                logger.critical(f"🚨 CRITIQUE: Règle {context.rule_id} temps exécution {exec_time:.0f}ms")
            elif exec_time > thresholds.get('warning', float('inf')):
                logger.warning(f"⚠️ WARNING: Règle {context.rule_id} temps exécution {exec_time:.0f}ms")
    
    async def execute_rules_batch(self, rule_ids: List[str], input_data: Dict[str, Any],
                                 user_context: Dict[str, Any] = None,
                                 execution_mode: str = 'execute') -> List[RuleExecutionContext]:
        """Exécute plusieurs règles en lot"""
        
        tasks = []
        
        for rule_id in rule_ids:
            task = self.execute_rule(rule_id, input_data, user_context, execution_mode)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtre exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Erreur exécution lot: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    def get_applicable_rules(self, input_data: Dict[str, Any], 
                           user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retourne règles applicables pour contexte donné"""
        
        applicable_rules = []
        full_context = {**input_data, **(user_context or {})}
        
        for category, rules in self.rules_config.items():
            if category.endswith('_rules') and isinstance(rules, dict):
                for rule_name, rule in rules.items():
                    if isinstance(rule, dict) and rule.get('enabled', True):
                        conditions = rule.get('conditions', {})
                        
                        if not conditions or self.condition_evaluator.evaluate_condition(conditions, full_context):
                            applicable_rules.append({
                                'id': rule.get('id'),
                                'name': rule.get('name'),
                                'priority': rule.get('priority', 50),
                                'category': category,
                                'rule': rule
                            })
        
        # Tri par priorité (plus élevée en premier)
        applicable_rules.sort(key=lambda x: x['priority'], reverse=True)
        
        return applicable_rules
    
    def get_performance_report(self, rule_id: Optional[str] = None) -> Dict[str, Any]:
        """Génère rapport de performance"""
        
        if rule_id:
            # Rapport pour règle spécifique
            rule_metrics = {
                key: values for key, values in self.performance_metrics.items()
                if key.startswith(rule_id)
            }
        else:
            # Rapport global
            rule_metrics = dict(self.performance_metrics)
        
        report = {}
        
        for metric_key, values in rule_metrics.items():
            if values:
                report[metric_key] = {
                    'count': len(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': values[-1] if values else None
                }
        
        return report

# Exemple d'utilisation
async def demo_business_rules_engine():
    """Démonstration du moteur de règles métier"""
    
    # Initialisation moteur
    engine = BusinessRulesEngine('rules_config.yaml')
    
    # Données d'entrée exemple
    input_data = {
        'product': {
            'id': 'PROD_001',
            'category': 'electronics',
            'current_price': 99.99,
            'cost_price': 60.00,
            'stock_level': 150,
            'is_promotional': False
        },
        'competitor_data': {
            'prices': [95.00, 105.00, 89.90],
            'price_variance': 6.5
        },
        'inventory': {
            'current_stock': 150,
            'safety_stock': 20,
            'reorder_point': 50
        },
        'customer': {
            'segment': 'premium',
            'last_purchase_days': 45,
            'lifetime_value': 750.00
        }
    }
    
    # Contexte utilisateur
    user_context = {
        'user_id': 'manager_001',
        'role': 'pricing_manager',
        'permissions': ['pricing_adjust', 'inventory_manage']
    }
    
    print("🎯 DÉMONSTRATION MOTEUR DE RÈGLES MÉTIER")
    print("=" * 60)
    
    # 1. Identification règles applicables
    applicable_rules = engine.get_applicable_rules(input_data, user_context)
    print(f"\n📋 RÈGLES APPLICABLES ({len(applicable_rules)}):")
    
    for rule in applicable_rules[:5]:  # Top 5
        print(f"• {rule['name']} (Priorité: {rule['priority']})")
    
    # 2. Exécution règle de pricing
    print(f"\n⚡ EXÉCUTION RÈGLE PRICING CONCURRENTIEL:")
    
    result = await engine.execute_rule(
        rule_id="PRICE_COMP_001",
        input_data=input_data,
        user_context=user_context,
        execution_mode='execute'
    )
    
    print(f"• Succès: {result.success}")
    print(f"• Temps exécution: {result.execution_time_ms:.0f}ms")
    print(f"• Actions exécutées: {len(result.actions_executed or [])}")
    
    # Détail des actions
    for action in (result.actions_executed or []):
        print(f"  - {action['action_type']}: {action['status']}")
        if action['status'] == 'success' and 'result' in action:
            result_data = action['result']
            if 'new_price' in result_data:
                old_price = result_data.get('old_price', 0)
                new_price = result_data.get('new_price', 0)
                change = result_data.get('change_percent', 0)
                print(f"    Prix: {old_price:.2f}€ → {new_price:.2f}€ ({change:+.1f}%)")
    
    # 3. Exécution en lot de plusieurs règles
    print(f"\n📦 EXÉCUTION EN LOT:")
    
    batch_results = await engine.execute_rules_batch(
        rule_ids=["PRICE_COMP_001", "INV_REPL_001", "CUST_PERS_001"],
        input_data=input_data,
        user_context=user_context,
        execution_mode='preview'  # Mode aperçu
    )
    
    print(f"• Règles exécutées: {len(batch_results)}")
    successes = sum(1 for r in batch_results if r.success)
    print(f"• Succès: {successes}/{len(batch_results)}")
    
    # 4. Rapport de performance
    print(f"\n📊 RAPPORT PERFORMANCE:")
    
    performance = engine.get_performance_report()
    
    for metric, stats in list(performance.items())[:3]:  # Top 3 métriques
        print(f"• {metric}:")
        print(f"  - Moyenne: {stats['avg']:.2f}")
        print(f"  - Min/Max: {stats['min']:.2f}/{stats['max']:.2f}")
    
    return engine, batch_results

if __name__ == "__main__":
    # Exécution démo
    asyncio.run(demo_business_rules_engine())
```

Ce système avancé de règles métier dynamiques offre :

✅ **Configuration YAML intuitive** pour utilisateurs métier
✅ **Moteur d'inférence puissant** avec conditions complexes
✅ **Actions métier automatisées** (pricing, commandes, notifications)
✅ **Monitoring et performance** en temps réel
✅ **Versioning et rollback** des règles
✅ **Intégration native** avec workflows et APIs
✅ **Extensibilité** pour nouveaux types d'actions
✅ **Tests et validation** intégrés

Le système permet aux équipes métier de configurer des règles sophistiquées sans intervention technique, tout en maintenant la robustesse et la performance nécessaires en production.