# IA Intégrée pour Recommandations Business - Espace Perplexity AI

## Vue d'ensemble
Ce document présente un système d'intelligence artificielle avancé pour l'espace Perplexity AI, capable d'interpréter automatiquement les données métier, de générer des insights intelligents et de proposer des recommandations d'actions concrètes aux utilisateurs business.

## Architecture du Système d'IA Métier

### Écosystème IA Business Intelligence

```
┌─────────────────────────────────────────────────────────────────┐
│                 IA MÉTIER INTÉGRÉE - RECOMMANDATIONS            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🧠 NLP Métier        📊 Analytics IA       🎯 Recommandations  │
│  ┌───────────────┐    ┌───────────────┐     ┌─────────────────┐  │
│  │ • Text Mining │    │ • Pattern ML  │     │ • Action Plans │  │
│  │ • Intent Recog│    │ • Prediction  │     │ • Priority Rank│  │
│  │ • Sentiment   │    │ • Clustering  │     │ • ROI Estimate │  │
│  │ • Entity Extract│   │ • Anomaly AI  │     │ • Risk Assess │  │
│  └───────────────┘    └───────────────┘     └─────────────────┘  │
│                                  ↕                              │
│  🔍 Context Engine   🤖 Decision Support    ⚡ Real-time AI     │
│  ┌───────────────┐    ┌───────────────┐     ┌─────────────────┐  │
│  │ • Business Rules│   │ • Multi-criteria│   │ • Stream Process│  │
│  │ • Domain Know │    │ • Optimization │     │ • Live Insights │  │
│  │ • Temporal    │    │ • What-if Analysis│  │ • Auto-trigger │  │
│  │ • User Profile│    │ • Scenario Plan│     │ • Adaptive    │  │
│  └───────────────┘    └───────────────┘     └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Module 1 : Moteur de Recommandations Intelligentes

### Système Central de Recommandations Business

```python
# intelligent_business_recommender.py
"""
Système d'IA pour recommandations métier automatiques
Intègre ML, NLP, règles métier et optimisation multi-critères
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
import re

# ML et NLP
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from textblob import TextBlob
import spacy

# Optimization
from scipy.optimize import minimize
import pulp

# Visualization
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    PRICING = "pricing"
    INVENTORY = "inventory"  
    MARKETING = "marketing"
    CUSTOMER = "customer"
    OPERATIONS = "operations"
    STRATEGIC = "strategic"
    RISK = "risk"
    FINANCIAL = "financial"

class RecommendationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RecommendationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class BusinessContext:
    """Contexte métier pour recommandations"""
    industry: str
    company_size: str  # startup, sme, enterprise
    business_model: str  # b2b, b2c, marketplace, saas
    key_metrics: List[str]
    constraints: Dict[str, Any]
    objectives: List[str]
    current_performance: Dict[str, float]
    market_conditions: Dict[str, Any]
    
@dataclass
class Recommendation:
    """Recommandation métier intelligente"""
    id: str
    type: RecommendationType
    priority: RecommendationPriority
    title: str
    description: str
    rationale: str
    
    # Actions recommandées
    suggested_actions: List[Dict[str, Any]]
    expected_impact: Dict[str, Any]  # revenue, cost, risk, etc.
    
    # Méta-information
    confidence_score: float  # 0-1
    risk_level: str  # low, medium, high
    implementation_effort: str  # low, medium, high
    timeline: Dict[str, Any]  # immediate, short_term, long_term
    
    # Données de support
    supporting_data: Dict[str, Any]
    related_metrics: List[str]
    dependencies: List[str]
    
    # Suivi
    created_at: datetime
    expires_at: Optional[datetime] = None
    status: RecommendationStatus = RecommendationStatus.PENDING
    
@dataclass
class RecommendationExplanation:
    """Explication détaillée d'une recommandation"""
    recommendation_id: str
    reasoning_chain: List[Dict[str, Any]]
    data_sources: List[str]
    model_insights: Dict[str, Any]
    alternative_scenarios: List[Dict[str, Any]]
    sensitivity_analysis: Dict[str, Any]

