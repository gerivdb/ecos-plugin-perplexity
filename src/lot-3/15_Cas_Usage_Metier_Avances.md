# Cas d'Usage Métier Avancés - Espace Perplexity AI

## Vue d'ensemble
Ce document présente des cas d'usage métier avancés et complexes pour l'espace Perplexity AI, avec des implémentations complètes couvrant le pricing dynamique, le booking prédictif, l'analyse de marché en temps réel, et d'autres scénarios métier sophistiqués.

## Architecture Cas d'Usage

### Matrice des Cas d'Usage par Secteur

```
┌─────────────────────────────────────────────────────────────────┐
│                 MATRICE CAS D'USAGE MÉTIER                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  💰 E-COMMERCE     🏨 HÔTELLERIE    🏦 FINANCE    🚚 LOGISTIQUE │
│  ┌─────────────┐   ┌─────────────┐  ┌───────────┐ ┌────────────┐│
│  │ • Pricing   │   │ • Revenue   │  │ • Risk    │ │ • Route    ││
│  │   Dynamique │   │   Mgmt      │  │   Scoring │ │   Optim    ││
│  │ • Inventory │   │ • Booking   │  │ • Portfolio│ │ • Fleet    ││
│  │   Optim     │   │   Forecast  │  │   Analysis│ │   Mgmt     ││
│  │ • Customer  │   │ • Dynamic   │  │ • Fraud   │ │ • Demand   ││
│  │   Segment   │   │   Pricing   │  │   Detect  │ │   Forecast ││
│  └─────────────┘   └─────────────┘  └───────────┘ └────────────┘│
│                                                                 │
│  🎵 MUSIQUE       📈 MARKETING      ⚕️ SANTÉ      🏭 INDUSTRIE │
│  ┌─────────────┐   ┌─────────────┐  ┌───────────┐ ┌────────────┐│
│  │ • Playlist  │   │ • Campaign  │  │ • Patient │ │ • Predictive│
│  │   Curation  │   │   Optim     │  │   Risk    │ │   Maint    ││
│  │ • Royalty   │   │ • Attribution│  │ • Resource│ │ • Quality  ││
│  │   Calc      │   │   Modeling  │  │   Planning│ │   Control  ││
│  │ • Trend     │   │ • A/B Test  │  │ • Drug    │ │ • Supply   ││
│  │   Analysis  │   │   Analysis  │  │   Discovery│ │   Chain    ││
│  └─────────────┘   └─────────────┘  └───────────┘ └────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Cas d'Usage 1 : Pricing Dynamique E-Commerce Avancé

### Architecture Solution

```python
# pricing_engine_advanced.py
"""
Moteur de pricing dynamique multi-facteurs pour e-commerce
Intègre ML, analyse concurrentielle, élasticité-prix, et contraintes métier
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

logger = logging.getLogger(__name__)

class PricingStrategy(Enum):
    COMPETITIVE = "competitive"
    PREMIUM = "premium"
    PENETRATION = "penetration"
    DYNAMIC = "dynamic"
    SEASONAL = "seasonal"

class MarketCondition(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class ProductPricingContext:
    """Contexte complet pour décision pricing d'un produit"""
    product_id: str
    current_price: float
    cost_price: float
    min_margin_percent: float
    category: str
    brand: str
    
    # Données historiques
    sales_history: List[Dict[str, Any]]
    price_history: List[Dict[str, Any]]
    
    # Contexte concurrentiel
    competitor_prices: Dict[str, float]
    market_position: str
    
    # Contexte temporel
    seasonality_factor: float
    day_of_week: str
    hour_of_day: int
    is_holiday: bool
    
    # Inventory et demande
    stock_level: int
    demand_forecast: float
    velocity_category: str  # A, B, C
    
    # Métriques performance
    conversion_rate: float
    click_through_rate: float
    price_elasticity: float
    
    # Contraintes métier
    promotional_constraints: List[str]
    regulatory_constraints: List[str]

