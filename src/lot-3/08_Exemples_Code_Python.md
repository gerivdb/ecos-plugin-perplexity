# Exemples de Code Python - Espace Métier Perplexity AI

## Vue d'ensemble
Ce document propose une bibliothèque complète de scripts Python réutilisables avec commentaires détaillés et cas d'usage métier pour l'espace Perplexity AI.

## Scripts de Base Métier

### Collecte et Traitement de Données

#### Script 1 : Collecteur de Données Multi-Sources
```python
#!/usr/bin/env python3
"""
Collecteur de données intelligent multi-sources
Cas d'usage : Agrégation données concurrentielles, market data, social media
Auteur : Équipe Perplexity AI
Tags : data-collection, apis, scraping
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiSourceDataCollector:
    """Collecteur de données depuis sources multiples avec gestion d'erreurs robuste"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'PerplexityAI/1.0')
        })
        
        # Rate limiting global
        self.requests_per_minute = config.get('requests_per_minute', 60)
        self.request_times = []
        
        # Résultats collectés
        self.collected_data = {}
        
    def _enforce_rate_limit(self):
        """Applique limitation taux de requêtes"""
        now = time.time()
        
        # Nettoie les requêtes anciennes (> 1 minute)
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Vérifie si on peut faire une nouvelle requête
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit atteint, pause {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def collect_from_api(self, source_name: str, endpoint: str, 
                        params: Dict[str, Any] = None,
                        headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """
        Collecte données depuis une API REST
        
        Args:
            source_name: Nom de la source pour tracking
            endpoint: URL de l'API
            params: Paramètres GET
            headers: Headers supplémentaires
            
        Returns:
            Données JSON ou None si erreur
        """
        self._enforce_rate_limit()
        
        try:
            logger.info(f"Collecte API {source_name}: {endpoint}")
            
            # Merge headers
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = self.session.get(
                endpoint, 
                params=params, 
                headers=request_headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Enrichissement métadonnées
            enriched_data = {
                'source': source_name,
                'collected_at': datetime.now().isoformat(),
                'endpoint': endpoint,
                'data': data
            }
            
            logger.info(f"✅ Succès collecte {source_name}")
            return enriched_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur API {source_name}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur JSON {source_name}: {e}")
            return None
    
    def collect_from_multiple_apis(self, sources: List[Dict[str, Any]], 
                                  max_workers: int = 3) -> Dict[str, Any]:
        """
        Collecte parallèle depuis plusieurs APIs
        
        Args:
            sources: Liste des configurations API
            max_workers: Nombre de threads parallèles
            
        Returns:
            Dictionnaire des résultats par source
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumission des tâches
            future_to_source = {}
            
            for source_config in sources:
                future = executor.submit(
                    self.collect_from_api,
                    source_config['name'],
                    source_config['endpoint'],
                    source_config.get('params', {}),
                    source_config.get('headers', {})
                )
                future_to_source[future] = source_config['name']
            
            # Récupération des résultats
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    result = future.result()
                    if result:
                        results[source_name] = result
                except Exception as e:
                    logger.error(f"Erreur thread {source_name}: {e}")
        
        return results
    
    def save_collected_data(self, data: Dict[str, Any], 
                           output_format: str = 'json') -> str:
        """
        Sauvegarde données collectées
        
        Args:
            data: Données à sauvegarder
            output_format: Format (json, csv, excel)
            
        Returns:
            Nom du fichier créé
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == 'json':
            filename = f"collected_data_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
        elif output_format == 'csv':
            filename = f"collected_data_{timestamp}.csv"
            # Aplatit les données pour CSV
            flattened_data = self._flatten_for_csv(data)
            df = pd.DataFrame(flattened_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            
        elif output_format == 'excel':
            filename = f"collected_data_{timestamp}.xlsx"
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for source, source_data in data.items():
                    if isinstance(source_data.get('data'), list):
                        df = pd.DataFrame(source_data['data'])
                        sheet_name = source[:31]  # Limite Excel
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"📁 Données sauvegardées: {filename}")
        return filename
    
    def _flatten_for_csv(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplatit données structurées pour export CSV"""
        flattened = []
        
        for source, source_data in data.items():
            base_record = {
                'source': source,
                'collected_at': source_data.get('collected_at')
            }
            
            if isinstance(source_data.get('data'), list):
                for item in source_data['data']:
                    record = base_record.copy()
                    if isinstance(item, dict):
                        record.update(item)
                    else:
                        record['value'] = item
                    flattened.append(record)
            else:
                record = base_record.copy()
                record['data'] = str(source_data.get('data'))
                flattened.append(record)
        
        return flattened

# Exemple d'utilisation
def exemple_collecte_pricing():
    """Exemple : Collecte prix concurrents e-commerce"""
    
    config = {
        'requests_per_minute': 30,
        'user_agent': 'PriceBot/1.0'
    }
    
    collector = MultiSourceDataCollector(config)
    
    # Configuration sources prix
    pricing_sources = [
        {
            'name': 'api_concurrent_a',
            'endpoint': 'https://api.concurrent-a.com/v1/prices',
            'params': {'category': 'electronics', 'limit': 100},
            'headers': {'Authorization': 'Bearer YOUR_TOKEN'}
        },
        {
            'name': 'api_concurrent_b', 
            'endpoint': 'https://api.concurrent-b.com/products/prices',
            'params': {'active': True}
        }
    ]
    
    # Collecte parallèle
    logger.info("🚀 Début collecte pricing concurrentiel")
    results = collector.collect_from_multiple_apis(pricing_sources)
    
    # Analyse rapide
    total_products = sum(
        len(source_data.get('data', [])) 
        for source_data in results.values()
        if isinstance(source_data.get('data'), list)
    )
    
    logger.info(f"📊 Total produits collectés: {total_products}")
    
    # Sauvegarde multi-format
    json_file = collector.save_collected_data(results, 'json')
    csv_file = collector.save_collected_data(results, 'csv')
    excel_file = collector.save_collected_data(results, 'excel')
    
    return {
        'results': results,
        'files': [json_file, csv_file, excel_file],
        'summary': {
            'sources_successful': len(results),
            'total_products': total_products,
            'collection_time': datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    # Exécution exemple
    summary = exemple_collecte_pricing()
    print(f"Collecte terminée: {summary['summary']}")
```