class IntelligentBusinessRecommender:
    """Système d'IA pour recommandations métier"""
    
    def __init__(self, business_context: BusinessContext):
        self.business_context = business_context
        self.recommendation_models = {}
        self.nlp_processor = None
        self.knowledge_base = {}
        
        self.setup_ai_components()
        self.load_domain_knowledge()
    
    def setup_ai_components(self):
        """Initialise composants d'IA"""
        
        # Modèles ML spécialisés
        self.recommendation_models = {
            'pricing_optimizer': RandomForestRegressor(n_estimators=100, random_state=42),
            'customer_segmenter': KMeans(n_clusters=5, random_state=42),
            'churn_predictor': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'demand_forecaster': RandomForestRegressor(n_estimators=150, random_state=42),
            'risk_classifier': GradientBoostingClassifier(n_estimators=80, random_state=42)
        }
        
        # Processeur NLP pour analyse textuelle
        try:
            self.nlp_processor = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Modèle spaCy non disponible, utilisation TextBlob")
            self.nlp_processor = None
        
        # Scalers pour normalisation
        self.scalers = {
            'standard': StandardScaler(),
            'label': LabelEncoder()
        }
        
        logger.info("✅ Composants IA initialisés")
    
    def load_domain_knowledge(self):
        """Charge base de connaissances métier"""
        
        # Règles métier par industrie
        industry_rules = {
            'ecommerce': {
                'key_ratios': ['conversion_rate', 'cart_abandonment', 'customer_lifetime_value'],
                'benchmarks': {'conversion_rate': 0.025, 'aov': 75, 'retention_rate': 0.27},
                'seasonality_patterns': ['black_friday', 'christmas', 'back_to_school'],
                'critical_metrics': ['revenue', 'traffic', 'conversion_rate', 'inventory_turnover']
            },
            'saas': {
                'key_ratios': ['mrr_growth', 'churn_rate', 'ltv_cac', 'nps'],
                'benchmarks': {'monthly_churn': 0.05, 'ltv_cac': 3.0, 'gross_retention': 0.9},
                'growth_stages': ['startup', 'growth', 'scale', 'mature'],
                'critical_metrics': ['mrr', 'arr', 'churn_rate', 'expansion_revenue']
            },
            'retail': {
                'key_ratios': ['same_store_sales', 'inventory_turnover', 'gross_margin'],
                'benchmarks': {'inventory_turnover': 4, 'gross_margin': 0.4, 'shrinkage': 0.02},
                'operational_factors': ['foot_traffic', 'basket_size', 'staff_productivity'],
                'critical_metrics': ['sales_per_sqft', 'inventory_levels', 'margin_per_category']
            }
        }
        
        # Patterns de recommandations par type
        recommendation_patterns = {
            RecommendationType.PRICING: {
                'triggers': ['competitor_price_change', 'demand_fluctuation', 'inventory_levels'],
                'actions': ['price_increase', 'price_decrease', 'dynamic_pricing', 'promotional_pricing'],
                'constraints': ['min_margin', 'market_position', 'customer_sensitivity']
            },
            RecommendationType.INVENTORY: {
                'triggers': ['stockout_risk', 'excess_inventory', 'seasonal_patterns', 'demand_forecast'],
                'actions': ['reorder', 'liquidation', 'promotional_push', 'supplier_negotiation'],
                'constraints': ['storage_capacity', 'cash_flow', 'supplier_minimums']
            },
            RecommendationType.MARKETING: {
                'triggers': ['acquisition_cost_high', 'conversion_low', 'retention_declining'],
                'actions': ['channel_optimization', 'audience_targeting', 'creative_refresh', 'budget_reallocation'],
                'constraints': ['budget_limits', 'brand_guidelines', 'regulatory_requirements']
            }
        }
        
        self.knowledge_base = {
            'industry_rules': industry_rules,
            'recommendation_patterns': recommendation_patterns,
            'business_contexts': self._load_business_contexts(),
            'success_patterns': self._load_success_patterns()
        }
        
        logger.info(f"📚 Base de connaissances chargée pour {len(industry_rules)} industries")
    
    def generate_recommendations(self, data: pd.DataFrame, 
                               analysis_results: Dict[str, Any] = None,
                               user_query: str = None) -> List[Recommendation]:
        """Génère recommandations intelligentes"""
        
        logger.info("🤖 Génération recommandations IA en cours...")
        
        all_recommendations = []
        
        # 1. Recommandations basées sur données
        if not data.empty:
            data_recommendations = self._generate_data_driven_recommendations(data)
            all_recommendations.extend(data_recommendations)
        
        # 2. Recommandations basées sur analyse existante
        if analysis_results:
            analysis_recommendations = self._generate_analysis_based_recommendations(analysis_results)
            all_recommendations.extend(analysis_recommendations)
        
        # 3. Recommandations basées sur NLP si query fournie
        if user_query:
            nlp_recommendations = self._generate_nlp_based_recommendations(user_query, data)
            all_recommendations.extend(nlp_recommendations)
        
        # 4. Recommandations proactives basées sur patterns
        proactive_recommendations = self._generate_proactive_recommendations(data)
        all_recommendations.extend(proactive_recommendations)
        
        # 5. Filtrage et priorisation
        filtered_recommendations = self._filter_and_prioritize_recommendations(all_recommendations)
        
        # 6. Génération explications
        for rec in filtered_recommendations:
            rec.explanation = self._generate_recommendation_explanation(rec, data)
        
        logger.info(f"✅ {len(filtered_recommendations)} recommandations générées")
        return filtered_recommendations
    
    def _generate_data_driven_recommendations(self, data: pd.DataFrame) -> List[Recommendation]:
        """Génère recommandations basées sur analyse des données"""
        
        recommendations = []
        
        # Détection colonnes métier importantes
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        # Analyse des tendances pour recommandations
        for col in numeric_cols:
            if self._is_business_metric(col):
                trend_rec = self._analyze_metric_trend(col, data)
                if trend_rec:
                    recommendations.append(trend_rec)
        
        # Détection anomalies pour alertes
        anomaly_recommendations = self._detect_anomaly_recommendations(data)
        recommendations.extend(anomaly_recommendations)
        
        # Optimisation basée corrélations
        correlation_recommendations = self._generate_correlation_recommendations(data)
        recommendations.extend(correlation_recommendations)
        
        # Recommandations saisonnières
        if self._has_temporal_data(data):
            seasonal_recommendations = self._generate_seasonal_recommendations(data)
            recommendations.extend(seasonal_recommendations)
        
        return recommendations
    
    def _analyze_metric_trend(self, metric: str, data: pd.DataFrame) -> Optional[Recommendation]:
        """Analyse tendance métrique et génère recommandation"""
        
        if len(data) < 10:
            return None
        
        metric_values = data[metric].dropna()
        if len(metric_values) < 5:
            return None
        
        # Calcul tendance sur dernières 30% des données
        recent_size = max(5, len(metric_values) // 3)
        recent_values = metric_values.tail(recent_size)
        older_values = metric_values.head(len(metric_values) - recent_size)
        
        recent_mean = recent_values.mean()
        older_mean = older_values.mean()
        
        if older_mean == 0:
            return None
        
        change_percent = (recent_mean - older_mean) / older_mean
        
        # Seuils pour recommandations
        if abs(change_percent) < 0.05:  # Moins de 5% de changement
            return None
        
        # Classification du changement
        if change_percent > 0.2:  # +20%
            priority = RecommendationPriority.HIGH
            impact_level = "high"
        elif change_percent > 0.1:  # +10%
            priority = RecommendationPriority.MEDIUM
            impact_level = "medium"
        elif change_percent < -0.2:  # -20%
            priority = RecommendationPriority.CRITICAL
            impact_level = "high"
        elif change_percent < -0.1:  # -10%
            priority = RecommendationPriority.HIGH
            impact_level = "medium"
        else:
            priority = RecommendationPriority.MEDIUM
            impact_level = "low"
        
        # Génération recommandation selon métrique et changement
        if change_percent > 0:
            # Tendance positive
            title = f"Capitaliser sur la croissance de {metric}"
            description = f"Le {metric} montre une croissance de {change_percent*100:.1f}% récemment"
            
            actions = [
                {
                    "action": "scale_up_operations",
                    "description": f"Augmenter capacité pour soutenir croissance {metric}",
                    "priority": "high"
                },
                {
                    "action": "analyze_success_factors", 
                    "description": "Identifier facteurs de succès pour reproduction",
                    "priority": "medium"
                },
                {
                    "action": "resource_planning",
                    "description": "Planifier ressources nécessaires croissance continue",
                    "priority": "medium"
                }
            ]
            
            risk_level = "medium"  # Risque de ne pas suivre la croissance
            
        else:
            # Tendance négative
            title = f"Corriger le déclin de {metric}"
            description = f"Le {metric} montre un déclin de {abs(change_percent)*100:.1f}% récemment"
            
            actions = [
                {
                    "action": "root_cause_analysis",
                    "description": f"Analyser causes du déclin {metric}",
                    "priority": "critical"
                },
                {
                    "action": "corrective_plan",
                    "description": "Mettre en place plan correctif immédiat",
                    "priority": "high"
                },
                {
                    "action": "competitive_analysis",
                    "description": "Analyser performance concurrentielle",
                    "priority": "medium"
                }
            ]
            
            risk_level = "high"  # Déclin = risque élevé
        
        # Estimation impact business
        current_value = recent_mean
        projected_value = current_value * (1 + change_percent * 0.5)  # Conservation tendance modérée
        
        expected_impact = {
            "metric_name": metric,
            "current_value": float(current_value),
            "projected_value": float(projected_value),
            "impact_percentage": change_percent * 50,  # Impact attendu modéré
            "confidence": 0.75,
            "timeframe_months": 3
        }
        
        return Recommendation(
            id=f"trend_{metric}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=self._classify_recommendation_type(metric),
            priority=priority,
            title=title,
            description=description,
            rationale=f"Tendance {change_percent*100:+.1f}% détectée sur {metric} nécessite action",
            
            suggested_actions=actions,
            expected_impact=expected_impact,
            
            confidence_score=0.8,
            risk_level=risk_level,
            implementation_effort="medium",
            timeline={
                "immediate": [actions[0]] if actions else [],
                "short_term": actions[1:2] if len(actions) > 1 else [],
                "long_term": actions[2:] if len(actions) > 2 else []
            },
            
            supporting_data={
                "recent_mean": float(recent_mean),
                "older_mean": float(older_mean),
                "change_percent": float(change_percent),
                "sample_size": len(metric_values),
                "trend_analysis": "increasing" if change_percent > 0 else "decreasing"
            },
            related_metrics=[metric],
            dependencies=[],
            
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=30)
        )
    
    def _detect_anomaly_recommendations(self, data: pd.DataFrame) -> List[Recommendation]:
        """Détecte anomalies et génère recommandations"""
        
        recommendations = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if not self._is_business_metric(col):
                continue
                
            col_data = data[col].dropna()
            if len(col_data) < 20:  # Pas assez de données
                continue
            
            # Détection simple avec IQR
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Anomalies récentes (derniers 10% des données)
            recent_size = max(5, len(col_data) // 10)
            recent_data = col_data.tail(recent_size)
            
            recent_anomalies = recent_data[
                (recent_data < lower_bound) | (recent_data > upper_bound)
            ]
            
            if len(recent_anomalies) > 0:
                anomaly_rate = len(recent_anomalies) / len(recent_data)
                
                if anomaly_rate > 0.2:  # Plus de 20% d'anomalies récentes
                    
                    # Classification anomalies
                    high_anomalies = recent_anomalies[recent_anomalies > upper_bound]
                    low_anomalies = recent_anomalies[recent_anomalies < lower_bound]
                    
                    if len(high_anomalies) > len(low_anomalies):
                        anomaly_type = "positive_spike"
                        title = f"Pics anormaux détectés - {col}"
                        risk = "medium"
                        actions_focus = "investigate_positive_anomaly"
                    else:
                        anomaly_type = "negative_spike" 
                        title = f"Chutes anormales détectées - {col}"
                        risk = "high"
                        actions_focus = "investigate_negative_anomaly"
                    
                    actions = [
                        {
                            "action": "anomaly_investigation",
                            "description": f"Investiguer anomalies {col} ({anomaly_rate*100:.1f}% des données récentes)",
                            "priority": "high"
                        },
                        {
                            "action": "data_validation",
                            "description": "Vérifier qualité et intégrité des données",
                            "priority": "medium"
                        },
                        {
                            "action": "process_review",
                            "description": "Revoir processus métier impactant cette métrique",
                            "priority": "medium"
                        }
                    ]
                    
                    recommendation = Recommendation(
                        id=f"anomaly_{col}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        type=RecommendationType.RISK,
                        priority=RecommendationPriority.HIGH,
                        title=title,
                        description=f"Anomalies détectées dans {col} : {len(recent_anomalies)} valeurs anormales sur {len(recent_data)} données récentes",
                        rationale=f"Taux d'anomalies de {anomaly_rate*100:.1f}% dépasse seuil acceptable (20%)",
                        
                        suggested_actions=actions,
                        expected_impact={
                            "risk_reduction": "high",
                            "data_quality_improvement": "high", 
                            "business_continuity": "medium",
                            "investigation_time_hours": 8
                        },
                        
                        confidence_score=0.9,
                        risk_level=risk,
                        implementation_effort="low",
                        timeline={
                            "immediate": [actions[0]],
                            "short_term": actions[1:],
                            "long_term": []
                        },
                        
                        supporting_data={
                            "anomaly_count": len(recent_anomalies),
                            "anomaly_rate": float(anomaly_rate),
                            "anomaly_type": anomaly_type,
                            "bounds": {"lower": float(lower_bound), "upper": float(upper_bound)},
                            "recent_anomaly_values": recent_anomalies.tolist()
                        },
                        related_metrics=[col],
                        dependencies=["data_quality_check"],
                        
                        created_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(days=7)  # Urgent
                    )
                    
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_correlation_recommendations(self, data: pd.DataFrame) -> List[Recommendation]:
        """Génère recommandations basées sur corrélations découvertes"""
        
        recommendations = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return recommendations
        
        # Calcul corrélations
        corr_matrix = data[numeric_cols].corr()
        
        # Recherche corrélations fortes entre métriques métier
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i >= j or not (self._is_business_metric(col1) and self._is_business_metric(col2)):
                    continue
                
                correlation = corr_matrix.loc[col1, col2]
                
                if pd.isna(correlation) or abs(correlation) < 0.6:  # Seuil corrélation forte
                    continue
                
                # Interprétation business de la corrélation
                business_insight = self._interpret_business_correlation(col1, col2, correlation)
                
                if business_insight:
                    
                    correlation_strength = "très forte" if abs(correlation) > 0.8 else "forte"
                    correlation_direction = "positive" if correlation > 0 else "négative"
                    
                    title = f"Exploiter corrélation {correlation_strength} : {col1} ↔ {col2}"
                    
                    actions = [
                        {
                            "action": "leverage_correlation",
                            "description": f"Utiliser relation {col1}-{col2} pour optimisation",
                            "priority": "high"
                        },
                        {
                            "action": "causal_analysis",
                            "description": "Analyser causalité de cette relation",
                            "priority": "medium"
                        },
                        {
                            "action": "create_composite_metric",
                            "description": f"Créer métrique combinée {col1}/{col2}",
                            "priority": "low"
                        }
                    ]
                    
                    # Ajout actions spécifiques selon type corrélation
                    actions.extend(business_insight.get('specific_actions', []))
                    
                    recommendation = Recommendation(
                        id=f"corr_{col1}_{col2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        type=business_insight.get('type', RecommendationType.STRATEGIC),
                        priority=RecommendationPriority.MEDIUM,
                        title=title,
                        description=f"Corrélation {correlation_direction} {correlation_strength} ({correlation:.2f}) entre {col1} et {col2}. {business_insight['description']}",
                        rationale=f"Corrélation forte permet optimisation conjointe ou prédiction d'une métrique via l'autre",
                        
                        suggested_actions=actions,
                        expected_impact={
                            "optimization_potential": "medium",
                            "predictive_power": "high" if abs(correlation) > 0.8 else "medium",
                            "strategic_value": business_insight.get('impact', 'medium'),
                            "implementation_complexity": "low"
                        },
                        
                        confidence_score=min(0.9, abs(correlation) + 0.1),
                        risk_level="low",
                        implementation_effort="medium",
                        timeline={
                            "immediate": [],
                            "short_term": actions[:2],
                            "long_term": actions[2:]
                        },
                        
                        supporting_data={
                            "correlation_coefficient": float(correlation),
                            "correlation_strength": correlation_strength,
                            "correlation_direction": correlation_direction,
                            "business_interpretation": business_insight['description']
                        },
                        related_metrics=[col1, col2],
                        dependencies=[],
                        
                        created_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(days=60)
                    )
                    
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_nlp_based_recommendations(self, user_query: str, data: pd.DataFrame) -> List[Recommendation]:
        """Génère recommandations basées sur analyse NLP de la requête utilisateur"""
        
        recommendations = []
        
        # Analyse sentiment et intention
        sentiment_analysis = self._analyze_query_sentiment(user_query)
        intent = self._extract_business_intent(user_query)
        entities = self._extract_business_entities(user_query)
        
        # Génération recommandations selon intent détecté
        if intent == "performance_concern":
            perf_rec = self._generate_performance_recommendations(entities, data, sentiment_analysis)
            if perf_rec:
                recommendations.append(perf_rec)
        
        elif intent == "optimization_request":
            opt_rec = self._generate_optimization_recommendations(entities, data)
            if opt_rec:
                recommendations.append(opt_rec)
        
        elif intent == "trend_inquiry":
            trend_rec = self._generate_trend_recommendations(entities, data)
            if trend_rec:
                recommendations.append(trend_rec)
        
        elif intent == "comparison_request":
            comp_rec = self._generate_comparison_recommendations(entities, data)
            if comp_rec:
                recommendations.append(comp_rec)
        
        return recommendations
    
    def _generate_proactive_recommendations(self, data: pd.DataFrame) -> List[Recommendation]:
        """Génère recommandations proactives basées sur patterns business connus"""
        
        recommendations = []
        
        # 1. Recommandations saisonnières
        seasonal_recs = self._check_seasonal_opportunities(data)
        recommendations.extend(seasonal_recs)
        
        # 2. Recommandations de maintenance prédictive
        maintenance_recs = self._check_maintenance_needs(data)
        recommendations.extend(maintenance_recs)
        
        # 3. Recommandations d'optimisation continue
        optimization_recs = self._check_optimization_opportunities(data)
        recommendations.extend(optimization_recs)
        
        return recommendations
    
    def _filter_and_prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Filtre et priorise recommandations selon contexte métier"""
        
        # Suppression doublons basés sur similarité
        unique_recommendations = self._remove_duplicate_recommendations(recommendations)
        
        # Filtrage selon contraintes métier
        business_filtered = self._filter_by_business_constraints(unique_recommendations)
        
        # Scoring et priorisation
        scored_recommendations = self._score_recommendations(business_filtered)
        
        # Tri par priorité et score
        sorted_recs = sorted(scored_recommendations, 
                           key=lambda x: (
                               x.priority.value, 
                               -x.confidence_score,
                               -x.expected_impact.get('business_value', 0)
                           ))
        
        # Limitation nombre de recommandations (top 10)
        return sorted_recs[:10]
    
    def _generate_recommendation_explanation(self, recommendation: Recommendation, 
                                           data: pd.DataFrame) -> RecommendationExplanation:
        """Génère explication détaillée d'une recommandation"""
        
        reasoning_chain = [
            {
                "step": 1,
                "description": "Analyse des données d'entrée",
                "details": f"Dataset avec {len(data)} lignes et {len(data.columns)} colonnes analysé"
            },
            {
                "step": 2,  
                "description": "Détection pattern/tendance",
                "details": recommendation.rationale
            },
            {
                "step": 3,
                "description": "Application règles métier",
                "details": f"Règles {self.business_context.industry} appliquées"
            },
            {
                "step": 4,
                "description": "Génération actions recommandées", 
                "details": f"{len(recommendation.suggested_actions)} actions identifiées"
            }
        ]
        
        return RecommendationExplanation(
            recommendation_id=recommendation.id,
            reasoning_chain=reasoning_chain,
            data_sources=[f"Dataset principal ({len(data)} rows)"],
            model_insights={
                "confidence": recommendation.confidence_score,
                "supporting_metrics": recommendation.related_metrics
            },
            alternative_scenarios=[],
            sensitivity_analysis={}
        )
    
    # Méthodes utilitaires
    def _is_business_metric(self, column_name: str) -> bool:
        """Vérifie si colonne est métrique business"""
        business_terms = [
            'revenue', 'sales', 'income', 'profit', 'margin', 'cost', 'expense',
            'price', 'quantity', 'volume', 'amount', 'total',
            'customer', 'client', 'user', 'conversion', 'churn', 'retention',
            'traffic', 'views', 'clicks', 'orders', 'transactions'
        ]
        
        return any(term in column_name.lower() for term in business_terms)
    
    def _classify_recommendation_type(self, metric: str) -> RecommendationType:
        """Classifie type de recommandation selon métrique"""
        metric_lower = metric.lower()
        
        if any(term in metric_lower for term in ['price', 'pricing', 'cost']):
            return RecommendationType.PRICING
        elif any(term in metric_lower for term in ['inventory', 'stock', 'supply']):
            return RecommendationType.INVENTORY
        elif any(term in metric_lower for term in ['marketing', 'traffic', 'conversion', 'acquisition']):
            return RecommendationType.MARKETING
        elif any(term in metric_lower for term in ['customer', 'client', 'churn', 'retention']):
            return RecommendationType.CUSTOMER
        elif any(term in metric_lower for term in ['revenue', 'profit', 'margin', 'financial']):
            return RecommendationType.FINANCIAL
        elif any(term in metric_lower for term in ['risk', 'compliance', 'security']):
            return RecommendationType.RISK
        else:
            return RecommendationType.OPERATIONS

# Démonstration du système de recommandations IA
def demo_intelligent_business_recommender():
    """Démonstration système recommandations IA"""
    
    # Contexte métier exemple
    business_context = BusinessContext(
        industry="ecommerce",
        company_size="sme",
        business_model="b2c",
        key_metrics=["revenue", "conversion_rate", "customer_acquisition_cost"],
        constraints={"max_budget": 100000, "min_roi": 2.0},
        objectives=["increase_revenue", "reduce_churn", "optimize_margins"],
        current_performance={
            "revenue": 50000,
            "conversion_rate": 0.025,
            "customer_acquisition_cost": 35
        },
        market_conditions={"growth_rate": 0.15, "competition": "high"}
    )
    
    # Génération données exemple
    np.random.seed(42)
    n_days = 90
    dates = pd.date_range('2025-06-01', periods=n_days, freq='D')
    
    # Simulation e-commerce avec tendances
    base_revenue = 1000
    trend = np.linspace(0, 200, n_days)  # Croissance
    seasonality = 150 * np.sin(2 * np.pi * np.arange(n_days) / 7)  # Pattern hebdomadaire
    noise = np.random.normal(0, 50, n_days)
    
    revenue = base_revenue + trend + seasonality + noise
    
    # Ajout pic Black Friday (simulation)
    weekend_indices = [i for i, date in enumerate(dates) if date.weekday() >= 5]
    for idx in weekend_indices[-2:]:  # Dernier weekend = promotion
        revenue[idx] *= 1.5
    
    # Autres métriques corrélées
    conversion_rate = 0.02 + 0.01 * (revenue / revenue.mean() - 1) + np.random.normal(0, 0.002, n_days)
    conversion_rate = np.clip(conversion_rate, 0.005, 0.05)
    
    traffic = revenue / (conversion_rate * 45)  # AOV ~45€
    customer_acquisition_cost = 25 + 15 * np.random.random(n_days)
    
    df = pd.DataFrame({
        'date': dates,
        'revenue': revenue,
        'traffic': traffic,
        'conversion_rate': conversion_rate,
        'customer_acquisition_cost': customer_acquisition_cost,
        'orders_count': traffic * conversion_rate,
        'avg_order_value': revenue / (traffic * conversion_rate)
    })
    
    print("🤖 DÉMONSTRATION SYSTÈME RECOMMANDATIONS IA")
    print("=" * 60)
    
    # Initialisation système
    recommender = IntelligentBusinessRecommender(business_context)
    
    # Génération recommandations
    recommendations = recommender.generate_recommendations(
        data=df,
        user_query="Je m'inquiète de la performance de mes conversions cette semaine"
    )
    
    print(f"\n🎯 RECOMMANDATIONS GÉNÉRÉES ({len(recommendations)}):")
    print("=" * 60)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec.priority.value.upper()}] {rec.title}")
        print(f"   Type: {rec.type.value} | Confiance: {rec.confidence_score:.1%}")
        print(f"   📋 {rec.description}")
        print(f"   💡 {rec.rationale}")
        
        print(f"   🎯 ACTIONS RECOMMANDÉES:")
        for j, action in enumerate(rec.suggested_actions[:2], 1):  # Top 2 actions
            print(f"      {j}. {action['description']} (Priorité: {action['priority']})")
        
        print(f"   📊 IMPACT ATTENDU:")
        impact = rec.expected_impact
        for key, value in list(impact.items())[:3]:  # Top 3 impacts
            if isinstance(value, (int, float)):
                print(f"      • {key}: {value:,.1f}")
            else:
                print(f"      • {key}: {value}")
        
        print(f"   ⏱️ TIMELINE: {rec.implementation_effort} effort, expire le {rec.expires_at.strftime('%Y-%m-%d')}")
        
        if i >= 3:  # Limite affichage
            break
    
    print(f"\n📈 ANALYSE BUSINESS CONTEXT:")
    print(f"• Industrie: {business_context.industry}")
    print(f"• Taille: {business_context.company_size}")
    print(f"• Objectifs: {', '.join(business_context.objectives)}")
    
    print(f"\n🧠 CAPACITÉS IA UTILISÉES:")
    print(f"• Détection tendances automatique")
    print(f"• Analyse corrélations métier")
    print(f"• Détection anomalies intelligente")
    print(f"• Recommandations contextualisées")
    print(f"• Priorisation basée ROI")
    
    return recommendations