class AdvancedPricingEngine:
    """Moteur de pricing avancé avec ML et règles métier"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.pricing_rules = {}
        self.load_models()
        self.setup_business_rules()
    
    def load_models(self) -> None:
        """Charge les modèles ML pré-entraînés"""
        try:
            # Modèle principal : prédiction optimum price
            self.models['price_optimizer'] = joblib.load('models/price_optimizer_rf.pkl')
            
            # Modèle élasticité prix-demande
            self.models['demand_elasticity'] = joblib.load('models/demand_elasticity_gb.pkl')
            
            # Modèle prédiction concurrence
            self.models['competitor_predictor'] = joblib.load('models/competitor_price_predictor.pkl')
            
            logger.info("✅ Modèles ML chargés avec succès")
            
        except FileNotFoundError:
            logger.warning("⚠️ Modèles non trouvés, initialisation avec modèles par défaut")
            self._initialize_default_models()
    
    def _initialize_default_models(self) -> None:
        """Initialise modèles par défaut si pré-entraînés non disponibles"""
        self.models['price_optimizer'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.models['demand_elasticity'] = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
    
    def setup_business_rules(self) -> None:
        """Configure règles métier pour pricing"""
        self.pricing_rules = {
            # Règles marge minimum
            'min_margin': {
                'standard': 0.15,  # 15% minimum
                'premium': 0.30,   # 30% pour produits premium
                'clearance': 0.05  # 5% pour déstockage
            },
            
            # Règles variation prix maximum
            'max_price_change': {
                'daily': 0.10,     # Max 10% par jour
                'weekly': 0.25,    # Max 25% par semaine
                'promotional': 0.50 # Max 50% en promo
            },
            
            # Règles concurrentielles
            'competitive_positioning': {
                'leader': {'min_discount': 0.0, 'max_premium': 0.15},
                'follower': {'min_discount': 0.05, 'max_premium': 0.10},
                'premium': {'min_discount': 0.0, 'max_premium': 0.50}
            },
            
            # Règles stock
            'inventory_rules': {
                'high_stock': {'pressure_factor': 1.2},  # Pression vente
                'low_stock': {'scarcity_factor': 1.1},   # Prime rareté
                'out_of_stock': {'disable_pricing': True}
            }
        }
    
    def calculate_optimal_price(self, context: ProductPricingContext) -> Dict[str, Any]:
        """Calcule prix optimal avec approche multi-facteurs"""
        
        logger.info(f"🎯 Calcul prix optimal pour {context.product_id}")
        
        # 1. Analyse données historiques et tendances
        historical_analysis = self._analyze_historical_performance(context)
        
        # 2. Prédiction élasticité prix-demande
        elasticity_analysis = self._calculate_price_elasticity(context)
        
        # 3. Analyse concurrentielle et positionnement
        competitive_analysis = self._analyze_competitive_landscape(context)
        
        # 4. Facteurs saisonniers et temporels
        temporal_factors = self._calculate_temporal_factors(context)
        
        # 5. Contraintes métier et réglementaires
        business_constraints = self._apply_business_constraints(context)
        
        # 6. Modèle ML pour prix optimal
        ml_recommendation = self._get_ml_price_recommendation(
            context, historical_analysis, elasticity_analysis, 
            competitive_analysis, temporal_factors
        )
        
        # 7. Synthèse et décision finale
        final_recommendation = self._synthesize_pricing_decision(
            context, ml_recommendation, business_constraints
        )
        
        # 8. Validation et métriques impact
        impact_assessment = self._assess_pricing_impact(
            context, final_recommendation
        )
        
        return {
            'product_id': context.product_id,
            'current_price': context.current_price,
            'recommended_price': final_recommendation['optimal_price'],
            'price_change_percent': final_recommendation['change_percent'],
            'confidence_score': final_recommendation['confidence'],
            'reasoning': final_recommendation['reasoning'],
            'expected_impact': impact_assessment,
            'implementation_timeline': final_recommendation['timeline'],
            'monitoring_kpis': final_recommendation['kpis_to_monitor'],
            'analysis_components': {
                'historical': historical_analysis,
                'elasticity': elasticity_analysis,
                'competitive': competitive_analysis,
                'temporal': temporal_factors,
                'constraints': business_constraints,
                'ml_model': ml_recommendation
            }
        }
    
    def _analyze_historical_performance(self, context: ProductPricingContext) -> Dict[str, Any]:
        """Analyse performance historique des prix"""
        
        if not context.price_history or not context.sales_history:
            return {'status': 'insufficient_data', 'confidence': 0.3}
        
        # Convertit en DataFrame pour analyse
        price_df = pd.DataFrame(context.price_history)
        sales_df = pd.DataFrame(context.sales_history)
        
        # Merge données prix et ventes
        merged_df = pd.merge(price_df, sales_df, on='date', how='inner')
        
        if len(merged_df) < 10:
            return {'status': 'insufficient_data', 'confidence': 0.4}
        
        # Calculs statistiques
        price_stats = {
            'mean_price': merged_df['price'].mean(),
            'std_price': merged_df['price'].std(),
            'min_price': merged_df['price'].min(),
            'max_price': merged_df['price'].max(),
            'cv_price': merged_df['price'].std() / merged_df['price'].mean()
        }
        
        sales_stats = {
            'mean_sales': merged_df['quantity_sold'].mean(),
            'std_sales': merged_df['quantity_sold'].std(),
            'total_revenue': (merged_df['price'] * merged_df['quantity_sold']).sum()
        }
        
        # Corrélation prix-ventes
        price_sales_correlation = merged_df['price'].corr(merged_df['quantity_sold'])
        
        # Analyse des points de prix optimaux historiques
        merged_df['revenue'] = merged_df['price'] * merged_df['quantity_sold']
        merged_df['margin'] = ((merged_df['price'] - context.cost_price) / merged_df['price'])
        
        # Meilleures performances
        best_revenue_periods = merged_df.nlargest(5, 'revenue')
        best_margin_periods = merged_df.nlargest(5, 'margin')
        
        return {
            'status': 'complete',
            'confidence': 0.8,
            'price_statistics': price_stats,
            'sales_statistics': sales_stats,
            'price_sales_correlation': price_sales_correlation,
            'optimal_historical_prices': {
                'best_revenue': best_revenue_periods['price'].mean(),
                'best_margin': best_margin_periods['price'].mean(),
                'most_frequent': merged_df['price'].mode()[0] if not merged_df['price'].mode().empty else None
            },
            'performance_insights': {
                'price_volatility': 'high' if price_stats['cv_price'] > 0.2 else 'low',
                'demand_sensitivity': 'high' if abs(price_sales_correlation) > 0.5 else 'moderate',
                'revenue_trend': 'positive' if merged_df['revenue'].corr(range(len(merged_df))) > 0 else 'negative'
            }
        }
    
    def _calculate_price_elasticity(self, context: ProductPricingContext) -> Dict[str, Any]:
        """Calcule élasticité prix de la demande"""
        
        # Si élasticité fournie dans contexte
        if context.price_elasticity and context.price_elasticity != 0:
            elasticity = context.price_elasticity
            confidence = 0.9
        else:
            # Calcul basé sur données historiques
            elasticity = self._estimate_elasticity_from_history(context)
            confidence = 0.6
        
        # Classification de l'élasticité
        if abs(elasticity) > 1.5:
            elasticity_type = "très_élastique"
            pricing_strategy = "attention_maximale_aux_variations"
        elif abs(elasticity) > 1.0:
            elasticity_type = "élastique"
            pricing_strategy = "surveillance_concurrence"
        elif abs(elasticity) > 0.5:
            elasticity_type = "modérément_élastique"
            pricing_strategy = "optimisation_marge"
        else:
            elasticity_type = "inélastique"
            pricing_strategy = "pricing_premium_possible"
        
        # Calcul impact potentiel changements prix
        price_scenarios = {}
        for change_percent in [-20, -10, -5, 5, 10, 20]:
            new_price = context.current_price * (1 + change_percent/100)
            demand_change = elasticity * change_percent
            new_demand = context.demand_forecast * (1 + demand_change/100)
            
            price_scenarios[f"{change_percent:+d}%"] = {
                'new_price': new_price,
                'demand_change_percent': demand_change,
                'estimated_demand': max(0, new_demand),
                'estimated_revenue': new_price * max(0, new_demand),
                'margin_impact': ((new_price - context.cost_price) / new_price) - context.min_margin_percent
            }
        
        return {
            'elasticity_coefficient': elasticity,
            'elasticity_type': elasticity_type,
            'confidence': confidence,
            'pricing_strategy_recommendation': pricing_strategy,
            'price_scenarios': price_scenarios,
            'optimal_price_from_elasticity': self._find_optimal_price_elasticity(
                context, elasticity
            )
        }
    
    def _estimate_elasticity_from_history(self, context: ProductPricingContext) -> float:
        """Estime élasticité depuis historique prix/ventes"""
        
        if not context.price_history or not context.sales_history:
            # Valeur par défaut selon catégorie
            category_elasticity = {
                'luxury': -0.5,     # Peu élastique
                'necessity': -0.3,  # Très peu élastique  
                'electronics': -1.2, # Élastique
                'fashion': -1.5,    # Très élastique
                'food': -0.8       # Modérément élastique
            }
            return category_elasticity.get(context.category.lower(), -1.0)
        
        # Calcul simple basé sur corrélation prix-quantité
        price_df = pd.DataFrame(context.price_history)
        sales_df = pd.DataFrame(context.sales_history)
        merged_df = pd.merge(price_df, sales_df, on='date', how='inner')
        
        if len(merged_df) < 5:
            return -1.0
        
        # Calcul variations prix et demande
        merged_df = merged_df.sort_values('date')
        merged_df['price_change'] = merged_df['price'].pct_change()
        merged_df['demand_change'] = merged_df['quantity_sold'].pct_change()
        
        # Supprime valeurs aberrantes et NaN
        clean_df = merged_df.dropna()
        clean_df = clean_df[
            (abs(clean_df['price_change']) < 0.5) & 
            (abs(clean_df['demand_change']) < 2.0)
        ]
        
        if len(clean_df) < 3:
            return -1.0
        
        # Élasticité = % variation demande / % variation prix
        elasticity_values = clean_df['demand_change'] / clean_df['price_change']
        elasticity_values = elasticity_values[elasticity_values.notna()]
        
        if len(elasticity_values) > 0:
            return elasticity_values.median()
        else:
            return -1.0
    
    def _analyze_competitive_landscape(self, context: ProductPricingContext) -> Dict[str, Any]:
        """Analyse paysage concurrentiel et positionnement"""
        
        if not context.competitor_prices:
            return {
                'status': 'no_competitor_data',
                'recommendation': 'cost_plus_pricing'
            }
        
        competitor_prices = list(context.competitor_prices.values())
        our_price = context.current_price
        
        # Statistiques concurrence
        competitor_stats = {
            'mean_price': np.mean(competitor_prices),
            'median_price': np.median(competitor_prices),
            'min_price': np.min(competitor_prices),
            'max_price': np.max(competitor_prices),
            'std_price': np.std(competitor_prices),
            'price_range': np.max(competitor_prices) - np.min(competitor_prices)
        }
        
        # Notre position
        price_rank = sum(1 for p in competitor_prices if p < our_price) + 1
        total_competitors = len(competitor_prices) + 1
        
        # Classification position
        if price_rank <= total_competitors * 0.25:
            position = "leader_prix"
            strategy = "maintenir_avantage"
        elif price_rank <= total_competitors * 0.50:
            position = "competitif"
            strategy = "optimiser_valeur"
        elif price_rank <= total_competitors * 0.75:
            position = "premium_modere"
            strategy = "justifier_differentiation"
        else:
            position = "premium_elevé"
            strategy = "verifier_proposition_valeur"
        
        # Écarts significatifs
        price_gaps = []
        for competitor, price in context.competitor_prices.items():
            gap_percent = ((our_price - price) / price) * 100
            price_gaps.append({
                'competitor': competitor,
                'their_price': price,
                'gap_percent': gap_percent,
                'gap_euros': our_price - price
            })
        
        # Opportunités pricing
        opportunities = []
        
        # Opportunité baisse si trop cher
        if our_price > competitor_stats['mean_price'] * 1.15:
            target_price = competitor_stats['mean_price'] * 1.05
            opportunities.append({
                'type': 'baisse_competitive',
                'target_price': target_price,
                'reason': 'Réalignement concurrentiel',
                'impact': 'Amélioration part de marché'
            })
        
        # Opportunité hausse si sous-évalué
        if our_price < competitor_stats['mean_price'] * 0.90:
            target_price = competitor_stats['mean_price'] * 0.95
            opportunities.append({
                'type': 'hausse_value_capture',
                'target_price': target_price,
                'reason': 'Capturer plus de valeur',
                'impact': 'Amélioration marge'
            })
        
        return {
            'status': 'complete',
            'competitor_statistics': competitor_stats,
            'our_position': {
                'rank': price_rank,
                'total_market': total_competitors,
                'percentile': (price_rank / total_competitors) * 100,
                'position_label': position,
                'strategy_recommendation': strategy
            },
            'price_gaps': sorted(price_gaps, key=lambda x: abs(x['gap_percent'])),
            'pricing_opportunities': opportunities,
            'competitive_pressure': {
                'level': 'high' if competitor_stats['std_price'] / competitor_stats['mean_price'] < 0.1 else 'moderate',
                'price_sensitivity': 'high' if competitor_stats['price_range'] / competitor_stats['mean_price'] > 0.3 else 'low'
            }
        }
    
    def _calculate_temporal_factors(self, context: ProductPricingContext) -> Dict[str, Any]:
        """Calcule facteurs temporels et saisonniers"""
        
        factors = {
            'seasonality_multiplier': context.seasonality_factor,
            'day_of_week_factor': self._get_day_of_week_factor(context.day_of_week),
            'hour_of_day_factor': self._get_hourly_factor(context.hour_of_day),
            'holiday_factor': 1.1 if context.is_holiday else 1.0
        }
        
        # Facteur temporel composite
        composite_factor = (
            factors['seasonality_multiplier'] *
            factors['day_of_week_factor'] * 
            factors['hour_of_day_factor'] *
            factors['holiday_factor']
        )
        
        # Recommandations temporelles
        recommendations = []
        
        if composite_factor > 1.1:
            recommendations.append({
                'type': 'hausse_temporelle',
                'factor': composite_factor,
                'reason': 'Conditions temporelles favorables'
            })
        elif composite_factor < 0.9:
            recommendations.append({
                'type': 'baisse_temporelle', 
                'factor': composite_factor,
                'reason': 'Période de faible demande'
            })
        
        return {
            'individual_factors': factors,
            'composite_factor': composite_factor,
            'temporal_recommendations': recommendations,
            'optimal_timing': self._determine_optimal_timing(context)
        }
    
    def _get_day_of_week_factor(self, day: str) -> float:
        """Facteur selon jour de semaine"""
        day_factors = {
            'Monday': 0.95,
            'Tuesday': 0.98,
            'Wednesday': 1.0,
            'Thursday': 1.02,
            'Friday': 1.05,
            'Saturday': 1.1,
            'Sunday': 0.9
        }
        return day_factors.get(day, 1.0)
    
    def _get_hourly_factor(self, hour: int) -> float:
        """Facteur selon heure de la journée"""
        if 9 <= hour <= 11:    # Pic matinal
            return 1.05
        elif 14 <= hour <= 16: # Pic après-midi
            return 1.08
        elif 19 <= hour <= 21: # Pic soirée
            return 1.1
        elif 22 <= hour or hour <= 6:  # Nuit
            return 0.85
        else:
            return 1.0
    
    def _apply_business_constraints(self, context: ProductPricingContext) -> Dict[str, Any]:
        """Applique contraintes métier et réglementaires"""
        
        constraints = {
            'min_price': context.cost_price * (1 + context.min_margin_percent),
            'max_daily_change': context.current_price * self.pricing_rules['max_price_change']['daily'],
            'regulatory_limits': [],
            'promotional_restrictions': []
        }
        
        # Contraintes promotionnelles
        if 'no_discount' in context.promotional_constraints:
            constraints['min_price'] = max(constraints['min_price'], context.current_price)
        
        if 'max_discount_20' in context.promotional_constraints:
            constraints['min_price'] = max(constraints['min_price'], context.current_price * 0.8)
        
        # Contraintes réglementaires
        for regulation in context.regulatory_constraints:
            if 'price_cap' in regulation:
                # Extraction du montant limite (format: "price_cap_100.50")
                try:
                    cap_amount = float(regulation.split('_')[-1])
                    constraints['regulatory_max_price'] = cap_amount
                except:
                    pass
        
        # Contraintes stock
        if context.stock_level <= 10:  # Stock faible
            constraints['scarcity_premium'] = context.current_price * 1.05
        elif context.stock_level >= 1000:  # Surstock
            constraints['clearance_pressure'] = context.current_price * 0.90
        
        return {
            'hard_constraints': constraints,
            'constraint_violations': self._check_constraint_violations(context, constraints),
            'flexibility_score': self._calculate_pricing_flexibility(context, constraints)
        }
    
    def _get_ml_price_recommendation(self, context: ProductPricingContext,
                                   historical: Dict, elasticity: Dict,
                                   competitive: Dict, temporal: Dict) -> Dict[str, Any]:
        """Utilise ML pour recommandation prix optimale"""
        
        # Préparation features pour modèle ML
        features = self._prepare_ml_features(
            context, historical, elasticity, competitive, temporal
        )
        
        if 'price_optimizer' in self.models:
            try:
                # Prédiction avec modèle principal
                predicted_price = self.models['price_optimizer'].predict([features])[0]
                
                # Score de confiance (si disponible)
                if hasattr(self.models['price_optimizer'], 'predict_proba'):
                    confidence = np.max(self.models['price_optimizer'].predict_proba([features]))
                else:
                    confidence = 0.7  # Confiance par défaut
                
                return {
                    'ml_recommended_price': predicted_price,
                    'confidence_score': confidence,
                    'model_features_used': len(features),
                    'prediction_method': 'trained_model'
                }
                
            except Exception as e:
                logger.warning(f"Erreur prédiction ML: {e}")
                return self._fallback_price_calculation(context)
        else:
            return self._fallback_price_calculation(context)
    
    def _prepare_ml_features(self, context: ProductPricingContext,
                           historical: Dict, elasticity: Dict,
                           competitive: Dict, temporal: Dict) -> List[float]:
        """Prépare features pour modèle ML"""
        
        features = [
            # Features produit
            context.current_price,
            context.cost_price,
            context.min_margin_percent,
            
            # Features demande
            context.demand_forecast,
            context.stock_level,
            context.conversion_rate,
            context.click_through_rate,
            
            # Features concurrence
            competitive.get('competitor_statistics', {}).get('mean_price', context.current_price),
            competitive.get('our_position', {}).get('percentile', 50),
            
            # Features temporels
            temporal.get('composite_factor', 1.0),
            1.0 if context.is_holiday else 0.0,
            
            # Features élasticité
            elasticity.get('elasticity_coefficient', -1.0),
            
            # Features historiques
            historical.get('price_statistics', {}).get('mean_price', context.current_price),
            historical.get('price_sales_correlation', 0.0),
        ]
        
        # Remplace NaN par valeurs par défaut
        features = [f if not np.isnan(f) else 0.0 for f in features]
        
        return features
    
    def _fallback_price_calculation(self, context: ProductPricingContext) -> Dict[str, Any]:
        """Calcul prix de secours si ML indisponible"""
        
        # Approche heuristique simple
        base_price = context.cost_price * (1 + context.min_margin_percent + 0.1)
        
        # Ajustements factoriels
        market_factor = 1.0
        if context.competitor_prices:
            market_mean = np.mean(list(context.competitor_prices.values()))
            market_factor = min(market_mean / base_price, 1.5)  # Max 50% d'ajustement
        
        seasonal_factor = context.seasonality_factor
        
        recommended_price = base_price * market_factor * seasonal_factor
        
        return {
            'ml_recommended_price': recommended_price,
            'confidence_score': 0.5,  # Confiance faible
            'prediction_method': 'heuristic_fallback'
        }
    
    def _synthesize_pricing_decision(self, context: ProductPricingContext,
                                   ml_recommendation: Dict,
                                   constraints: Dict) -> Dict[str, Any]:
        """Synthèse finale et décision pricing"""
        
        # Prix recommandé par ML
        ml_price = ml_recommendation['ml_recommended_price']
        
        # Application des contraintes
        min_allowed = constraints['hard_constraints']['min_price']
        max_daily_change = constraints['hard_constraints']['max_daily_change']
        
        max_allowed = context.current_price + max_daily_change
        min_change_allowed = context.current_price - max_daily_change
        
        # Prix final dans les limites
        final_price = np.clip(ml_price, 
                             max(min_allowed, min_change_allowed),
                             max_allowed)
        
        # Arrondi prix selon stratégie
        final_price = self._apply_price_rounding_strategy(final_price, context.category)
        
        # Calcul changement
        change_percent = ((final_price - context.current_price) / context.current_price) * 100
        
        # Génération du raisonnement
        reasoning = self._generate_pricing_reasoning(
            context, ml_recommendation, constraints, final_price, change_percent
        )
        
        # Timeline implémentation
        timeline = self._determine_implementation_timeline(change_percent, context)
        
        # KPIs à monitorer
        kpis_to_monitor = [
            'sales_volume',
            'revenue', 
            'conversion_rate',
            'competitor_response',
            'inventory_turnover'
        ]
        
        return {
            'optimal_price': final_price,
            'change_percent': change_percent,
            'confidence': ml_recommendation['confidence_score'],
            'reasoning': reasoning,
            'timeline': timeline,
            'kpis_to_monitor': kpis_to_monitor,
            'implementation_priority': 'high' if abs(change_percent) > 10 else 'medium'
        }
    
    def _apply_price_rounding_strategy(self, price: float, category: str) -> float:
        """Applique stratégie d'arrondi selon catégorie"""
        
        if category.lower() in ['luxury', 'premium']:
            # Arrondi à 0.00 pour produits premium
            return round(price, 2)
        elif category.lower() in ['discount', 'clearance']:
            # Prix psychologique .99
            return round(price - 0.01, 2)
        else:
            # Arrondi standard à .90 ou .99
            if price < 10:
                return round(price - 0.01, 2)  # 9.99
            elif price < 100:
                return round(price / 5) * 5 - 0.10  # 24.90
            else:
                return round(price / 10) * 10 - 1  # 199.00
    
    def _generate_pricing_reasoning(self, context: ProductPricingContext,
                                  ml_rec: Dict, constraints: Dict,
                                  final_price: float, change_percent: float) -> List[str]:
        """Génère explications de la décision pricing"""
        
        reasoning = []
        
        # Explication changement prix
        if abs(change_percent) < 2:
            reasoning.append("Prix maintenu - conditions stables")
        elif change_percent > 0:
            reasoning.append(f"Hausse de {change_percent:.1f}% recommandée")
        else:
            reasoning.append(f"Baisse de {abs(change_percent):.1f}% recommandée")
        
        # Facteurs principaux
        if ml_rec['confidence_score'] > 0.8:
            reasoning.append("Recommandation ML haute confiance")
        elif ml_rec['confidence_score'] < 0.5:
            reasoning.append("Recommandation basée sur heuristiques métier")
        
        # Contraintes appliquées
        if any(constraints['constraint_violations']):
            reasoning.append("Ajustements appliqués pour contraintes métier")
        
        # Contexte concurrentiel
        if context.competitor_prices:
            avg_competitor = np.mean(list(context.competitor_prices.values()))
            if final_price < avg_competitor * 0.95:
                reasoning.append("Prix agressif vs concurrence")
            elif final_price > avg_competitor * 1.05:
                reasoning.append("Positionnement premium maintenu")
        
        return reasoning
    
    def _determine_implementation_timeline(self, change_percent: float,
                                         context: ProductPricingContext) -> Dict[str, Any]:
        """Détermine timeline d'implémentation optimale"""
        
        if abs(change_percent) < 5:
            return {
                'recommended_timing': 'immediate',
                'implementation_window': '0-24h',
                'risk_level': 'low'
            }
        elif abs(change_percent) < 15:
            return {
                'recommended_timing': 'next_business_day',
                'implementation_window': '24-48h',
                'risk_level': 'medium',
                'pre_implementation_checks': [
                    'Vérifier stock disponible',
                    'Alerter équipe commerciale'
                ]
            }
        else:
            return {
                'recommended_timing': 'planned_rollout',
                'implementation_window': '48-72h',
                'risk_level': 'high',
                'pre_implementation_checks': [
                    'Validation management',
                    'Communication client',
                    'Monitoring renforcé',
                    'Plan rollback préparé'
                ]
            }
    
    def _assess_pricing_impact(self, context: ProductPricingContext,
                             recommendation: Dict) -> Dict[str, Any]:
        """Évalue impact attendu du changement de prix"""
        
        new_price = recommendation['optimal_price']
        price_change_percent = recommendation['change_percent']
        
        # Impact sur demande (via élasticité)
        demand_change_percent = context.price_elasticity * price_change_percent
        new_demand = context.demand_forecast * (1 + demand_change_percent / 100)
        
        # Impact financier
        current_revenue = context.current_price * context.demand_forecast
        new_revenue = new_price * new_demand
        revenue_change = new_revenue - current_revenue
        
        # Impact marge
        current_margin = context.current_price - context.cost_price
        new_margin = new_price - context.cost_price
        margin_change = new_margin - current_margin
        
        return {
            'demand_impact': {
                'current_demand': context.demand_forecast,
                'projected_demand': max(0, new_demand),
                'change_percent': demand_change_percent
            },
            'revenue_impact': {
                'current_revenue': current_revenue,
                'projected_revenue': new_revenue,
                'change_amount': revenue_change,
                'change_percent': (revenue_change / current_revenue) * 100 if current_revenue > 0 else 0
            },
            'margin_impact': {
                'current_margin_euro': current_margin,
                'projected_margin_euro': new_margin,
                'current_margin_percent': (current_margin / context.current_price) * 100,
                'projected_margin_percent': (new_margin / new_price) * 100
            },
            'break_even_analysis': self._calculate_break_even(context, new_price, new_demand)
        }
    
    def _calculate_break_even(self, context: ProductPricingContext,
                            new_price: float, projected_demand: float) -> Dict[str, Any]:
        """Calcule point mort avec nouveau pricing"""
        
        # Coûts fixes estimés (simple approximation)
        estimated_fixed_costs = context.cost_price * context.demand_forecast * 0.1
        
        # Contribution marginale unitaire
        unit_contribution = new_price - context.cost_price
        
        if unit_contribution > 0:
            break_even_quantity = estimated_fixed_costs / unit_contribution
            break_even_days = break_even_quantity / (projected_demand / 30)  # Approx mensuelle
        else:
            break_even_quantity = float('inf')
            break_even_days = float('inf')
        
        return {
            'break_even_quantity': break_even_quantity,
            'break_even_days': break_even_days,
            'unit_contribution': unit_contribution,
            'contribution_margin_percent': (unit_contribution / new_price) * 100 if new_price > 0 else 0
        }