#### Script 2 : Analyseur de Performance Marketing
```python
#!/usr/bin/env python3
"""
Analyseur de performance marketing multi-canal
Cas d'usage : ROI campagnes, attribution, optimisation budget
Auteur : Équipe Perplexity AI  
Tags : marketing, analytics, roi, attribution
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class MarketingPerformanceAnalyzer:
    """Analyseur avancé performance marketing"""
    
    def __init__(self):
        self.campaigns_data = pd.DataFrame()
        self.conversion_data = pd.DataFrame()
        self.cost_data = pd.DataFrame()
        
    def load_campaign_data(self, campaigns: List[Dict]) -> None:
        """Charge données campagnes marketing"""
        self.campaigns_data = pd.DataFrame(campaigns)
        if not self.campaigns_data.empty:
            self.campaigns_data['date'] = pd.to_datetime(self.campaigns_data['date'])
            
    def load_conversion_data(self, conversions: List[Dict]) -> None:
        """Charge données de conversion"""
        self.conversion_data = pd.DataFrame(conversions)
        if not self.conversion_data.empty:
            self.conversion_data['conversion_date'] = pd.to_datetime(
                self.conversion_data['conversion_date']
            )
    
    def calculate_channel_roi(self) -> pd.DataFrame:
        """
        Calcule ROI par canal marketing
        
        Returns:
            DataFrame avec métriques ROI par canal
        """
        if self.campaigns_data.empty:
            return pd.DataFrame()
        
        # Agrégation par canal
        channel_metrics = self.campaigns_data.groupby('channel').agg({
            'spend': 'sum',
            'impressions': 'sum', 
            'clicks': 'sum',
            'conversions': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calcul métriques dérivées
        channel_metrics['ctr'] = (channel_metrics['clicks'] / 
                                 channel_metrics['impressions'] * 100).round(2)
        
        channel_metrics['conversion_rate'] = (channel_metrics['conversions'] / 
                                            channel_metrics['clicks'] * 100).round(2)
        
        channel_metrics['cpa'] = (channel_metrics['spend'] / 
                                 channel_metrics['conversions']).round(2)
        
        channel_metrics['roi'] = ((channel_metrics['revenue'] - channel_metrics['spend']) / 
                                 channel_metrics['spend'] * 100).round(2)
        
        channel_metrics['roas'] = (channel_metrics['revenue'] / 
                                  channel_metrics['spend']).round(2)
        
        # Classement par performance
        channel_metrics['roi_rank'] = channel_metrics['roi'].rank(ascending=False)
        channel_metrics['roas_rank'] = channel_metrics['roas'].rank(ascending=False)
        
        return channel_metrics.sort_values('roi', ascending=False)
    
    def analyze_attribution_model(self, attribution_window_days: int = 30) -> Dict[str, Any]:
        """
        Analyse attribution multi-touch avec fenêtre temporelle
        
        Args:
            attribution_window_days: Fenêtre d'attribution en jours
            
        Returns:
            Résultats analyse d'attribution
        """
        if self.conversion_data.empty or self.campaigns_data.empty:
            return {}
        
        attribution_results = {}
        
        for _, conversion in self.conversion_data.iterrows():
            conversion_date = conversion['conversion_date']
            window_start = conversion_date - timedelta(days=attribution_window_days)
            
            # Touchpoints dans la fenêtre d'attribution
            touchpoints = self.campaigns_data[
                (self.campaigns_data['user_id'] == conversion['user_id']) &
                (self.campaigns_data['date'] >= window_start) &
                (self.campaigns_data['date'] <= conversion_date)
            ].sort_values('date')
            
            if len(touchpoints) == 0:
                continue
            
            conversion_value = conversion['conversion_value']
            
            # Modèles d'attribution
            models = {
                'first_touch': self._first_touch_attribution(touchpoints, conversion_value),
                'last_touch': self._last_touch_attribution(touchpoints, conversion_value), 
                'linear': self._linear_attribution(touchpoints, conversion_value),
                'time_decay': self._time_decay_attribution(touchpoints, conversion_value, conversion_date),
                'position_based': self._position_based_attribution(touchpoints, conversion_value)
            }
            
            # Accumulation par canal pour chaque modèle
            for model_name, attributions in models.items():
                if model_name not in attribution_results:
                    attribution_results[model_name] = {}
                
                for channel, value in attributions.items():
                    if channel not in attribution_results[model_name]:
                        attribution_results[model_name][channel] = 0
                    attribution_results[model_name][channel] += value
        
        return attribution_results
    
    def _first_touch_attribution(self, touchpoints: pd.DataFrame, 
                                conversion_value: float) -> Dict[str, float]:
        """Attribution 100% au premier touchpoint"""
        if len(touchpoints) == 0:
            return {}
        
        first_channel = touchpoints.iloc[0]['channel']
        return {first_channel: conversion_value}
    
    def _last_touch_attribution(self, touchpoints: pd.DataFrame,
                               conversion_value: float) -> Dict[str, float]:
        """Attribution 100% au dernier touchpoint"""
        if len(touchpoints) == 0:
            return {}
        
        last_channel = touchpoints.iloc[-1]['channel']
        return {last_channel: conversion_value}
    
    def _linear_attribution(self, touchpoints: pd.DataFrame,
                           conversion_value: float) -> Dict[str, float]:
        """Attribution linéaire égale entre tous touchpoints"""
        if len(touchpoints) == 0:
            return {}
        
        attribution_per_touch = conversion_value / len(touchpoints)
        attributions = {}
        
        for _, touchpoint in touchpoints.iterrows():
            channel = touchpoint['channel']
            attributions[channel] = attributions.get(channel, 0) + attribution_per_touch
        
        return attributions
    
    def _time_decay_attribution(self, touchpoints: pd.DataFrame,
                               conversion_value: float,
                               conversion_date: datetime,
                               decay_rate: float = 0.1) -> Dict[str, float]:
        """Attribution avec décroissance temporelle (plus récent = plus de poids)"""
        if len(touchpoints) == 0:
            return {}
        
        # Calcul des poids avec décroissance exponentielle
        weights = []
        for _, touchpoint in touchpoints.iterrows():
            days_before = (conversion_date - touchpoint['date']).days
            weight = np.exp(-decay_rate * days_before)
            weights.append(weight)
        
        total_weight = sum(weights)
        attributions = {}
        
        for i, (_, touchpoint) in enumerate(touchpoints.iterrows()):
            channel = touchpoint['channel']
            attribution_value = (weights[i] / total_weight) * conversion_value
            attributions[channel] = attributions.get(channel, 0) + attribution_value
        
        return attributions
    
    def _position_based_attribution(self, touchpoints: pd.DataFrame,
                                   conversion_value: float,
                                   first_weight: float = 0.4,
                                   last_weight: float = 0.4) -> Dict[str, float]:
        """Attribution basée position (40% premier, 40% dernier, 20% milieu)"""
        if len(touchpoints) == 0:
            return {}
        
        attributions = {}
        n_touches = len(touchpoints)
        
        if n_touches == 1:
            # Un seul touchpoint = 100%
            channel = touchpoints.iloc[0]['channel']
            attributions[channel] = conversion_value
            
        elif n_touches == 2:
            # Deux touchpoints = 50/50
            for _, touchpoint in touchpoints.iterrows():
                channel = touchpoint['channel']
                attributions[channel] = attributions.get(channel, 0) + conversion_value * 0.5
                
        else:
            # Premier touchpoint
            first_channel = touchpoints.iloc[0]['channel']
            attributions[first_channel] = attributions.get(first_channel, 0) + conversion_value * first_weight
            
            # Dernier touchpoint  
            last_channel = touchpoints.iloc[-1]['channel']
            attributions[last_channel] = attributions.get(last_channel, 0) + conversion_value * last_weight
            
            # Touchpoints intermédiaires
            middle_weight = 1.0 - first_weight - last_weight
            middle_attribution = middle_weight / (n_touches - 2)
            
            for i in range(1, n_touches - 1):
                channel = touchpoints.iloc[i]['channel']
                attributions[channel] = attributions.get(channel, 0) + conversion_value * middle_attribution
        
        return attributions
    
    def optimize_budget_allocation(self, total_budget: float,
                                 target_metric: str = 'roi') -> Dict[str, Any]:
        """
        Optimise allocation budget selon métrique cible
        
        Args:
            total_budget: Budget total à répartir
            target_metric: Métrique à optimiser (roi, roas, conversions)
            
        Returns:
            Recommandations allocation budget
        """
        channel_performance = self.calculate_channel_roi()
        
        if channel_performance.empty:
            return {'error': 'Pas de données performance disponibles'}
        
        # Tri par métrique cible
        if target_metric in channel_performance.columns:
            channel_performance = channel_performance.sort_values(
                target_metric, ascending=False
            )
        
        # Allocation proportionnelle aux performances
        if target_metric == 'roi':
            # Plus de budget aux canaux avec meilleur ROI
            weights = channel_performance['roi'].apply(lambda x: max(0, x))
        elif target_metric == 'roas':
            # Plus de budget aux canaux avec meilleur ROAS
            weights = channel_performance['roas']
        elif target_metric == 'conversions':
            # Plus de budget aux canaux avec plus de conversions
            weights = channel_performance['conversions']
        else:
            # Répartition égale par défaut
            weights = pd.Series([1] * len(channel_performance))
        
        # Normalisation et allocation
        total_weight = weights.sum()
        budget_allocations = {}
        
        for i, (_, row) in enumerate(channel_performance.iterrows()):
            channel = row['channel']
            if total_weight > 0:
                allocated_budget = (weights.iloc[i] / total_weight) * total_budget
            else:
                allocated_budget = total_budget / len(channel_performance)
            
            budget_allocations[channel] = {
                'allocated_budget': round(allocated_budget, 2),
                'current_spend': row['spend'],
                'budget_change': round(allocated_budget - row['spend'], 2),
                'performance_metric': row[target_metric] if target_metric in row else 0
            }
        
        return {
            'total_budget': total_budget,
            'optimization_metric': target_metric,
            'allocations': budget_allocations,
            'expected_improvement': self._estimate_performance_improvement(
                channel_performance, budget_allocations, target_metric
            )
        }
    
    def _estimate_performance_improvement(self, current_performance: pd.DataFrame,
                                        new_allocations: Dict[str, Dict],
                                        target_metric: str) -> Dict[str, float]:
        """Estime amélioration performance avec nouvelle allocation"""
        current_total = current_performance[target_metric].sum() if target_metric in current_performance.columns else 0
        
        # Estimation simplifiée basée sur élasticité budget
        estimated_improvement = {}
        
        for channel in new_allocations:
            current_channel = current_performance[current_performance['channel'] == channel]
            if not current_channel.empty:
                current_spend = current_channel.iloc[0]['spend']
                new_spend = new_allocations[channel]['allocated_budget']
                
                if current_spend > 0:
                    spend_change_ratio = new_spend / current_spend
                    # Assumption : élasticité de 0.7 (rendements décroissants)
                    performance_multiplier = spend_change_ratio ** 0.7
                    estimated_improvement[channel] = performance_multiplier
        
        return estimated_improvement
    
    def generate_performance_report(self) -> str:
        """Génère rapport complet performance marketing"""
        
        report_sections = []
        
        # Section ROI par canal
        channel_roi = self.calculate_channel_roi()
        if not channel_roi.empty:
            report_sections.append("# 📊 Performance par Canal Marketing\n")
            report_sections.append(channel_roi.to_string(index=False))
            report_sections.append("\n\n")
        
        # Section attribution
        attribution = self.analyze_attribution_model()
        if attribution:
            report_sections.append("# 🔗 Analyse d'Attribution\n")
            for model, results in attribution.items():
                report_sections.append(f"## {model.title().replace('_', ' ')}\n")
                for channel, value in sorted(results.items(), key=lambda x: x[1], reverse=True):
                    report_sections.append(f"- {channel}: {value:.2f}€\n")
                report_sections.append("\n")
        
        # Section optimisation budget
        optimization = self.optimize_budget_allocation(10000, 'roi')  # Exemple 10k€
        if 'allocations' in optimization:
            report_sections.append("# 💰 Optimisation Budget (10,000€)\n")
            for channel, details in optimization['allocations'].items():
                report_sections.append(
                    f"- {channel}: {details['allocated_budget']:.2f}€ "
                    f"({details['budget_change']:+.2f}€ vs actuel)\n"
                )
        
        return "".join(report_sections)

# Exemple d'utilisation
def exemple_analyse_marketing():
    """Exemple complet analyse performance marketing"""
    
    # Données exemple campagnes
    campaigns_data = [
        {'date': '2025-09-01', 'channel': 'google_ads', 'user_id': 'user1', 'spend': 100, 'impressions': 1000, 'clicks': 50, 'conversions': 5, 'revenue': 500},
        {'date': '2025-09-02', 'channel': 'facebook_ads', 'user_id': 'user1', 'spend': 80, 'impressions': 800, 'clicks': 40, 'conversions': 3, 'revenue': 300},
        {'date': '2025-09-01', 'channel': 'google_ads', 'user_id': 'user2', 'spend': 120, 'impressions': 1200, 'clicks': 60, 'conversions': 6, 'revenue': 720},
        # ... plus de données
    ]
    
    conversions_data = [
        {'user_id': 'user1', 'conversion_date': '2025-09-03', 'conversion_value': 150},
        {'user_id': 'user2', 'conversion_date': '2025-09-02', 'conversion_value': 200},
        # ... plus de conversions
    ]
    
    # Initialisation analyseur
    analyzer = MarketingPerformanceAnalyzer()
    analyzer.load_campaign_data(campaigns_data)
    analyzer.load_conversion_data(conversions_data)
    
    # Analyses
    channel_performance = analyzer.calculate_channel_roi()
    attribution_analysis = analyzer.analyze_attribution_model()
    budget_optimization = analyzer.optimize_budget_allocation(5000, 'roi')
    
    # Rapport
    report = analyzer.generate_performance_report()
    
    # Sauvegarde résultats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export Excel avec onglets multiples
    with pd.ExcelWriter(f'marketing_analysis_{timestamp}.xlsx') as writer:
        channel_performance.to_excel(writer, sheet_name='Channel_Performance', index=False)
        
        # Attribution dans onglets séparés
        for model, results in attribution_analysis.items():
            df_attribution = pd.DataFrame(list(results.items()), columns=['Channel', 'Attributed_Value'])
            df_attribution.to_excel(writer, sheet_name=f'Attribution_{model}', index=False)
    
    # Rapport markdown
    with open(f'marketing_report_{timestamp}.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Analyse terminée - Fichiers générés avec timestamp {timestamp}")
    
    return {
        'channel_performance': channel_performance,
        'attribution': attribution_analysis,
        'budget_optimization': budget_optimization
    }

if __name__ == "__main__":
    results = exemple_analyse_marketing()
    print("Performance Analysis Complete!")
```

