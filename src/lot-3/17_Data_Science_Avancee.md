# Data Science Avancée Métier - Espace Perplexity AI

## Vue d'ensemble
Ce document présente une suite complète d'outils et méthodologies de data science avancée spécialement adaptés aux besoins métier de l'espace Perplexity AI, couvrant les statistiques, les séries temporelles, la prédiction, l'analyse exploratoire et l'apprentissage automatique orienté business.

## Architecture Data Science Métier

### Écosystème Analytics Métier

```
┌─────────────────────────────────────────────────────────────────┐
│                 ÉCOSYSTÈME DATA SCIENCE MÉTIER                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Analytics Exploratoire  📈 Séries Temporelles  🤖 ML Métier │
│  ┌─────────────────┐       ┌─────────────────┐     ┌─────────┐  │
│  │ • EDA Auto      │       │ • Forecasting   │     │ • AutoML│  │
│  │ • Viz Interactive│       │ • Seasonality   │     │ • Tuning│  │
│  │ • Pattern Detect│       │ • Trend Analysis│     │ • Deploy│  │
│  │ • Outlier Detect│       │ • Anomaly Detect│     │ • Monitor│  │
│  └─────────────────┘       └─────────────────┘     └─────────┘  │
│                                  ↕                              │
│  📋 Reporting Auto      🎯 Business Intelligence   ⚡ Real-time │
│  ┌─────────────────┐     ┌─────────────────┐      ┌─────────┐  │
│  │ • KPI Dashboard │     │ • Insights Auto │      │ • Stream│  │
│  │ • Alert Smart   │     │ • Recommendations│      │ • CEP   │  │
│  │ • Export Multi  │     │ • Impact Analysis│      │ • Event │  │
│  │ • Schedule      │     │ • ROI Tracking  │      │ • Trigger│  │
│  └─────────────────┘     └─────────────────┘      └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Module 1 : Analytics Exploratoire Automatisé

### Analyseur de Données Métier Intelligent

```python
# business_data_analyzer.py
"""
Analyseur automatique de données métier avec génération d'insights
Intègre EDA, détection patterns, recommandations d'actions business
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import scipy.stats as stats
from scipy.stats import chi2_contingency, normaltest, jarque_bera
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class DataQualityReport:
    """Rapport qualité des données"""
    total_rows: int
    total_columns: int
    missing_values_report: Dict[str, Any]
    duplicate_rows: int
    data_types_summary: Dict[str, int]
    outliers_report: Dict[str, Any]
    quality_score: float
    recommendations: List[str]

@dataclass
class BusinessInsight:
    """Insight métier découvert automatiquement"""
    type: str  # trend, correlation, anomaly, pattern, opportunity
    title: str
    description: str
    confidence: float  # 0-1
    business_impact: str  # high, medium, low
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]
    visualization: Optional[str] = None

@dataclass
class AnalyticsReport:
    """Rapport complet d'analyse métier"""
    dataset_name: str
    analysis_timestamp: datetime
    data_quality: DataQualityReport
    descriptive_stats: Dict[str, Any]
    business_insights: List[BusinessInsight]
    correlations: Dict[str, Any]
    clusters_analysis: Dict[str, Any]
    forecasting_results: Dict[str, Any]
    visualizations: List[str]