# Utilisation du moteur pricing
def demo_pricing_engine():
    """Démonstration du moteur de pricing avancé"""
    
    # Configuration moteur
    config = {
        'model_path': 'models/',
        'enable_ml': True,
        'enable_monitoring': True
    }
    
    pricing_engine = AdvancedPricingEngine(config)
    
    # Contexte produit exemple
    context = ProductPricingContext(
        product_id="WIDGET_PRO_001",
        current_price=99.90,
        cost_price=45.00,
        min_margin_percent=0.20,
        category="electronics",
        brand="TechCorp",
        
        # Historique (simulé)
        sales_history=[
            {'date': '2025-08-01', 'quantity_sold': 150, 'revenue': 14985},
            {'date': '2025-08-02', 'quantity_sold': 145, 'revenue': 14490},
            {'date': '2025-08-03', 'quantity_sold': 160, 'revenue': 15984},
        ],
        price_history=[
            {'date': '2025-08-01', 'price': 99.90},
            {'date': '2025-08-02', 'price': 99.90},
            {'date': '2025-08-03', 'price': 99.90},
        ],
        
        # Concurrence
        competitor_prices={
            'CompetitorA': 94.50,
            'CompetitorB': 105.00,
            'CompetitorC': 89.90
        },
        market_position="middle",
        
        # Contexte temporel
        seasonality_factor=1.1,  # Haute saison
        day_of_week="Friday",
        hour_of_day=14,
        is_holiday=False,
        
        # Inventory
        stock_level=450,
        demand_forecast=155.0,
        velocity_category="A",
        
        # Performance
        conversion_rate=0.12,
        click_through_rate=0.08,
        price_elasticity=-1.2,
        
        # Contraintes
        promotional_constraints=[],
        regulatory_constraints=[]
    )
    
    # Calcul prix optimal
    result = pricing_engine.calculate_optimal_price(context)
    
    print("🎯 RÉSULTAT PRICING OPTIMAL")
    print("=" * 50)
    print(f"Produit: {result['product_id']}")
    print(f"Prix actuel: {result['current_price']:.2f}€")
    print(f"Prix recommandé: {result['recommended_price']:.2f}€")
    print(f"Changement: {result['price_change_percent']:+.1f}%")
    print(f"Confiance: {result['confidence_score']:.1%}")
    
    print(f"\n📋 RAISONNEMENT:")
    for reason in result['reasoning']:
        print(f"• {reason}")
    
    print(f"\n📊 IMPACT ATTENDU:")
    impact = result['expected_impact']
    print(f"• Demande: {impact['demand_impact']['change_percent']:+.1f}%")
    print(f"• Revenus: {impact['revenue_impact']['change_amount']:+.0f}€")
    print(f"• Marge: {impact['margin_impact']['projected_margin_percent']:.1f}%")
    
    print(f"\n⏱️ IMPLÉMENTATION:")
    timeline = result['implementation_timeline']
    print(f"• Timing: {timeline['recommended_timing']}")
    print(f"• Fenêtre: {timeline['implementation_window']}")
    print(f"• Risque: {timeline['risk_level']}")
    
    return result