### Scripts d'Automatisation Workflow

#### Script 3 : Automatiseur de Processus Métier
```python
#!/usr/bin/env python3
"""
Automatiseur de processus métier avec workflows intelligents
Cas d'usage : Automatisation tâches récurrentes, validation de données, notifications
Auteur : Équipe Perplexity AI
Tags : automation, workflow, business-process
"""

import schedule
import time
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
import pandas as pd
import json
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import requests

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Statuts possibles pour les tâches"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class BusinessRule:
    """Définition d'une règle métier"""
    rule_id: str
    name: str
    description: str
    condition_function: Callable[[Any], bool]
    action_function: Callable[[Any], Any]
    priority: int = 1
    enabled: bool = True

class BusinessProcessAutomator:
    """Automatiseur de processus métier avec gestion de règles"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.business_rules: List[BusinessRule] = []
        self.scheduled_tasks = {}
        self.task_history = []
        self.notification_channels = self._setup_notification_channels()
        
    def _setup_notification_channels(self) -> Dict[str, Any]:
        """Configure les canaux de notification"""
        channels = {}
        
        # Email
        if 'smtp' in self.config:
            channels['email'] = {
                'server': self.config['smtp']['server'],
                'port': self.config['smtp']['port'],
                'username': self.config['smtp']['username'],
                'password': self.config['smtp']['password']
            }
        
        # Slack
        if 'slack' in self.config:
            channels['slack'] = {
                'webhook_url': self.config['slack']['webhook_url'],
                'channel': self.config['slack']['channel']
            }
        
        # Teams
        if 'teams' in self.config:
            channels['teams'] = {
                'webhook_url': self.config['teams']['webhook_url']
            }
        
        return channels
    
    def add_business_rule(self, rule: BusinessRule) -> None:
        """Ajoute une règle métier"""
        self.business_rules.append(rule)
        logger.info(f"Règle ajoutée: {rule.name}")
    
    def execute_business_rules(self, data: Any, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Exécute toutes les règles métier sur les données
        
        Args:
            data: Données à évaluer
            context: Contexte d'exécution
            
        Returns:
            Résultats d'exécution des règles
        """
        context = context or {}
        results = []
        
        # Tri par priorité
        sorted_rules = sorted(self.business_rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
                
            rule_result = {
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'executed_at': datetime.now().isoformat(),
                'status': TaskStatus.PENDING.value
            }
            
            try:
                logger.info(f"Évaluation règle: {rule.name}")
                rule_result['status'] = TaskStatus.RUNNING.value
                
                # Évaluation condition
                if rule.condition_function(data):
                    logger.info(f"Condition vraie pour règle: {rule.name}")
                    
                    # Exécution action
                    action_result = rule.action_function(data)
                    
                    rule_result.update({
                        'status': TaskStatus.COMPLETED.value,
                        'condition_met': True,
                        'action_executed': True,
                        'action_result': action_result
                    })
                    
                    logger.info(f"✅ Règle exécutée avec succès: {rule.name}")
                    
                else:
                    rule_result.update({
                        'status': TaskStatus.SKIPPED.value,
                        'condition_met': False,
                        'action_executed': False
                    })
                    
                    logger.info(f"⏭️  Règle ignorée (condition fausse): {rule.name}")
                
            except Exception as e:
                rule_result.update({
                    'status': TaskStatus.FAILED.value,
                    'error': str(e)
                })
                logger.error(f"❌ Erreur règle {rule.name}: {e}")
                
                # Notification d'erreur
                self._send_error_notification(rule, e, data)
            
            results.append(rule_result)
        
        return results
    
    def schedule_recurring_task(self, task_name: str, task_function: Callable,
                               schedule_pattern: str, **kwargs) -> None:
        """
        Programme une tâche récurrente
        
        Args:
            task_name: Nom de la tâche
            task_function: Fonction à exécuter
            schedule_pattern: Pattern de programmation (daily, hourly, etc.)
            **kwargs: Arguments pour la fonction
        """
        
        def wrapped_task():
            """Wrapper avec gestion d'erreurs et logging"""
            start_time = datetime.now()
            task_record = {
                'task_name': task_name,
                'start_time': start_time.isoformat(),
                'status': TaskStatus.RUNNING.value
            }
            
            try:
                logger.info(f"🚀 Début tâche programmée: {task_name}")
                result = task_function(**kwargs)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                task_record.update({
                    'status': TaskStatus.COMPLETED.value,
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration,
                    'result': result
                })
                
                logger.info(f"✅ Tâche terminée: {task_name} ({duration:.2f}s)")
                
            except Exception as e:
                task_record.update({
                    'status': TaskStatus.FAILED.value,
                    'error': str(e),
                    'end_time': datetime.now().isoformat()
                })
                
                logger.error(f"❌ Erreur tâche {task_name}: {e}")
                self._send_error_notification_task(task_name, e)
            
            self.task_history.append(task_record)
        
        # Configuration programmation selon pattern
        if schedule_pattern == 'daily':
            schedule.every().day.at("09:00").do(wrapped_task)
        elif schedule_pattern == 'hourly':
            schedule.every().hour.do(wrapped_task)
        elif schedule_pattern.startswith('every_'):
            # Format: every_10_minutes, every_2_hours, etc.
            parts = schedule_pattern.split('_')
            if len(parts) == 3:
                interval = int(parts[1])
                unit = parts[2]
                
                if unit == 'minutes':
                    schedule.every(interval).minutes.do(wrapped_task)
                elif unit == 'hours':
                    schedule.every(interval).hours.do(wrapped_task)
                elif unit == 'days':
                    schedule.every(interval).days.do(wrapped_task)
        
        self.scheduled_tasks[task_name] = {
            'function': task_function,
            'pattern': schedule_pattern,
            'kwargs': kwargs,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"📅 Tâche programmée: {task_name} ({schedule_pattern})")
    
    def run_scheduler(self, run_pending_only: bool = False) -> None:
        """
        Démarre le scheduler de tâches
        
        Args:
            run_pending_only: Si True, exécute seulement les tâches en attente
        """
        if run_pending_only:
            schedule.run_pending()
        else:
            logger.info("🔄 Démarrage scheduler (Ctrl+C pour arrêter)")
            while True:
                schedule.run_pending()
                time.sleep(1)
    
    def _send_error_notification(self, rule: BusinessRule, error: Exception, data: Any) -> None:
        """Envoie notification en cas d'erreur de règle"""
        message = f"""
        Erreur règle métier détectée:
        
        Règle: {rule.name}
        Erreur: {str(error)}
        Timestamp: {datetime.now().isoformat()}
        
        Données concernées: {str(data)[:500]}...
        """
        
        self._send_notification("Erreur Règle Métier", message, priority="high")
    
    def _send_error_notification_task(self, task_name: str, error: Exception) -> None:
        """Envoie notification en cas d'erreur de tâche"""
        message = f"""
        Erreur tâche programmée détectée:
        
        Tâche: {task_name}
        Erreur: {str(error)}
        Timestamp: {datetime.now().isoformat()}
        """
        
        self._send_notification("Erreur Tâche Programmée", message, priority="high")
    
    def _send_notification(self, subject: str, message: str, priority: str = "normal") -> None:
        """Envoie notification via canaux configurés"""
        
        # Email
        if 'email' in self.notification_channels:
            self._send_email_notification(subject, message)
        
        # Slack
        if 'slack' in self.notification_channels:
            self._send_slack_notification(subject, message, priority)
        
        # Teams
        if 'teams' in self.notification_channels:
            self._send_teams_notification(subject, message, priority)
    
    def _send_email_notification(self, subject: str, message: str) -> None:
        """Envoie notification par email"""
        try:
            email_config = self.notification_channels['email']
            
            msg = MimeMultipart()
            msg['From'] = email_config['username']
            msg['To'] = self.config.get('notification_recipients', {}).get('email', '')
            msg['Subject'] = subject
            
            msg.attach(MimeText(message, 'plain'))
            
            with smtplib.SMTP(email_config['server'], email_config['port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
            
            logger.info("📧 Notification email envoyée")
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
    
    def _send_slack_notification(self, subject: str, message: str, priority: str) -> None:
        """Envoie notification Slack"""
        try:
            slack_config = self.notification_channels['slack']
            
            # Couleur selon priorité
            color = {"high": "danger", "normal": "good", "low": "warning"}.get(priority, "good")
            
            payload = {
                "channel": slack_config['channel'],
                "attachments": [{
                    "color": color,
                    "title": subject,
                    "text": message,
                    "footer": "Perplexity AI Automation",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(slack_config['webhook_url'], json=payload)
            response.raise_for_status()
            
            logger.info("💬 Notification Slack envoyée")
            
        except Exception as e:
            logger.error(f"Erreur envoi Slack: {e}")
    
    def _send_teams_notification(self, subject: str, message: str, priority: str) -> None:
        """Envoie notification Teams"""
        try:
            teams_config = self.notification_channels['teams']
            
            # Couleur selon priorité
            theme_color = {"high": "FF0000", "normal": "00FF00", "low": "FFA500"}.get(priority, "00FF00")
            
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": subject,
                "themeColor": theme_color,
                "sections": [{
                    "activityTitle": subject,
                    "activitySubtitle": "Perplexity AI Automation",
                    "text": message
                }]
            }
            
            response = requests.post(teams_config['webhook_url'], json=payload)
            response.raise_for_status()
            
            logger.info("👥 Notification Teams envoyée")
            
        except Exception as e:
            logger.error(f"Erreur envoi Teams: {e}")
    
    def get_task_history(self, task_name: Optional[str] = None, 
                        last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Récupère historique des tâches
        
        Args:
            task_name: Filtre par nom de tâche
            last_n: Nombre d'entrées récentes
            
        Returns:
            Liste des exécutions de tâches
        """
        history = self.task_history
        
        if task_name:
            history = [t for t in history if t['task_name'] == task_name]
        
        if last_n:
            history = history[-last_n:]
        
        return history
    
    def generate_automation_report(self) -> str:
        """Génère rapport d'automatisation"""
        
        report_sections = []
        
        # Statistiques générales
        total_tasks = len(self.task_history)
        successful_tasks = len([t for t in self.task_history if t['status'] == TaskStatus.COMPLETED.value])
        failed_tasks = len([t for t in self.task_history if t['status'] == TaskStatus.FAILED.value])
        
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        report_sections.append(f"# 🤖 Rapport d'Automatisation\n\n")
        report_sections.append(f"## Statistiques Générales\n")
        report_sections.append(f"- Total tâches exécutées: {total_tasks}\n")
        report_sections.append(f"- Succès: {successful_tasks} ({success_rate:.1f}%)\n")
        report_sections.append(f"- Échecs: {failed_tasks}\n")
        report_sections.append(f"- Taux de succès: {success_rate:.1f}%\n\n")
        
        # Tâches programmées
        report_sections.append(f"## Tâches Programmées Actives\n")
        for task_name, task_info in self.scheduled_tasks.items():
            report_sections.append(f"- **{task_name}**: {task_info['pattern']}\n")
        
        # Règles métier
        report_sections.append(f"\n## Règles Métier Configurées\n")
        active_rules = [r for r in self.business_rules if r.enabled]
        for rule in active_rules:
            report_sections.append(f"- **{rule.name}** (Priorité: {rule.priority})\n")
        
        return "".join(report_sections)

# Exemples de règles métier
def create_pricing_rules(automator: BusinessProcessAutomator) -> None:
    """Crée règles métier pour la gestion des prix"""
    
    # Règle 1: Alerte prix concurrent trop bas
    def condition_prix_concurrent_bas(data):
        return (data.get('competitor_price', 0) < data.get('our_price', 0) * 0.9)
    
    def action_alerte_prix_bas(data):
        message = f"🚨 Prix concurrent détecté: {data.get('competitor_price')}€ vs notre prix {data.get('our_price')}€"
        print(message)  # En réalité, enverrait notification
        return {'alert_sent': True, 'message': message}
    
    rule_prix = BusinessRule(
        rule_id="PRIX_001",
        name="Alerte Prix Concurrent Bas",
        description="Alerte quand concurrent 10% moins cher",
        condition_function=condition_prix_concurrent_bas,
        action_function=action_alerte_prix_bas,
        priority=5
    )
    
    automator.add_business_rule(rule_prix)
    
    # Règle 2: Ajustement automatique stock faible
    def condition_stock_faible(data):
        return data.get('stock_level', 0) < data.get('min_stock_threshold', 10)
    
    def action_reappro_stock(data):
        quantity_to_order = data.get('optimal_stock_level', 50) - data.get('stock_level', 0)
        # En réalité, passerait commande automatique
        return {'reorder_triggered': True, 'quantity': quantity_to_order}
    
    rule_stock = BusinessRule(
        rule_id="STOCK_001",
        name="Réapprovisionnement Automatique",
        description="Commande automatique si stock < seuil",
        condition_function=condition_stock_faible,
        action_function=action_reappro_stock,
        priority=3
    )
    
    automator.add_business_rule(rule_stock)

# Exemple d'utilisation complète
def exemple_automatisation_complete():
    """Exemple complet d'automatisation de processus métier"""
    
    # Configuration
    config = {
        'smtp': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'automation@company.com',
            'password': 'app_password'
        },
        'slack': {
            'webhook_url': 'https://hooks.slack.com/services/xxx',
            'channel': '#automation-alerts'
        },
        'notification_recipients': {
            'email': 'manager@company.com'
        }
    }
    
    # Initialisation
    automator = BusinessProcessAutomator(config)
    
    # Ajout règles métier
    create_pricing_rules(automator)
    
    # Tâches récurrentes
    def tache_analyse_quotidienne():
        """Analyse quotidienne des performances"""
        print("📊 Exécution analyse quotidienne...")
        
        # Simulation collecte données
        data = {
            'sales_today': 1250.50,
            'orders_count': 25,
            'avg_order_value': 50.02
        }
        
        # Simulation analyse
        if data['sales_today'] < 1000:
            return {'status': 'warning', 'message': 'Ventes sous objectif'}
        else:
            return {'status': 'success', 'message': 'Objectifs atteints'}
    
    def tache_verification_stock():
        """Vérification stock produits"""
        print("📦 Vérification des stocks...")
        
        # Simulation données stock
        products_to_check = [
            {'sku': 'PROD001', 'stock_level': 5, 'min_stock_threshold': 10, 'optimal_stock_level': 50},
            {'sku': 'PROD002', 'stock_level': 25, 'min_stock_threshold': 20, 'optimal_stock_level': 100}
        ]
        
        reorder_results = []
        for product in products_to_check:
            # Application règles métier
            rules_results = automator.execute_business_rules(product)
            reorder_results.extend(rules_results)
        
        return {'checked_products': len(products_to_check), 'rules_executed': len(reorder_results)}
    
    # Programmation tâches
    automator.schedule_recurring_task('analyse_quotidienne', tache_analyse_quotidienne, 'daily')
    automator.schedule_recurring_task('verification_stock', tache_verification_stock, 'every_4_hours')
    
    # Test exécution règles sur données exemple
    test_data = {
        'competitor_price': 45.0,
        'our_price': 55.0,
        'stock_level': 8,
        'min_stock_threshold': 10,
        'optimal_stock_level': 50
    }
    
    print("🧪 Test règles métier...")
    results = automator.execute_business_rules(test_data)
    
    for result in results:
        print(f"Règle: {result['rule_name']} - Status: {result['status']}")
    
    # Exécution tâches programmées (une fois pour demo)
    print("\n🚀 Exécution tâches programmées (demo)...")
    automator.run_scheduler(run_pending_only=True)
    
    # Génération rapport
    report = automator.generate_automation_report()
    
    # Sauvegarde
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'automation_report_{timestamp}.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Export historique tâches
    history_df = pd.DataFrame(automator.get_task_history())
    if not history_df.empty:
        history_df.to_excel(f'task_history_{timestamp}.xlsx', index=False)
    
    print(f"✅ Automatisation configurée - Rapport sauvegardé: automation_report_{timestamp}.md")
    
    return {
        'automator': automator,
        'rules_results': results,
        'report': report
    }

if __name__ == "__main__":
    results = exemple_automatisation_complete()
    print("\nAutomation Setup Complete!")
```

Ces exemples de scripts Python illustrent la puissance de l'intégration avec Perplexity AI pour créer des automatisations métier sophistiquées, robustes et facilement maintenables. Chaque script est documenté, testable et peut être adapté aux besoins spécifiques de différents secteurs d'activité.