if __name__ == "__main__":
    recommendations = demo_intelligent_business_recommender()
```

## Module 2 : Système d'Interprétation NLP Business

### Processeur de Langage Naturel Métier

```python
# business_nlp_processor.py
"""
Processeur NLP spécialisé pour compréhension et génération de texte métier
Intègre reconnaissance d'entités business, analyse sentiment, génération insights
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

# NLP Libraries
import nltk
from textblob import TextBlob
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel

# Custom business entities
class BusinessNLPProcessor:
    """Processeur NLP spécialisé métier"""
    
    def __init__(self):
        self.business_entities = self._load_business_entities()
        self.sentiment_analyzer = None
        self.intent_classifier = None
        self.setup_nlp_components()
    
    def setup_nlp_components(self):
        """Initialise composants NLP"""
        
        try:
            # Sentiment analysis avec modèle pré-entraîné
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Classification d'intention métier
            self.intent_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"  # Fallback généraliste
            )
            
        except Exception as e:
            logger.warning(f"Modèles Transformers non disponibles: {e}")
            # Fallback vers TextBlob
            self.sentiment_analyzer = None
            
        logger.info("🔤 Processeur NLP métier initialisé")
    
    def analyze_business_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyse complète requête métier"""
        
        analysis = {
            'original_query': query,
            'normalized_query': self._normalize_query(query),
            'sentiment': self._analyze_sentiment(query),
            'intent': self._classify_business_intent(query),
            'entities': self._extract_business_entities(query),
            'metrics_mentioned': self._extract_metrics_references(query),
            'time_references': self._extract_time_references(query),
            'action_verbs': self._extract_action_verbs(query),
            'urgency_level': self._assess_urgency(query),
            'suggested_responses': self._generate_response_suggestions(query, context)
        }
        
        return analysis
    
    def generate_business_insights_text(self, data_insights: List[Dict], target_audience: str = "business") -> str:
        """Génère texte insights métier en langage naturel"""
        
        if target_audience == "executive":
            return self._generate_executive_summary(data_insights)
        elif target_audience == "technical":
            return self._generate_technical_analysis(data_insights)
        else:
            return self._generate_business_narrative(data_insights)
    
    def _classify_business_intent(self, query: str) -> Dict[str, Any]:
        """Classifie intention métier de la requête"""
        
        query_lower = query.lower()
        
        # Patterns d'intention métier
        intent_patterns = {
            'performance_concern': [
                r'\b(worry|concern|problem|issue|drop|decline|decrease|fall|bad|poor|low)\b',
                r'\b(not good|not well|struggling|difficulty)\b'
            ],
            'optimization_request': [
                r'\b(optimize|improve|increase|boost|enhance|maximize|better)\b',
                r'\b(how to|how can|what should|recommend|suggest)\b'
            ],
            'trend_inquiry': [
                r'\b(trend|pattern|evolution|progress|trajectory|forecast)\b',
                r'\b(over time|recently|lately|this month|this week)\b'
            ],
            'comparison_request': [
                r'\b(compare|versus|vs|against|better than|worse than|difference)\b',
                r'\b(benchmark|competitor|market|industry average)\b'
            ],
            'data_exploration': [
                r'\b(show|display|visualize|chart|graph|report|dashboard)\b',
                r'\b(what|which|where|when|why|how much)\b'
            ],
            'alert_setup': [
                r'\b(alert|notify|warning|threshold|monitor|watch)\b',
                r'\b(when|if|whenever|as soon as)\b'
            ]
        }
        
        detected_intents = {}
        
        for intent, patterns in intent_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                matches = re.findall(pattern, query_lower)
                if matches:
                    score += len(matches)
                    matched_patterns.extend(matches)
            
            if score > 0:
                detected_intents[intent] = {
                    'confidence': min(1.0, score * 0.3),
                    'matched_terms': list(set(matched_patterns))
                }
        
        # Intent principal = plus haute confiance
        primary_intent = max(detected_intents.items(), key=lambda x: x[1]['confidence']) if detected_intents else ('generic_inquiry', {'confidence': 0.1})
        
        return {
            'primary_intent': primary_intent[0],
            'confidence': primary_intent[1]['confidence'],
            'all_intents': detected_intents
        }