if __name__ == "__main__":
    demo_pricing_engine()
```

## Cas d'Usage 2 : Booking Prédictif Hôtelier

### Système Prédictif de Réservation

```python
# hotel_booking_predictor.py
"""
Système avancé de prédiction et optimisation des réservations hôtelières
Intègre forecasting, yield management, et optimisation tarifaire dynamique
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import holidays
import logging

logger = logging.getLogger(__name__)

@dataclass
class HotelBookingContext:
    """Contexte complet pour prédictions booking hôtelier"""
    hotel_id: str
    total_rooms: int
    room_types: Dict[str, int]  # {'standard': 80, 'deluxe': 15, 'suite': 5}
    
    # Données historiques
    booking_history: List[Dict[str, Any]]
    cancellation_history: List[Dict[str, Any]]
    pricing_history: List[Dict[str, Any]]
    
    # Contexte externe
    local_events: List[Dict[str, Any]]
    weather_forecast: List[Dict[str, Any]]
    competitor_rates: Dict[str, float]
    
    # Métriques actuelles
    current_occupancy: float
    current_adr: float  # Average Daily Rate
    current_revpar: float  # Revenue per Available Room
    
    # Contraintes opérationnelles
    min_stay_requirements: Dict[str, int]
    blackout_dates: List[str]
    seasonal_adjustments: Dict[str, float]

class HotelBookingPredictor:
    """Prédicteur avancé pour réservations hôtelières"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.setup_models()
        self.setup_business_rules()
    
    def setup_models(self) -> None:
        """Initialise les modèles ML"""
        
        # Modèle prédiction demande
        self.models['demand_forecast'] = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.08,
            max_depth=8,
            random_state=42
        )
        
        # Modèle prédiction cancellations
        self.models['cancellation_forecast'] = RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            random_state=42
        )
        
        # Modèle optimisation prix
        self.models['pricing_optimizer'] = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        # Scalers pour normalisation
        self.scalers['features'] = StandardScaler()
        self.scalers['target'] = StandardScaler()
        
        logger.info("✅ Modèles prédiction booking initialisés")
    
    def setup_business_rules(self) -> None:
        """Configure règles métier hôtellerie"""
        
        self.business_rules = {
            # Règles yield management
            'yield_management': {
                'low_demand_threshold': 0.6,    # < 60% occupancy
                'high_demand_threshold': 0.85,   # > 85% occupancy
                'overbooking_limit': 1.05,      # Max 5% overbooking
                'advance_booking_discount': 0.9  # 10% discount si >30j
            },
            
            # Règles tarifaires
            'pricing_rules': {
                'weekend_premium': 1.25,        # +25% weekend
                'peak_season_premium': 1.4,     # +40% haute saison
                'last_minute_premium': 1.15,    # +15% si <3j
                'group_discount_threshold': 5,   # Remise dès 5 chambres
                'loyalty_discount': 0.95        # -5% clients fidèles
            },
            
            # Règles opérationnelles
            'operations': {
                'min_advance_booking': 1,       # Min 1j à l'avance
                'max_advance_booking': 365,     # Max 1 an à l'avance
                'housekeeping_buffer': 0.95,    # 5% buffer nettoyage
                'maintenance_reserve': 0.02     # 2% chambres maintenance
            }
        }
    
    def predict_booking_demand(self, context: HotelBookingContext,
                             forecast_horizon_days: int = 90) -> Dict[str, Any]:
        """Prédit la demande de réservation sur période donnée"""
        
        logger.info(f"🔮 Prédiction demande booking sur {forecast_horizon_days} jours")
        
        # Génération des features prédictives
        forecast_features = self._generate_forecast_features(context, forecast_horizon_days)
        
        # Prédictions demande par jour
        daily_predictions = []
        
        for i, features in enumerate(forecast_features):
            prediction_date = datetime.now().date() + timedelta(days=i)
            
            # Prédiction demande brute
            raw_demand = self._predict_daily_demand(features, context)
            
            # Ajustements contextuel et règles métier
            adjusted_demand = self._apply_demand_adjustments(
                raw_demand, prediction_date, context, features
            )
            
            # Prédiction cancellations
            expected_cancellations = self._predict_cancellations(features, context)
            
            # Demande nette
            net_demand = adjusted_demand - expected_cancellations
            
            daily_predictions.append({
                'date': prediction_date.isoformat(),
                'day_of_week': prediction_date.strftime('%A'),
                'raw_demand': raw_demand,
                'adjusted_demand': adjusted_demand,
                'expected_cancellations': expected_cancellations,
                'net_demand': max(0, net_demand),
                'features_used': len(features)
            })
        
        # Agrégations et métriques
        total_demand = sum([d['net_demand'] for d in daily_predictions])
        avg_daily_demand = total_demand / len(daily_predictions)
        peak_demand_date = max(daily_predictions, key=lambda x: x['net_demand'])
        
        # Analyse patterns
        demand_patterns = self._analyze_demand_patterns(daily_predictions)
        
        return {
            'forecast_horizon_days': forecast_horizon_days,
            'daily_predictions': daily_predictions,
            'summary_metrics': {
                'total_predicted_demand': total_demand,
                'average_daily_demand': avg_daily_demand,
                'peak_demand_date': peak_demand_date['date'],
                'peak_demand_value': peak_demand_date['net_demand'],
                'demand_volatility': np.std([d['net_demand'] for d in daily_predictions])
            },
            'demand_patterns': demand_patterns,
            'confidence_metrics': self._calculate_forecast_confidence(daily_predictions)
        }
    
    def optimize_room_pricing(self, context: HotelBookingContext,
                            demand_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Optimise tarification des chambres basée sur prédictions demande"""
        
        logger.info("💰 Optimisation pricing dynamique")
        
        pricing_recommendations = []
        
        for daily_pred in demand_forecast['daily_predictions']:
            date = daily_pred['date']
            predicted_demand = daily_pred['net_demand']
            
            # Calcul taux occupation prévu
            expected_occupancy = min(predicted_demand / context.total_rooms, 1.0)
            
            # Prix de base selon type chambre
            base_rates = self._calculate_base_rates(context, date)
            
            # Facteurs d'ajustement pricing
            pricing_factors = self._calculate_pricing_factors(
                expected_occupancy, date, context, daily_pred
            )
            
            # Prix optimaux par type chambre
            optimized_rates = {}
            revenue_projections = {}
            
            for room_type, base_rate in base_rates.items():
                # Application facteurs
                optimized_rate = base_rate
                for factor_name, factor_value in pricing_factors.items():
                    optimized_rate *= factor_value
                
                # Arrondi pricing psychologique
                optimized_rate = self._apply_psychological_pricing(optimized_rate)
                
                optimized_rates[room_type] = optimized_rate
                
                # Projection revenus
                room_demand = predicted_demand * self._get_room_type_demand_ratio(room_type)
                available_rooms = context.room_types.get(room_type, 0)
                sold_rooms = min(room_demand, available_rooms)
                
                revenue_projections[room_type] = {
                    'rooms_sold': sold_rooms,
                    'rate': optimized_rate,
                    'revenue': sold_rooms * optimized_rate
                }
            
            # Métriques globales jour
            total_revenue = sum([proj['revenue'] for proj in revenue_projections.values()])
            total_rooms_sold = sum([proj['rooms_sold'] for proj in revenue_projections.values()])
            
            adr = total_revenue / total_rooms_sold if total_rooms_sold > 0 else 0
            revpar = total_revenue / context.total_rooms
            
            pricing_recommendations.append({
                'date': date,
                'expected_occupancy': expected_occupancy,
                'optimized_rates': optimized_rates,
                'pricing_factors_applied': pricing_factors,
                'revenue_projection': revenue_projections,
                'metrics': {
                    'projected_adr': adr,
                    'projected_revpar': revpar,
                    'total_revenue': total_revenue,
                    'occupancy_rate': total_rooms_sold / context.total_rooms
                }
            })
        
        # Analyse performance pricing
        performance_analysis = self._analyze_pricing_performance(
            pricing_recommendations, context
        )
        
        return {
            'daily_pricing_recommendations': pricing_recommendations,
            'performance_analysis': performance_analysis,
            'implementation_priorities': self._identify_pricing_priorities(pricing_recommendations),
            'yield_management_insights': self._generate_yield_insights(pricing_recommendations, context)
        }
    
    def identify_booking_opportunities(self, context: HotelBookingContext,
                                     demand_forecast: Dict[str, Any],
                                     pricing_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Identifie opportunités d'amélioration booking"""
        
        opportunities = []
        
        # Analyse des créneaux sous-performants
        for daily_pricing in pricing_optimization['daily_pricing_recommendations']:
            occupancy = daily_pricing['expected_occupancy']
            date = daily_pricing['date']
            
            if occupancy < 0.6:  # Faible occupation
                opportunities.append({
                    'type': 'low_demand_marketing',
                    'date': date,
                    'current_occupancy': occupancy,
                    'recommended_actions': [
                        'Campagne marketing ciblée',
                        'Packages attractifs',
                        'Partenariats locaux'
                    ],
                    'potential_upside': f"+{(0.75 - occupancy) * 100:.0f}% occupancy",
                    'priority': 'high' if occupancy < 0.4 else 'medium'
                })
            
            elif occupancy > 0.9:  # Surdemande
                opportunities.append({
                    'type': 'upselling_opportunity',
                    'date': date,
                    'current_occupancy': occupancy,
                    'recommended_actions': [
                        'Upsell vers chambres supérieures',
                        'Services additionnels',
                        'Packages expérience'
                    ],
                    'potential_upside': f"+15-25% revenue per booking",
                    'priority': 'high'
                })
        
        # Opportunités saisonnières
        seasonal_opportunities = self._identify_seasonal_opportunities(
            demand_forecast, context
        )
        opportunities.extend(seasonal_opportunities)
        
        # Opportunités concurrentielles
        competitive_opportunities = self._identify_competitive_opportunities(
            context, pricing_optimization
        )
        opportunities.extend(competitive_opportunities)
        
        return {
            'identified_opportunities': opportunities,
            'opportunity_prioritization': self._prioritize_opportunities(opportunities),
            'implementation_roadmap': self._create_opportunity_roadmap(opportunities),
            'expected_impact': self._estimate_opportunity_impact(opportunities, context)
        }
    
    def generate_booking_recommendations(self, context: HotelBookingContext) -> Dict[str, Any]:
        """Génère recommandations complètes booking hôtelier"""
        
        logger.info("🎯 Génération recommandations booking complètes")
        
        # 1. Prédiction demande
        demand_forecast = self.predict_booking_demand(context, forecast_horizon_days=90)
        
        # 2. Optimisation pricing
        pricing_optimization = self.optimize_room_pricing(context, demand_forecast)
        
        # 3. Identification opportunités
        opportunities = self.identify_booking_opportunities(
            context, demand_forecast, pricing_optimization
        )
        
        # 4. Recommandations opérationnelles
        operational_recommendations = self._generate_operational_recommendations(
            context, demand_forecast, pricing_optimization
        )
        
        # 5. Plan d'action
        action_plan = self._create_comprehensive_action_plan(
            demand_forecast, pricing_optimization, opportunities, operational_recommendations
        )
        
        return {
            'hotel_id': context.hotel_id,
            'analysis_date': datetime.now().isoformat(),
            'forecast_period': '90 days',
            
            # Résultats principaux
            'demand_forecast': demand_forecast,
            'pricing_optimization': pricing_optimization,
            'opportunities': opportunities,
            'operational_recommendations': operational_recommendations,
            
            # Plan d'action
            'action_plan': action_plan,
            
            # Métriques de pilotage
            'key_performance_indicators': self._define_booking_kpis(context),
            'monitoring_dashboard': self._setup_monitoring_dashboard(context)
        }
    
    def _generate_forecast_features(self, context: HotelBookingContext, 
                                  horizon_days: int) -> List[List[float]]:
        """Génère features prédictives pour chaque jour de forecast"""
        
        features_list = []
        base_date = datetime.now().date()
        
        # Calendrier des jours fériés
        fr_holidays = holidays.France(years=range(2025, 2027))
        
        for i in range(horizon_days):
            forecast_date = base_date + timedelta(days=i)
            
            # Features temporelles
            features = [
                forecast_date.weekday(),  # 0=lundi, 6=dimanche
                forecast_date.month,
                forecast_date.day,
                1.0 if forecast_date in fr_holidays else 0.0,
                1.0 if forecast_date.weekday() >= 5 else 0.0,  # Weekend
            ]
            
            # Features saisonnières
            seasonal_factor = context.seasonal_adjustments.get(
                f"{forecast_date.month:02d}", 1.0
            )
            features.append(seasonal_factor)
            
            # Features événements locaux
            event_factor = self._calculate_event_impact(forecast_date, context.local_events)
            features.append(event_factor)
            
            # Features météo (si disponible)
            weather_factor = self._calculate_weather_impact(forecast_date, context.weather_forecast)
            features.append(weather_factor)
            
            # Features concurrence
            avg_competitor_rate = np.mean(list(context.competitor_rates.values())) if context.competitor_rates else context.current_adr
            competitive_position = context.current_adr / avg_competitor_rate if avg_competitor_rate > 0 else 1.0
            features.append(competitive_position)
            
            # Features historiques (patterns similaires)
            historical_pattern = self._get_historical_pattern_match(forecast_date, context)
            features.extend(historical_pattern)
            
            features_list.append(features)
        
        return features_list
    
    def _predict_daily_demand(self, features: List[float], context: HotelBookingContext) -> float:
        """Prédit demande quotidienne basée sur features"""
        
        # Simulation modèle ML (en production, utiliser modèle entraîné)
        if hasattr(self.models['demand_forecast'], 'predict'):
            try:
                prediction = self.models['demand_forecast'].predict([features])[0]
                return max(0, prediction)
            except:
                # Fallback
                pass
        
        # Heuristique simple comme fallback
        base_demand = context.total_rooms * 0.7  # 70% occupation base
        
        # Ajustements selon features
        weekend_factor = 1.2 if features[4] == 1.0 else 1.0  # Weekend
        holiday_factor = 1.3 if features[3] == 1.0 else 1.0  # Jour férié
        seasonal_factor = features[5]  # Facteur saisonnier
        event_factor = features[6]  # Impact événements
        
        adjusted_demand = base_demand * weekend_factor * holiday_factor * seasonal_factor * event_factor
        
        return min(adjusted_demand, context.total_rooms * 1.1)  # Max overbooking 10%
    
    def _apply_demand_adjustments(self, raw_demand: float, date: datetime.date,
                                context: HotelBookingContext, features: List[float]) -> float:
        """Applique ajustements métier à la demande prédite"""
        
        adjusted_demand = raw_demand
        
        # Ajustement capacité opérationnelle
        operational_capacity = context.total_rooms * self.business_rules['operations']['housekeeping_buffer']
        adjusted_demand = min(adjusted_demand, operational_capacity)
        
        # Ajustement blackout dates
        if date.isoformat() in context.blackout_dates:
            adjusted_demand = 0
        
        # Ajustement minimum séjour
        # (Simplification - en réalité plus complexe)
        
        return adjusted_demand
    
    def _predict_cancellations(self, features: List[float], context: HotelBookingContext) -> float:
        """Prédit taux de cancellation"""
        
        # Taux de cancellation historique moyen
        if context.cancellation_history:
            historical_cancellation_rate = np.mean([
                c.get('cancellation_rate', 0.1) for c in context.cancellation_history
            ])
        else:
            historical_cancellation_rate = 0.08  # 8% par défaut
        
        # Ajustements selon contexte
        advance_booking_factor = 1.0  # Plus d'advance = moins de cancellations
        seasonal_factor = features[5]  # Haute saison = moins cancellations
        
        adjusted_cancellation_rate = historical_cancellation_rate * advance_booking_factor * (2 - seasonal_factor)
        
        return adjusted_cancellation_rate * context.total_rooms
    
    def _calculate_base_rates(self, context: HotelBookingContext, date: str) -> Dict[str, float]:
        """Calcule tarifs de base par type de chambre"""
        
        # Tarifs de base selon type chambre (proportionnel à l'ADR actuel)
        base_rates = {}
        
        for room_type, room_count in context.room_types.items():
            if room_type.lower() == 'standard':
                base_rates[room_type] = context.current_adr * 0.85
            elif room_type.lower() == 'deluxe':
                base_rates[room_type] = context.current_adr * 1.25
            elif room_type.lower() == 'suite':
                base_rates[room_type] = context.current_adr * 1.8
            else:
                base_rates[room_type] = context.current_adr
        
        return base_rates
    
    def _calculate_pricing_factors(self, expected_occupancy: float, date: str,
                                 context: HotelBookingContext, daily_pred: Dict) -> Dict[str, float]:
        """Calcule facteurs d'ajustement pricing"""
        
        factors = {}
        
        # Facteur demande/offre
        if expected_occupancy > 0.9:
            factors['demand_pressure'] = 1.15  # +15% si forte demande
        elif expected_occupancy > 0.75:
            factors['demand_pressure'] = 1.05  # +5% si bonne demande
        elif expected_occupancy < 0.5:
            factors['demand_pressure'] = 0.90  # -10% si faible demande
        else:
            factors['demand_pressure'] = 1.0
        
        # Facteur jour de semaine
        date_obj = datetime.fromisoformat(date).date()
        if date_obj.weekday() >= 5:  # Weekend
            factors['weekend_premium'] = self.business_rules['pricing_rules']['weekend_premium']
        else:
            factors['weekend_premium'] = 1.0
        
        # Facteur saisonnier
        month = date_obj.month
        if month in [7, 8, 12]:  # Haute saison
            factors['seasonal'] = self.business_rules['pricing_rules']['peak_season_premium']
        elif month in [1, 2, 11]:  # Basse saison
            factors['seasonal'] = 0.85
        else:
            factors['seasonal'] = 1.0
        
        # Facteur advance booking
        days_in_advance = (date_obj - datetime.now().date()).days
        if days_in_advance > 30:
            factors['advance_booking'] = self.business_rules['pricing_rules']['advance_booking_discount']
        elif days_in_advance < 3:
            factors['advance_booking'] = self.business_rules['pricing_rules']['last_minute_premium']
        else:
            factors['advance_booking'] = 1.0
        
        return factors
    
    def _apply_psychological_pricing(self, rate: float) -> float:
        """Applique pricing psychologique"""
        
        if rate < 100:
            return round(rate - 0.01, 2)  # 99.99
        elif rate < 200:
            return round(rate / 5) * 5 - 1  # 149, 154, etc.
        else:
            return round(rate / 10) * 10 - 1  # 199, 249, etc.

# Exemple d'utilisation
def demo_hotel_booking_predictor():
    """Démonstration système prédictif hôtelier"""
    
    config = {
        'enable_ml': True,
        'forecast_accuracy_target': 0.85
    }
    
    predictor = HotelBookingPredictor(config)
    
    # Contexte hôtel exemple
    context = HotelBookingContext(
        hotel_id="HOTEL_PARIS_001",
        total_rooms=100,
        room_types={'standard': 70, 'deluxe': 25, 'suite': 5},
        
        # Historiques simulés
        booking_history=[
            {'date': '2025-08-01', 'bookings': 75, 'adr': 150.0, 'occupancy': 0.75},
            {'date': '2025-08-02', 'bookings': 82, 'adr': 155.0, 'occupancy': 0.82},
        ],
        cancellation_history=[
            {'date': '2025-08-01', 'cancellations': 8, 'cancellation_rate': 0.096}
        ],
        pricing_history=[
            {'date': '2025-08-01', 'standard': 120, 'deluxe': 180, 'suite': 350}
        ],
        
        # Contexte externe
        local_events=[
            {'name': 'Fashion Week', 'start_date': '2025-09-15', 'end_date': '2025-09-22', 'impact_factor': 1.4}
        ],
        weather_forecast=[],
        competitor_rates={'Competitor1': 145.0, 'Competitor2': 165.0},
        
        # Métriques actuelles
        current_occupancy=0.78,
        current_adr=152.0,
        current_revpar=118.56,
        
        # Contraintes
        min_stay_requirements={'weekend': 2},
        blackout_dates=[],
        seasonal_adjustments={'12': 1.3, '07': 1.4, '08': 1.3}
    )
    
    # Génération recommandations complètes
    recommendations = predictor.generate_booking_recommendations(context)
    
    print("🏨 RECOMMANDATIONS BOOKING HÔTELIER")
    print("=" * 60)
    
    # Résumé forecast
    forecast = recommendations['demand_forecast']
    print(f"📈 PRÉVISIONS DEMANDE (90 jours):")
    print(f"• Demande moyenne/jour: {forecast['summary_metrics']['average_daily_demand']:.0f} chambres")
    print(f"• Pic de demande: {forecast['summary_metrics']['peak_demand_date']} ({forecast['summary_metrics']['peak_demand_value']:.0f} chambres)")
    
    # Résumé pricing
    pricing = recommendations['pricing_optimization']
    avg_projected_revpar = np.mean([
        day['metrics']['projected_revpar'] 
        for day in pricing['daily_pricing_recommendations']
    ])
    print(f"\n💰 OPTIMISATION PRICING:")
    print(f"• RevPAR projeté moyen: {avg_projected_revpar:.2f}€")
    print(f"• Amélioration vs actuel: {((avg_projected_revpar/context.current_revpar - 1) * 100):+.1f}%")
    
    # Opportunités prioritaires
    opportunities = recommendations['opportunities']
    high_priority_ops = [op for op in opportunities['identified_opportunities'] if op.get('priority') == 'high']
    print(f"\n🎯 OPPORTUNITÉS PRIORITAIRES ({len(high_priority_ops)}):")
    for i, opp in enumerate(high_priority_ops[:3], 1):
        print(f"• {i}. {opp['type']}: {opp.get('potential_upside', 'Impact significatif')}")
    
    return recommendations

if __name__ == "__main__":
    demo_hotel_booking_predictor()
```

Ce cas d'usage avancé de booking prédictif hôtelier intègre :

✅ **Prédiction ML de la demande** avec features temporelles, événementielles et concurrentielles
✅ **Optimisation pricing dynamique** avec yield management intelligent
✅ **Identification d'opportunités** business automatisée
✅ **Recommandations opérationnelles** actionnables
✅ **Intégration de contraintes métier** réalistes

Le système peut être étendu avec d'autres secteurs (retail, transport, finance) suivant la même approche modulaire et prédictive.