class BusinessDataAnalyzer:
    """Analyseur avancé de données métier"""
    
    def __init__(self, business_context: Dict[str, Any] = None):
        self.business_context = business_context or {}
        self.insights = []
        self.visualizations = []
        
        # Configuration métier
        self.business_metrics = {
            'revenue': ['revenue', 'sales', 'income', 'turnover', 'chiffre_affaires'],
            'profit': ['profit', 'margin', 'benefice', 'marge'],
            'costs': ['cost', 'expense', 'cout', 'depense'],
            'customers': ['customer', 'client', 'user', 'utilisateur'],
            'products': ['product', 'item', 'produit', 'article'],
            'time': ['date', 'time', 'timestamp', 'periode']
        }
        
        self.kpi_thresholds = {
            'growth_rate': {'good': 0.1, 'acceptable': 0.05, 'poor': 0.0},
            'conversion_rate': {'good': 0.05, 'acceptable': 0.02, 'poor': 0.01},
            'churn_rate': {'good': 0.05, 'acceptable': 0.10, 'poor': 0.20},
            'margin_percent': {'good': 0.20, 'acceptable': 0.15, 'poor': 0.10}
        }
    
    def analyze_dataset(self, df: pd.DataFrame, dataset_name: str = "Business Data") -> AnalyticsReport:
        """Analyse complète d'un dataset métier"""
        
        logger.info(f"🔍 Début analyse dataset: {dataset_name}")
        
        # 1. Analyse qualité données
        data_quality = self._analyze_data_quality(df)
        
        # 2. Statistiques descriptives enrichies
        descriptive_stats = self._generate_descriptive_stats(df)
        
        # 3. Détection insights métier
        business_insights = self._discover_business_insights(df)
        
        # 4. Analyse corrélationnelle
        correlations = self._analyze_correlations(df)
        
        # 5. Analyse clustering
        clusters_analysis = self._perform_clustering_analysis(df)
        
        # 6. Prédictions et forecasting
        forecasting_results = self._generate_forecasting(df)
        
        # 7. Génération visualisations
        visualizations = self._generate_visualizations(df, dataset_name)
        
        # Compilation rapport final
        report = AnalyticsReport(
            dataset_name=dataset_name,
            analysis_timestamp=datetime.now(),
            data_quality=data_quality,
            descriptive_stats=descriptive_stats,
            business_insights=business_insights,
            correlations=correlations,
            clusters_analysis=clusters_analysis,
            forecasting_results=forecasting_results,
            visualizations=visualizations
        )
        
        logger.info(f"✅ Analyse terminée - {len(business_insights)} insights découverts")
        return report
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> DataQualityReport:
        """Analyse qualité des données avec focus métier"""
        
        # Valeurs manquantes
        missing_analysis = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            missing_analysis[col] = {
                'count': int(missing_count),
                'percentage': round(missing_pct, 2),
                'business_impact': self._assess_missing_impact(col, missing_pct)
            }
        
        # Doublons
        duplicate_count = df.duplicated().sum()
        
        # Types de données
        data_types = df.dtypes.value_counts().to_dict()
        data_types_summary = {str(k): int(v) for k, v in data_types.items()}
        
        # Outliers par colonne numérique
        outliers_report = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            
            outliers_report[col] = {
                'count': len(outliers),
                'percentage': round((len(outliers) / len(df)) * 100, 2),
                'lower_bound': round(lower_bound, 2),
                'upper_bound': round(upper_bound, 2),
                'business_relevance': self._assess_outlier_relevance(col, outliers)
            }
        
        # Score qualité global (0-100)
        quality_score = self._calculate_quality_score(missing_analysis, duplicate_count, outliers_report, df)
        
        # Recommandations
        recommendations = self._generate_quality_recommendations(missing_analysis, duplicate_count, outliers_report, quality_score)
        
        return DataQualityReport(
            total_rows=len(df),
            total_columns=len(df.columns),
            missing_values_report=missing_analysis,
            duplicate_rows=int(duplicate_count),
            data_types_summary=data_types_summary,
            outliers_report=outliers_report,
            quality_score=quality_score,
            recommendations=recommendations
        )
    
    def _assess_missing_impact(self, column_name: str, missing_pct: float) -> str:
        """Évalue l'impact business des valeurs manquantes"""
        
        # Colonnes critiques métier
        critical_columns = ['revenue', 'price', 'cost', 'customer_id', 'date']
        important_columns = ['quantity', 'category', 'region', 'channel']
        
        col_lower = column_name.lower()
        
        if any(critical in col_lower for critical in critical_columns):
            if missing_pct > 10:
                return "CRITIQUE - Métrique business clé avec trop de valeurs manquantes"
            elif missing_pct > 5:
                return "ÉLEVÉ - Métrique importante partiellement manquante"
            else:
                return "MODÉRÉ - Métrique clé avec peu de manques"
        
        elif any(important in col_lower for important in important_columns):
            if missing_pct > 20:
                return "ÉLEVÉ - Dimension d'analyse importante trop incomplète"
            else:
                return "MODÉRÉ - Dimension partiellement disponible"
        
        else:
            if missing_pct > 50:
                return "FAIBLE - Colonne peu utilisable"
            else:
                return "FAIBLE - Impact limité"
    
    def _assess_outlier_relevance(self, column_name: str, outliers: pd.Series) -> str:
        """Évalue la relevance métier des outliers"""
        
        col_lower = column_name.lower()
        
        # Pour les métriques monétaires, les outliers peuvent être importants
        if any(money_term in col_lower for money_term in ['revenue', 'sales', 'price', 'cost', 'profit']):
            return "IMPORTANTE - Outliers financiers à analyser (gros clients, promotions?)"
        
        # Pour les quantités, outliers peuvent indiquer commandes spéciales
        elif any(qty_term in col_lower for qty_term in ['quantity', 'volume', 'count']):
            return "MODÉRÉE - Peut indiquer commandes exceptionnelles"
        
        # Pour les métriques temporelles
        elif any(time_term in col_lower for time_term in ['time', 'duration', 'delay']):
            return "IMPORTANTE - Problèmes opérationnels potentiels"
        
        else:
            return "FAIBLE - À examiner selon contexte"
    
    def _generate_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Génère statistiques descriptives enrichies"""
        
        stats_summary = {}
        
        # Statistiques numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            numeric_stats = df[numeric_cols].describe()
            
            # Enrichissement avec métriques métier
            enhanced_numeric = {}
            for col in numeric_cols:
                col_data = df[col].dropna()
                
                enhanced_numeric[col] = {
                    'count': int(col_data.count()),
                    'mean': round(col_data.mean(), 2),
                    'median': round(col_data.median(), 2),
                    'std': round(col_data.std(), 2),
                    'min': round(col_data.min(), 2),
                    'max': round(col_data.max(), 2),
                    'q25': round(col_data.quantile(0.25), 2),
                    'q75': round(col_data.quantile(0.75), 2),
                    'skewness': round(stats.skew(col_data), 3),
                    'kurtosis': round(stats.kurtosis(col_data), 3),
                    'coefficient_variation': round(col_data.std() / col_data.mean(), 3) if col_data.mean() != 0 else None,
                    'business_interpretation': self._interpret_numeric_column(col, col_data)
                }
            
            stats_summary['numeric'] = enhanced_numeric
        
        # Statistiques catégorielles
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            categorical_stats = {}
            
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                
                categorical_stats[col] = {
                    'unique_count': int(df[col].nunique()),
                    'most_frequent': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    'most_frequent_percentage': round((value_counts.iloc[0] / len(df)) * 100, 2) if len(value_counts) > 0 else 0,
                    'distribution_entropy': round(stats.entropy(value_counts), 3),
                    'business_interpretation': self._interpret_categorical_column(col, value_counts)
                }
            
            stats_summary['categorical'] = categorical_stats
        
        # Statistiques temporelles si colonnes de date détectées
        date_cols = self._detect_date_columns(df)
        if date_cols:
            temporal_stats = {}
            
            for col in date_cols:
                date_data = pd.to_datetime(df[col], errors='coerce').dropna()
                if len(date_data) > 0:
                    temporal_stats[col] = {
                        'earliest_date': date_data.min().strftime('%Y-%m-%d'),
                        'latest_date': date_data.max().strftime('%Y-%m-%d'),
                        'date_range_days': (date_data.max() - date_data.min()).days,
                        'frequency_analysis': self._analyze_temporal_frequency(date_data),
                        'business_interpretation': self._interpret_temporal_column(col, date_data)
                    }
            
            stats_summary['temporal'] = temporal_stats
        
        return stats_summary
    
    def _discover_business_insights(self, df: pd.DataFrame) -> List[BusinessInsight]:
        """Découvre automatiquement les insights métier"""
        
        insights = []
        
        # 1. Insights de tendance temporelle
        insights.extend(self._detect_trend_insights(df))
        
        # 2. Insights de corrélation business
        insights.extend(self._detect_correlation_insights(df))
        
        # 3. Insights d'anomalies
        insights.extend(self._detect_anomaly_insights(df))
        
        # 4. Insights de segmentation
        insights.extend(self._detect_segmentation_insights(df))
        
        # 5. Insights d'opportunités
        insights.extend(self._detect_opportunity_insights(df))
        
        # Tri par impact business et confiance
        insights.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x.business_impact], 
            x.confidence
        ), reverse=True)
        
        return insights
    
    def _detect_trend_insights(self, df: pd.DataFrame) -> List[BusinessInsight]:
        """Détecte insights de tendances temporelles"""
        
        insights = []
        date_cols = self._detect_date_columns(df)
        
        if not date_cols:
            return insights
        
        # Analyse des métriques business dans le temps
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for date_col in date_cols:
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col])
            
            if len(df_temp) < 10:  # Pas assez de données
                continue
            
            # Groupe par période et calcule métriques
            df_temp['period'] = df_temp[date_col].dt.to_period('M')  # Par mois
            monthly_data = df_temp.groupby('period')[numeric_cols].agg(['sum', 'mean', 'count'])
            
            for metric in numeric_cols:
                if self._is_business_metric(metric):
                    metric_data = monthly_data[(metric, 'sum')].dropna()
                    
                    if len(metric_data) >= 3:
                        # Calcul tendance
                        x = np.arange(len(metric_data))
                        z = np.polyfit(x, metric_data.values, 1)
                        trend_slope = z[0]
                        
                        # Calcul taux de croissance mensuel moyen
                        growth_rate = (metric_data.iloc[-1] / metric_data.iloc[0]) ** (1/(len(metric_data)-1)) - 1
                        
                        # Classification de la tendance
                        if abs(growth_rate) > 0.05:  # 5% croissance mensuelle
                            trend_strength = "FORTE"
                            confidence = 0.9
                            business_impact = "high"
                        elif abs(growth_rate) > 0.02:
                            trend_strength = "MODÉRÉE"
                            confidence = 0.7
                            business_impact = "medium"
                        else:
                            trend_strength = "FAIBLE"
                            confidence = 0.5
                            business_impact = "low"
                        
                        trend_direction = "CROISSANCE" if growth_rate > 0 else "DÉCLIN"
                        
                        # Génération insight
                        insight = BusinessInsight(
                            type="trend",
                            title=f"{trend_direction} {trend_strength} - {metric}",
                            description=f"Le métrique '{metric}' montre une {trend_direction.lower()} {trend_strength.lower()} avec un taux de croissance mensuel moyen de {growth_rate*100:.1f}%",
                            confidence=confidence,
                            business_impact=business_impact,
                            recommended_actions=self._generate_trend_actions(trend_direction, growth_rate, metric),
                            supporting_data={
                                'growth_rate_monthly': round(growth_rate * 100, 2),
                                'trend_slope': round(trend_slope, 2),
                                'periods_analyzed': len(metric_data),
                                'metric_name': metric,
                                'latest_value': round(metric_data.iloc[-1], 2),
                                'first_value': round(metric_data.iloc[0], 2)
                            }
                        )
                        
                        insights.append(insight)
        
        return insights
    
    def _detect_correlation_insights(self, df: pd.DataFrame) -> List[BusinessInsight]:
        """Détecte insights de corrélations métier importantes"""
        
        insights = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return insights
        
        # Calcul matrice de corrélation
        corr_matrix = df[numeric_cols].corr()
        
        # Recherche corrélations significatives
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i >= j:  # Évite doublons et auto-corrélation
                    continue
                
                correlation = corr_matrix.loc[col1, col2]
                
                if pd.isna(correlation):
                    continue
                
                # Filtre corrélations significatives
                if abs(correlation) >= 0.5:
                    
                    # Détermine force et direction
                    if abs(correlation) >= 0.8:
                        strength = "TRÈS FORTE"
                        confidence = 0.95
                        business_impact = "high"
                    elif abs(correlation) >= 0.7:
                        strength = "FORTE"
                        confidence = 0.85
                        business_impact = "high"
                    elif abs(correlation) >= 0.6:
                        strength = "MODÉRÉE À FORTE"
                        confidence = 0.75
                        business_impact = "medium"
                    else:
                        strength = "MODÉRÉE"
                        confidence = 0.6
                        business_impact = "medium"
                    
                    direction = "POSITIVE" if correlation > 0 else "NÉGATIVE"
                    
                    # Interprétation métier
                    business_meaning = self._interpret_correlation_business(col1, col2, correlation)
                    
                    insight = BusinessInsight(
                        type="correlation",
                        title=f"Corrélation {strength} {direction} - {col1} ↔ {col2}",
                        description=f"Corrélation {direction.lower()} {strength.lower()} ({correlation:.2f}) entre '{col1}' et '{col2}'. {business_meaning}",
                        confidence=confidence,
                        business_impact=business_impact,
                        recommended_actions=self._generate_correlation_actions(col1, col2, correlation),
                        supporting_data={
                            'correlation_coefficient': round(correlation, 3),
                            'variable_1': col1,
                            'variable_2': col2,
                            'strength': strength,
                            'direction': direction
                        }
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def _detect_anomaly_insights(self, df: pd.DataFrame) -> List[BusinessInsight]:
        """Détecte anomalies et patterns inhabituels"""
        
        insights = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Détection d'anomalies avec Isolation Forest
        for col in numeric_cols:
            if self._is_business_metric(col):
                col_data = df[col].dropna()
                
                if len(col_data) < 10:
                    continue
                
                # Isolation Forest pour détection anomalies
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_labels = iso_forest.fit_predict(col_data.values.reshape(-1, 1))
                
                anomaly_indices = np.where(anomaly_labels == -1)[0]
                normal_indices = np.where(anomaly_labels == 1)[0]
                
                if len(anomaly_indices) > 0:
                    anomalous_values = col_data.iloc[anomaly_indices]
                    normal_values = col_data.iloc[normal_indices]
                    
                    # Statistiques anomalies
                    anomaly_pct = len(anomaly_indices) / len(col_data) * 100
                    avg_anomaly = anomalous_values.mean()
                    avg_normal = normal_values.mean()
                    
                    # Classification business impact
                    if anomaly_pct > 15:
                        impact = "high"
                        confidence = 0.9
                    elif anomaly_pct > 5:
                        impact = "medium"
                        confidence = 0.75
                    else:
                        impact = "medium"
                        confidence = 0.6
                    
                    # Interprétation métier
                    business_interpretation = self._interpret_anomalies_business(col, anomalous_values, avg_normal)
                    
                    insight = BusinessInsight(
                        type="anomaly",
                        title=f"Anomalies détectées - {col}",
                        description=f"{len(anomaly_indices)} anomalies détectées dans '{col}' ({anomaly_pct:.1f}% des données). {business_interpretation}",
                        confidence=confidence,
                        business_impact=impact,
                        recommended_actions=self._generate_anomaly_actions(col, anomalous_values),
                        supporting_data={
                            'anomaly_count': len(anomaly_indices),
                            'anomaly_percentage': round(anomaly_pct, 2),
                            'avg_anomaly_value': round(avg_anomaly, 2),
                            'avg_normal_value': round(avg_normal, 2),
                            'anomaly_values': anomalous_values.tolist()[:10]  # Top 10
                        }
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def _generate_trend_actions(self, trend_direction: str, growth_rate: float, metric: str) -> List[str]:
        """Génère actions recommandées selon tendance détectée"""
        
        actions = []
        
        if trend_direction == "CROISSANCE":
            if growth_rate > 0.1:  # Forte croissance
                actions.extend([
                    f"Capitaliser sur la forte croissance de {metric}",
                    "Analyser les facteurs de succès pour les répliquer",
                    "Prévoir les ressources nécessaires pour soutenir la croissance",
                    "Évaluer la capacité d'absorption de la croissance"
                ])
            else:
                actions.extend([
                    f"Maintenir et accélérer la croissance de {metric}",
                    "Identifier les leviers d'amélioration",
                    "Benchmarker avec les concurrents"
                ])
        else:  # DÉCLIN
            if abs(growth_rate) > 0.1:  # Fort déclin
                actions.extend([
                    f"URGENT: Analyser les causes du déclin de {metric}",
                    "Mettre en place un plan de redressement immédiat",
                    "Identifier les facteurs de dégradation",
                    "Revoir la stratégie métier concernée"
                ])
            else:
                actions.extend([
                    f"Surveiller et corriger le déclin de {metric}",
                    "Analyser les tendances du marché",
                    "Identifier les actions correctives"
                ])
        
        return actions
    
    def _generate_correlation_actions(self, col1: str, col2: str, correlation: float) -> List[str]:
        """Génère actions basées sur corrélations découvertes"""
        
        actions = []
        
        # Actions selon type de corrélation
        if correlation > 0.7:  # Forte corrélation positive
            actions.extend([
                f"Exploiter la relation positive entre {col1} et {col2}",
                f"Optimiser {col1} pour améliorer {col2}",
                "Créer des métriques combinées pour le pilotage",
                "Analyser la causalité de cette relation"
            ])
        elif correlation < -0.7:  # Forte corrélation négative
            actions.extend([
                f"Gérer le trade-off entre {col1} et {col2}",
                "Rechercher un point d'équilibre optimal",
                "Analyser si cette relation est souhaitable",
                "Considérer des stratégies de découplage"
            ])
        
        # Actions spécifiques selon type de métriques
        if any(revenue_term in col1.lower() for revenue_term in ['revenue', 'sales', 'chiffre']):
            actions.append("Utiliser cette corrélation pour les prévisions de revenus")
        
        if any(cost_term in col1.lower() or cost_term in col2.lower() for cost_term in ['cost', 'cout', 'expense']):
            actions.append("Intégrer dans l'analyse de rentabilité")
        
        return actions
    
    def _perform_clustering_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Effectue analyse de clustering pour segmentation métier"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {"status": "insufficient_numeric_data"}
        
        # Préparation données
        df_numeric = df[numeric_cols].dropna()
        
        if len(df_numeric) < 10:
            return {"status": "insufficient_rows"}
        
        # Standardisation
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(df_numeric)
        
        # K-means clustering
        optimal_k = self._find_optimal_clusters(data_scaled)
        
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        cluster_labels = kmeans.fit_predict(data_scaled)
        
        # Analyse des clusters
        df_clustered = df_numeric.copy()
        df_clustered['cluster'] = cluster_labels
        
        cluster_profiles = {}
        for cluster_id in range(optimal_k):
            cluster_data = df_clustered[df_clustered['cluster'] == cluster_id]
            
            cluster_profiles[f"cluster_{cluster_id}"] = {
                'size': len(cluster_data),
                'percentage': round((len(cluster_data) / len(df_clustered)) * 100, 1),
                'characteristics': self._analyze_cluster_characteristics(cluster_data, numeric_cols),
                'business_interpretation': self._interpret_cluster_business(cluster_data, numeric_cols, cluster_id)
            }
        
        # DBSCAN pour détection d'outliers
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        dbscan_labels = dbscan.fit_predict(data_scaled)
        outliers_count = sum(dbscan_labels == -1)
        
        return {
            "status": "complete",
            "optimal_clusters": optimal_k,
            "cluster_profiles": cluster_profiles,
            "outliers_detected": outliers_count,
            "outliers_percentage": round((outliers_count / len(df_numeric)) * 100, 2),
            "business_recommendations": self._generate_clustering_recommendations(cluster_profiles)
        }
    
    def _find_optimal_clusters(self, data: np.ndarray, max_k: int = 8) -> int:
        """Trouve nombre optimal de clusters avec méthode elbow"""
        
        if len(data) < max_k * 2:
            max_k = max(2, len(data) // 2)
        
        inertias = []
        k_range = range(2, min(max_k + 1, len(data)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(data)
            inertias.append(kmeans.inertia_)
        
        # Méthode elbow simplifiée
        if len(inertias) >= 2:
            diffs = np.diff(inertias)
            second_diffs = np.diff(diffs)
            
            if len(second_diffs) > 0:
                optimal_idx = np.argmax(second_diffs) + 2
                return min(optimal_idx, len(k_range) + 1)
        
        return 3  # Défaut
    
    def _generate_visualizations(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        """Génère visualisations automatiques"""
        
        visualizations = []
        
        # 1. Distribution des variables numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            fig = self._create_distributions_plot(df, numeric_cols, dataset_name)
            viz_name = f"distributions_{dataset_name.lower().replace(' ', '_')}.html"
            fig.write_html(viz_name)
            visualizations.append(viz_name)
        
        # 2. Matrice de corrélation interactive
        if len(numeric_cols) >= 2:
            fig = self._create_correlation_heatmap(df, numeric_cols)
            viz_name = f"correlations_{dataset_name.lower().replace(' ', '_')}.html"
            fig.write_html(viz_name)
            visualizations.append(viz_name)
        
        # 3. Analyse temporelle si données de date
        date_cols = self._detect_date_columns(df)
        if date_cols and len(numeric_cols) > 0:
            fig = self._create_temporal_analysis(df, date_cols[0], numeric_cols[:3])
            viz_name = f"temporal_{dataset_name.lower().replace(' ', '_')}.html"
            fig.write_html(viz_name)
            visualizations.append(viz_name)
        
        return visualizations
    
    def _create_distributions_plot(self, df: pd.DataFrame, numeric_cols: List[str], title: str):
        """Crée graphique distributions avec insights"""
        
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=[f"Distribution - {col}" for col in numeric_cols[:n_rows*n_cols]],
            specs=[[{"secondary_y": False} for _ in range(n_cols)] for _ in range(n_rows)]
        )
        
        for i, col in enumerate(numeric_cols):
            row = i // n_cols + 1
            col_pos = i % n_cols + 1
            
            # Histogramme
            fig.add_trace(
                go.Histogram(
                    x=df[col].dropna(),
                    name=col,
                    showlegend=False,
                    marker_color='lightblue',
                    opacity=0.7
                ),
                row=row, col=col_pos
            )
        
        fig.update_layout(
            title_text=f"Distributions des Variables - {title}",
            title_x=0.5,
            height=400 * n_rows,
            showlegend=False
        )
        
        return fig
    
    def _create_correlation_heatmap(self, df: pd.DataFrame, numeric_cols: List[str]):
        """Crée heatmap corrélations interactive"""
        
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu_r',
            zmin=-1, zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hovertemplate="<b>%{x} vs %{y}</b><br>Corrélation: %{z:.3f}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Matrice de Corrélations Interactive",
            title_x=0.5,
            xaxis_title="Variables",
            yaxis_title="Variables",
            width=600,
            height=600
        )
        
        return fig
    
    def _create_temporal_analysis(self, df: pd.DataFrame, date_col: str, numeric_cols: List[str]):
        """Crée analyse temporelle interactive"""
        
        df_temp = df.copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
        df_temp = df_temp.dropna(subset=[date_col]).sort_values(date_col)
        
        fig = make_subplots(
            rows=len(numeric_cols), cols=1,
            subplot_titles=[f"Évolution - {col}" for col in numeric_cols],
            shared_xaxes=True
        )
        
        for i, col in enumerate(numeric_cols):
            fig.add_trace(
                go.Scatter(
                    x=df_temp[date_col],
                    y=df_temp[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2),
                    marker=dict(size=4),
                    hovertemplate=f"<b>{col}</b><br>Date: %{{x}}<br>Valeur: %{{y:.2f}}<extra></extra>"
                ),
                row=i+1, col=1
            )
        
        fig.update_layout(
            title="Analyse Temporelle des Métriques Métier",
            title_x=0.5,
            height=300 * len(numeric_cols),
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Date", row=len(numeric_cols), col=1)
        
        return fig
    
    # Méthodes utilitaires
    def _is_business_metric(self, column_name: str) -> bool:
        """Détermine si colonne est métrique business importante"""
        col_lower = column_name.lower()
        
        business_keywords = [
            'revenue', 'sales', 'income', 'profit', 'margin', 'cost', 'expense',
            'price', 'quantity', 'volume', 'count', 'amount', 'total',
            'customer', 'client', 'user', 'conversion', 'churn', 'retention'
        ]
        
        return any(keyword in col_lower for keyword in business_keywords)
    
    def _detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """Détecte colonnes de dates"""
        date_cols = []
        
        for col in df.columns:
            # Test conversion datetime
            try:
                if df[col].dtype == 'datetime64[ns]':
                    date_cols.append(col)
                else:
                    # Teste échantillon
                    sample = df[col].dropna().head(100)
                    if len(sample) > 0:
                        converted = pd.to_datetime(sample, errors='coerce')
                        if converted.notna().sum() / len(sample) > 0.8:  # 80% convertibles
                            date_cols.append(col)
            except:
                continue
        
        return date_cols

# Démonstration complète
def demo_advanced_business_analytics():
    """Démonstration analytics métier avancée"""
    
    # Génération dataset exemple
    np.random.seed(42)
    n_rows = 1000
    
    # Simulation données e-commerce
    dates = pd.date_range('2024-01-01', periods=n_rows, freq='H')
    
    data = {
        'date': dates,
        'revenue': np.random.normal(1000, 300, n_rows) * (1 + 0.1 * np.sin(np.arange(n_rows) * 2 * np.pi / 168)),  # Saisonnalité hebdomadaire
        'orders_count': np.random.poisson(50, n_rows),
        'avg_order_value': np.random.normal(200, 50, n_rows),
        'marketing_spend': np.random.normal(500, 150, n_rows),
        'customer_acquisition_cost': np.random.normal(25, 8, n_rows),
        'conversion_rate': np.random.beta(2, 50, n_rows),  # Taux conversion réaliste
        'product_category': np.random.choice(['Electronics', 'Fashion', 'Home', 'Sports'], n_rows, p=[0.4, 0.3, 0.2, 0.1]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_rows)
    }
    
    # Corrélations intentionnelles
    data['revenue'] = data['orders_count'] * data['avg_order_value'] * np.random.normal(1, 0.1, n_rows)
    
    # Ajout anomalies intentionnelles
    anomaly_indices = np.random.choice(n_rows, 50, replace=False)
    for idx in anomaly_indices:
        data['revenue'][idx] *= 3  # Spike revenus
    
    df = pd.DataFrame(data)
    
    print("🔬 DÉMONSTRATION DATA SCIENCE MÉTIER AVANCÉE")
    print("=" * 60)
    
    # Initialisation analyseur
    business_context = {
        'industry': 'ecommerce',
        'key_metrics': ['revenue', 'conversion_rate', 'customer_acquisition_cost'],
        'business_goals': ['growth', 'profitability', 'efficiency']
    }
    
    analyzer = BusinessDataAnalyzer(business_context)
    
    # Analyse complète
    report = analyzer.analyze_dataset(df, "E-commerce Performance Data")
    
    # Affichage résultats
    print(f"\n📊 QUALITÉ DES DONNÉES:")
    print(f"• Score qualité: {report.data_quality.quality_score:.1f}/100")
    print(f"• Lignes: {report.data_quality.total_rows:,}")
    print(f"• Colonnes: {report.data_quality.total_columns}")
    print(f"• Doublons: {report.data_quality.duplicate_rows}")
    
    print(f"\n🔍 TOP INSIGHTS MÉTIER:")
    for i, insight in enumerate(report.business_insights[:5], 1):
        print(f"{i}. [{insight.type.upper()}] {insight.title}")
        print(f"   Impact: {insight.business_impact.upper()} | Confiance: {insight.confidence:.1%}")
        print(f"   {insight.description}")
        if insight.recommended_actions:
            print(f"   Actions: {insight.recommended_actions[0]}")
        print()
    
    print(f"\n📈 STATISTIQUES CLÉS:")
    if 'numeric' in report.descriptive_stats:
        for metric, stats in list(report.descriptive_stats['numeric'].items())[:3]:
            print(f"• {metric}:")
            print(f"  - Moyenne: {stats['mean']:,.2f}")
            print(f"  - Médiane: {stats['median']:,.2f}")
            print(f"  - CV: {stats['coefficient_variation']:.2f}")
    
    print(f"\n🎯 CLUSTERING:")
    if report.clusters_analysis.get('status') == 'complete':
        clusters = report.clusters_analysis
        print(f"• Clusters optimaux: {clusters['optimal_clusters']}")
        print(f"• Outliers détectés: {clusters['outliers_detected']} ({clusters['outliers_percentage']:.1f}%)")
    
    print(f"\n📊 VISUALISATIONS GÉNÉRÉES:")
    for viz in report.visualizations:
        print(f"• {viz}")
    
    return report

if __name__ == "__main__":
    report = demo_advanced_business_analytics()
```

## Module 2 : Séries Temporelles et Forecasting Métier

### Prédicteur Avancé de Séries Temporelles

```python
# business_forecasting_engine.py
"""
Moteur de forecasting avancé pour métriques métier
Intègre saisonnalité, tendances, événements externes, et modèles ML
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML et stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import scipy.stats as stats

