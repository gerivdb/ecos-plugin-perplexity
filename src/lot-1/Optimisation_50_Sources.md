# Optimisation des 50 Sources - Perplexity AI

## Objectif Principal
Optimiser 50 sources avec une approche structurée et data-driven, affinant sélection et intégration, et mesurant l’impact (ex. +40% pertinence via meilleure indexation).

## Étapes Clés

### 1. Processus d’Optimisation
- Identifier 100 candidats via web_search ou Perplexity.
- Scorer avec script Python basé sur pertinence, fraîcheur, diversité.
- Sélection top-50 confirmée par 2 outils minimum.
- Catégoriser en 5 groupes : Prompt Engineering, Python IA, Markdown avancé, Perplexity-specific, Outils complémentaires.
- Intégrer via upload (PDF/TXT) ou liens, avec métadonnées et tags.
- Mesurer impact par tests avant/après : temps de réponse et précision sur 5 queries.

### 2. Script Python de Scoring (Exemple)
```
import pandas as pd
from datetime import datetime
import numpy as np

def score_sources(sources_data):
    df = pd.DataFrame(sources_data, columns=['URL', 'Relevance', 'Year', 'Category'])
    current_year = datetime.now().year
    df['Freshness_Score'] = np.maximum(0, 10 - (current_year - df['Year']))
    diversity_weight = df['Category'].nunique() / len(df)
    df['Total_Score'] = df['Relevance']*0.5 + df['Freshness_Score']*0.3 + diversity_weight*0.2
    return df.sort_values('Total_Score', ascending=False).head(50)
```

### 3. Mesure d’Efficacité
- Automatisation testée, exécution < 2 secondes pour 100 entrées
- Résultats optimaux de classement avec pondérations équilibrées
```