# Génération automatique de rapports business
def demo_business_nlp_system():
    """Démonstration système NLP métier"""
    
    processor = BusinessNLPProcessor()
    
    # Requêtes utilisateur exemples
    business_queries = [
        "Je suis inquiet de la baisse de nos conversions cette semaine",
        "Comment optimiser notre taux de conversion pour le Black Friday?",
        "Montre-moi l'évolution des revenus par rapport à l'année dernière",
        "Nos coûts d'acquisition client sont-ils compétitifs vs le marché?",
        "Peux-tu analyser la performance de notre campagne email?"
    ]
    
    print("🔤 DÉMONSTRATION SYSTÈME NLP MÉTIER")
    print("=" * 60)
    
    for i, query in enumerate(business_queries, 1):
        print(f"\n📝 REQUÊTE {i}: '{query}'")
        
        analysis = processor.analyze_business_query(query)
        
        print(f"   🎯 Intention: {analysis['intent']['primary_intent']} ({analysis['intent']['confidence']:.1%})")
        print(f"   😊 Sentiment: {analysis['sentiment']['label']} ({analysis['sentiment']['confidence']:.1%})")
        print(f"   📊 Métriques mentionnées: {', '.join(analysis['metrics_mentioned'][:3])}")
        print(f"   ⏰ Références temporelles: {', '.join(analysis['time_references'])}")
        print(f"   🚨 Niveau urgence: {analysis['urgency_level']}")
        
        if analysis['suggested_responses']:
            print(f"   💡 Réponse suggérée: {analysis['suggested_responses'][0][:100]}...")
    
    return processor

if __name__ == "__main__":
    nlp_demo = demo_business_nlp_system()
```

Cette implémentation avancée d'IA métier intégrée offre :

✅ **Recommandations intelligentes** basées sur ML et règles métier
✅ **Analyse NLP avancée** pour compréhension requêtes business
✅ **Génération d'insights automatique** avec explications
✅ **Détection d'anomalies** et alertes proactives
✅ **Optimisation multi-critères** avec contraintes business
✅ **Contextualisation sectorielle** selon industrie
✅ **Priorisation intelligente** basée sur impact ROI
✅ **Interface langage naturel** pour utilisateurs métier
✅ **Traçabilité complète** des raisonnements IA

Le système transforme automatiquement les données et requêtes en recommandations actionnables pour les équipes métier.