# Séries temporelles spécialisées
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Visualisation
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ForecastConfig:
    """Configuration pour forecasting"""
    target_column: str
    forecast_horizon: int  # nombre de périodes à prédire
    frequency: str  # D, W, M, Q, Y
    seasonality_periods: List[int]  # [7, 30, 365] pour daily data
    confidence_levels: List[float] = None  # [0.80, 0.95]
    external_factors: List[str] = None  # colonnes facteurs externes
    business_constraints: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = [0.80, 0.95]
        if self.external_factors is None:
            self.external_factors = []
        if self.business_constraints is None:
            self.business_constraints = {}

@dataclass
class ForecastResult:
    """Résultat de prédiction"""
    config: ForecastConfig
    historical_data: pd.DataFrame
    forecast_data: pd.DataFrame
    model_performance: Dict[str, Any]
    decomposition: Dict[str, Any]
    business_insights: List[str]
    confidence_intervals: Dict[float, pd.DataFrame]
    model_explanation: Dict[str, Any]
    
class BusinessForecastingEngine:
    """Moteur de forecasting métier avancé"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.setup_models()
    
    def setup_models(self):
        """Initialise ensemble de modèles"""
        self.models = {
            'linear_trend': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            # ARIMA et Exponential Smoothing seront configurés dynamiquement
        }
    
    def forecast_timeseries(self, df: pd.DataFrame, config: ForecastConfig) -> ForecastResult:
        """Prédiction complète série temporelle métier"""
        
        logger.info(f"🔮 Début forecasting: {config.target_column} sur {config.forecast_horizon} périodes")
        
        # 1. Préparation et validation données
        prepared_data = self._prepare_timeseries_data(df, config)
        
        # 2. Décomposition saisonnière
        decomposition = self._decompose_timeseries(prepared_data, config)
        
        # 3. Tests de stationnarité
        stationarity = self._test_stationarity(prepared_data[config.target_column])
        
        # 4. Sélection et entraînement modèles
        model_results = self._train_forecast_models(prepared_data, config, decomposition)
        
        # 5. Génération prédictions
        forecast_data = self._generate_forecasts(prepared_data, config, model_results)
        
        # 6. Calcul intervalles de confiance
        confidence_intervals = self._calculate_confidence_intervals(
            prepared_data, forecast_data, config, model_results
        )
        
        # 7. Évaluation performance sur données historiques
        model_performance = self._evaluate_model_performance(prepared_data, config, model_results)
        
        # 8. Insights métier
        business_insights = self._generate_forecast_insights(
            prepared_data, forecast_data, decomposition, config
        )
        
        # 9. Explication modèle
        model_explanation = self._explain_forecast_model(model_results, config)
        
        return ForecastResult(
            config=config,
            historical_data=prepared_data,
            forecast_data=forecast_data,
            model_performance=model_performance,
            decomposition=decomposition,
            business_insights=business_insights,
            confidence_intervals=confidence_intervals,
            model_explanation=model_explanation
        )
    
    def _prepare_timeseries_data(self, df: pd.DataFrame, config: ForecastConfig) -> pd.DataFrame:
        """Prépare données pour analyse temporelle"""
        
        data = df.copy()
        
        # Détection colonne date
        date_col = self._detect_date_column(data)
        
        if date_col is None:
            raise ValueError("Aucune colonne de date détectée")
        
        # Conversion et tri
        data[date_col] = pd.to_datetime(data[date_col])
        data = data.sort_values(date_col)
        data.set_index(date_col, inplace=True)
        
        # Vérification colonne target
        if config.target_column not in data.columns:
            raise ValueError(f"Colonne target '{config.target_column}' non trouvée")
        
        # Rééchantillonnage selon fréquence
        if config.frequency:
            # Agrégation par fréquence (somme pour métriques comme revenus, moyenne pour ratios)
            if self._is_additive_metric(config.target_column):
                data_resampled = data.resample(config.frequency)[config.target_column].sum().to_frame()
            else:
                data_resampled = data.resample(config.frequency)[config.target_column].mean().to_frame()
            
            # Ajoute facteurs externes si spécifiés
            for factor in config.external_factors:
                if factor in data.columns:
                    if self._is_additive_metric(factor):
                        data_resampled[factor] = data.resample(config.frequency)[factor].sum()
                    else:
                        data_resampled[factor] = data.resample(config.frequency)[factor].mean()
            
            data = data_resampled
        
        # Nettoyage valeurs manquantes
        data = data.fillna(method='forward').fillna(method='backward')
        
        # Ajout features temporelles
        data = self._add_temporal_features(data)
        
        return data
    
    def _decompose_timeseries(self, data: pd.DataFrame, config: ForecastConfig) -> Dict[str, Any]:
        """Décompose série temporelle en tendance, saisonnalité, résidus"""
        
        target_series = data[config.target_column]
        
        # Détermine période saisonnière principale
        main_period = self._determine_seasonality_period(target_series, config)
        
        if main_period and len(target_series) >= 2 * main_period:
            try:
                # Décomposition STL (plus robuste)
                decomposition = seasonal_decompose(
                    target_series,
                    model='multiplicative',  # ou 'additive'
                    period=main_period,
                    extrapolate_trend='freq'
                )
                
                return {
                    'trend': decomposition.trend,
                    'seasonal': decomposition.seasonal,
                    'residual': decomposition.resid,
                    'period': main_period,
                    'model_type': 'multiplicative',
                    'strength_of_trend': self._calculate_trend_strength(decomposition.trend),
                    'strength_of_seasonality': self._calculate_seasonality_strength(decomposition.seasonal),
                    'residual_autocorr': self._calculate_residual_autocorrelation(decomposition.resid)
                }
                
            except Exception as e:
                logger.warning(f"Décomposition échouée: {e}")
                return self._simple_decomposition(target_series)
        else:
            return self._simple_decomposition(target_series)
    
    def _train_forecast_models(self, data: pd.DataFrame, config: ForecastConfig,
                              decomposition: Dict[str, Any]) -> Dict[str, Any]:
        """Entraîne ensemble de modèles de forecasting"""
        
        target_series = data[config.target_column]
        
        # Préparation features pour modèles ML
        ml_features = self._prepare_ml_features(data, config, decomposition)
        
        # Split train/validation (80/20)
        train_size = int(len(data) * 0.8)
        
        train_data = data.iloc[:train_size]
        val_data = data.iloc[train_size:]
        
        train_target = train_data[config.target_column]
        val_target = val_data[config.target_column]
        
        results = {}
        
        # 1. Modèles ML avec features temporelles
        if len(ml_features) > 0:
            X_train = ml_features.iloc[:train_size]
            X_val = ml_features.iloc[train_size:]
            
            for model_name, model in self.models.items():
                if model_name in ['random_forest', 'gradient_boosting']:
                    try:
                        model.fit(X_train, train_target)
                        val_pred = model.predict(X_val)
                        
                        results[model_name] = {
                            'model': model,
                            'val_predictions': val_pred,
                            'val_mae': mean_absolute_error(val_target, val_pred),
                            'val_rmse': np.sqrt(mean_squared_error(val_target, val_pred)),
                            'val_r2': r2_score(val_target, val_pred),
                            'feature_importance': dict(zip(X_train.columns, model.feature_importances_)) if hasattr(model, 'feature_importances_') else {}
                        }
                    except Exception as e:
                        logger.warning(f"Erreur modèle {model_name}: {e}")
        
        # 2. ARIMA automatique
        try:
            arima_result = self._fit_auto_arima(train_target, val_target)
            if arima_result:
                results['arima'] = arima_result
        except Exception as e:
            logger.warning(f"Erreur ARIMA: {e}")
        
        # 3. Exponential Smoothing
        try:
            exp_smooth_result = self._fit_exponential_smoothing(train_target, val_target, decomposition)
            if exp_smooth_result:
                results['exponential_smoothing'] = exp_smooth_result
        except Exception as e:
            logger.warning(f"Erreur Exponential Smoothing: {e}")
        
        # 4. Modèle ensemble (moyenne pondérée)
        if len(results) > 1:
            ensemble_result = self._create_ensemble_model(results, val_target)
            results['ensemble'] = ensemble_result
        
        # Sélection meilleur modèle
        best_model = self._select_best_model(results)
        results['best_model'] = best_model
        
        return results
    
    def _generate_forecasts(self, data: pd.DataFrame, config: ForecastConfig,
                           model_results: Dict[str, Any]) -> pd.DataFrame:
        """Génère prédictions avec meilleur modèle"""
        
        best_model_name = model_results['best_model']
        best_model_data = model_results[best_model_name]
        
        # Génère index futur
        last_date = data.index[-1]
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(self._get_frequency_delta(config.frequency)),
            periods=config.forecast_horizon,
            freq=config.frequency
        )
        
        # Prédictions selon type de modèle
        if best_model_name in ['random_forest', 'gradient_boosting']:
            # Modèles ML : génère features futures
            future_features = self._generate_future_features(data, config, future_dates)
            predictions = best_model_data['model'].predict(future_features)
            
        elif best_model_name == 'arima':
            # ARIMA : forecast direct
            predictions = best_model_data['model'].forecast(steps=config.forecast_horizon)
            
        elif best_model_name == 'exponential_smoothing':
            # Exponential Smoothing : forecast direct
            predictions = best_model_data['model'].forecast(steps=config.forecast_horizon)
            
        elif best_model_name == 'ensemble':
            # Ensemble : combine prédictions
            predictions = best_model_data['predictions']
        
        else:
            # Fallback : tendance linéaire simple
            predictions = self._linear_trend_forecast(data[config.target_column], config.forecast_horizon)
        
        # Applique contraintes métier
        predictions = self._apply_business_constraints(predictions, config)
        
        # Crée DataFrame résultat
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'forecast': predictions,
            'model_used': best_model_name
        })
        
        forecast_df.set_index('date', inplace=True)
        
        return forecast_df
    
    def _calculate_confidence_intervals(self, data: pd.DataFrame, forecast_df: pd.DataFrame,
                                      config: ForecastConfig, model_results: Dict[str, Any]) -> Dict[float, pd.DataFrame]:
        """Calcule intervalles de confiance pour prédictions"""
        
        intervals = {}
        
        # Utilise résidus du meilleur modèle pour estimation incertitude
        best_model_name = model_results['best_model']
        best_model_data = model_results[best_model_name]
        
        # Calcule erreur standard sur validation
        if 'val_predictions' in best_model_data:
            val_predictions = best_model_data['val_predictions']
            val_actual = data[config.target_column].iloc[-len(val_predictions):]
            residuals = val_actual - val_predictions
            std_error = np.std(residuals)
        else:
            # Estimation basée sur volatilité historique
            returns = data[config.target_column].pct_change().dropna()
            std_error = np.std(returns) * np.mean(data[config.target_column])
        
        # Génère intervalles pour chaque niveau de confiance
        for confidence_level in config.confidence_levels:
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            
            # Ajustement pour horizon (incertitude croît avec distance)
            horizon_factor = np.sqrt(np.arange(1, len(forecast_df) + 1))
            adjusted_std = std_error * horizon_factor
            
            margin_error = z_score * adjusted_std
            
            interval_df = forecast_df.copy()
            interval_df[f'lower_{int(confidence_level*100)}'] = forecast_df['forecast'] - margin_error
            interval_df[f'upper_{int(confidence_level*100)}'] = forecast_df['forecast'] + margin_error
            
            intervals[confidence_level] = interval_df
        
        return intervals
    
    def _generate_forecast_insights(self, historical_data: pd.DataFrame, forecast_data: pd.DataFrame,
                                  decomposition: Dict[str, Any], config: ForecastConfig) -> List[str]:
        """Génère insights métier sur prédictions"""
        
        insights = []
        
        # Analyse tendance prévue
        forecasted_values = forecast_data['forecast']
        current_value = historical_data[config.target_column].iloc[-1]
        forecast_change = (forecasted_values.iloc[-1] - current_value) / current_value
        
        if forecast_change > 0.1:
            insights.append(f"📈 CROISSANCE FORTE prévue: +{forecast_change*100:.1f}% sur {config.forecast_horizon} périodes")
        elif forecast_change > 0.05:
            insights.append(f"📈 Croissance modérée prévue: +{forecast_change*100:.1f}% sur la période")
        elif forecast_change < -0.1:
            insights.append(f"📉 DÉCLIN SIGNIFICATIF prévu: {forecast_change*100:.1f}% sur la période")
        elif forecast_change < -0.05:
            insights.append(f"📉 Baisse modérée prévue: {forecast_change*100:.1f}% sur la période")
        else:
            insights.append(f"➡️ Stabilité prévue avec variation de {forecast_change*100:.1f}%")
        
        # Analyse saisonnalité
        if 'strength_of_seasonality' in decomposition:
            seasonal_strength = decomposition['strength_of_seasonality']
            if seasonal_strength > 0.3:
                insights.append(f"🔄 Saisonnalité FORTE détectée ({seasonal_strength:.1%}) - Prévoir variations cycliques")
            elif seasonal_strength > 0.1:
                insights.append(f"🔄 Saisonnalité modérée ({seasonal_strength:.1%}) - Patterns récurrents visibles")
        
        # Analyse volatilité
        historical_volatility = historical_data[config.target_column].std() / historical_data[config.target_column].mean()
        if historical_volatility > 0.3:
            insights.append(f"⚠️ VOLATILITÉ ÉLEVÉE ({historical_volatility:.1%}) - Prédictions avec incertitude")
        
        # Points d'attention par période
        if config.frequency == 'M':
            insights.append("📅 Prévisions mensuelles - Recommandé de réviser chaque trimestre")
        elif config.frequency == 'W':
            insights.append("📅 Prévisions hebdomadaires - Révision mensuelle conseillée")
        elif config.frequency == 'D':
            insights.append("📅 Prévisions quotidiennes - Révision hebdomadaire recommandée")
        
        # Recommandations actions
        if forecast_change > 0.15:
            insights.append("🎯 ACTION: Préparer montée en charge pour croissance prévue")
        elif forecast_change < -0.15:
            insights.append("🚨 ACTION: Plan de contingence pour baisse prévue")
        
        return insights

# Démonstration du moteur de forecasting
def demo_business_forecasting():
    """Démonstration forecasting métier avancé"""
    
    # Génération série temporelle réaliste
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2025-08-31', freq='D')
    
    # Composants de la série
    n_days = len(dates)
    trend = np.linspace(1000, 1500, n_days)  # Tendance croissante
    seasonality_annual = 200 * np.sin(2 * np.pi * np.arange(n_days) / 365.25)
    seasonality_weekly = 100 * np.sin(2 * np.pi * np.arange(n_days) / 7)
    noise = np.random.normal(0, 50, n_days)
    
    # Série finale
    revenue = trend + seasonality_annual + seasonality_weekly + noise
    
    # Ajout événements spéciaux
    # Black Friday
    black_friday_indices = [i for i, date in enumerate(dates) if date.month == 11 and date.weekday() == 4 and 22 <= date.day <= 28]
    for idx in black_friday_indices:
        revenue[idx] *= 1.8
    
    # Effets COVID (simulation baisse 2024)
    covid_start = (pd.Timestamp('2024-03-01') - dates[0]).days
    covid_end = (pd.Timestamp('2024-06-01') - dates[0]).days
    if covid_start >= 0 and covid_end < len(revenue):
        revenue[covid_start:covid_end] *= 0.7
    
    # DataFrame
    df = pd.DataFrame({
        'date': dates,
        'revenue': revenue,
        'marketing_spend': np.random.normal(200, 50, n_days),
        'orders_count': revenue / np.random.normal(25, 5, n_days)
    })
    
    print("🔮 DÉMONSTRATION FORECASTING MÉTIER AVANCÉ")
    print("=" * 60)
    
    # Configuration forecasting
    config = ForecastConfig(
        target_column='revenue',
        forecast_horizon=90,  # 3 mois
        frequency='D',
        seasonality_periods=[7, 365],
        confidence_levels=[0.80, 0.95],
        external_factors=['marketing_spend'],
        business_constraints={
            'min_value': 0,
            'max_growth_rate': 0.5  # Max 50% growth
        }
    )
    
    # Initialisation moteur
    engine = BusinessForecastingEngine()
    
    # Forecasting complet
    result = engine.forecast_timeseries(df, config)
    
    # Affichage résultats
    print(f"\n📊 PERFORMANCE MODÈLES:")
    best_model = result.model_performance['best_model']
    perf = result.model_performance[best_model]
    
    print(f"• Meilleur modèle: {best_model}")
    print(f"• MAE: {perf['val_mae']:.2f}")
    print(f"• RMSE: {perf['val_rmse']:.2f}")
    print(f"• R²: {perf.get('val_r2', 'N/A')}")
    
    print(f"\n🔍 DÉCOMPOSITION SÉRIE:")
    decomp = result.decomposition
    print(f"• Force tendance: {decomp.get('strength_of_trend', 'N/A'):.1%}")
    print(f"• Force saisonnalité: {decomp.get('strength_of_seasonality', 'N/A'):.1%}")
    print(f"• Période saisonnière: {decomp.get('period', 'N/A')}")
    
    print(f"\n🎯 PRÉVISIONS CLÉS:")
    forecast_values = result.forecast_data['forecast']
    current_value = result.historical_data[config.target_column].iloc[-1]
    
    print(f"• Valeur actuelle: {current_value:,.0f}")
    print(f"• Prévision J+30: {forecast_values.iloc[29]:,.0f}")
    print(f"• Prévision J+90: {forecast_values.iloc[89]:,.0f}")
    
    # Intervalles confiance
    conf_80 = result.confidence_intervals[0.80]
    print(f"• Intervalle 80% J+90: [{conf_80.iloc[89]['lower_80']:,.0f}, {conf_80.iloc[89]['upper_80']:,.0f}]")
    
    print(f"\n💡 INSIGHTS MÉTIER:")
    for insight in result.business_insights:
        print(f"• {insight}")
    
    print(f"\n🔧 EXPLICATION MODÈLE:")
    explanation = result.model_explanation
    if 'feature_importance' in explanation:
        print("• Features les plus importantes:")
        for feature, importance in list(explanation['feature_importance'].items())[:3]:
            print(f"  - {feature}: {importance:.3f}")
    
    return result

if __name__ == "__main__":
    result = demo_business_forecasting()
```

Cette implémentation avancée de data science métier offre :

✅ **Analytics exploratoire automatisé** avec détection d'insights business
✅ **Forecasting sophistiqué** avec ensemble de modèles (ARIMA, ML, Exponential Smoothing)
✅ **Décomposition saisonnière** et détection de patterns temporels
✅ **Intervalles de confiance** et évaluation d'incertitude
✅ **Visualisations interactives** générées automatiquement
✅ **Recommandations d'actions** basées sur analyses
✅ **Détection d'anomalies** et outliers métier
✅ **Clustering intelligent** pour segmentation
✅ **Métriques de qualité** des données avec évaluation business

Le système transforme automatiquement les données brutes en insights actionnables pour les équipes métier.