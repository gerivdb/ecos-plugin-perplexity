# Tutoriel Python : Analyse et Scoring des Sources pour Perplexity AI

## Introduction
Ce tutoriel guide pas à pas la mise en place d’un script Python pour analyser, scorer et classer des sources selon des critères pertinence, fraîcheur et diversité dans un espace Projet Perplexity AI.

## Prérequis
- Python 3.x installé
- Bibliothèques : pandas, numpy (installation via pip si besoin)

```
pip install pandas numpy
```

## Étape 1 : Préparation des données
Préparez vos données sous forme d’une liste de tuples ou un CSV avec les colonnes suivantes : URL, Relevance (score entre 0 et 1), Year (année de publication), Category (catégorie thématique).

Exemple :
```
sources_data = [
    ('https://arxiv.org/abs/2303.08774', 0.95, 2023, 'Prompt Eng'),
    ('https://github.com/huggingface/transformers', 0.90, 2024, 'Python IA'),
    ('https://www.markdownguide.org', 0.85, 2022, 'Markdown'),
]
```

## Étape 2 : Script de scoring

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

# Exemple d’utilisation
result = score_sources(sources_data)
print(result)
```

## Étape 3 : Interprétation des résultats
Le tableau retourné classe les sources selon un score total combiné, favorisant pertinence, fraîcheur et diversité. Les 50 meilleures sources sont sélectionnées pour intégration.

## Conseils
- Adaptez les pondérations dans la fonction selon vos priorités.
- Intégrez ces scripts dans un pipeline d’import automatique pour scalabilité.
- Utilisez des visualisations (ex. matplotlib) pour illustrer les scores si besoin.

## Conclusion
Ce tutoriel facilite une gestion automatisée, rigoureuse et évolutive des sources, essentielle à la réussite du projet Perplexity AI.
```
