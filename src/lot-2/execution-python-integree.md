
# Exploitation de l’Exécution Python Intégrée dans Perplexity AI

## Capacités de l’Environnement Python

Les espaces Perplexity AI intègrent un environnement Python **persistant** qui simule un notebook Jupyter simplifié, offrant une puissance d’analyse avancée :

- Maintien des **variables entre exécutions** successives
- Accès aux principales bibliothèques data science : **pandas**, **numpy**, **json**, etc.
- Limite d’exécution fixée à **30 secondes** pour éviter les blocages
- Capacité à lire, traiter et écrire des **fichiers**
- Analyse et calculs **en temps réel**

## Utilisations Typiques

- Analyse automatique de fichiers uploadés (CSV, JSON, Excel)
- Extraction et transformation des données brutes
- Synthèse et scoring des sources par critères dynamiques
- Génération de rapports textuels ou numériques en automatisé
- Filtrage avancé et création de tableaux adaptés

## Exemple Pratique : Analyse et Scoring Basique des Sources

```
import pandas as pd
from datetime import datetime
import numpy as np

def score_sources(data):
    df = pd.DataFrame(data)
    current_year = datetime.now().year
    # Calcul score fraîcheur : décroit avec l'âge (0 si > 10 ans)
    df['freshness'] = np.maximum(0, 10 - (current_year - df['year']))
    # Score final : pondération example (pertinence 0.5, fraîcheur 0.3, diversité 0.2)
    df['score'] = (0.5 * df['relevance']) + (0.3 * df['freshness']) + (0.2 * df['diversity'])
    return df.sort_values('score', ascending=False)

# Exemple d’entrée :
sources = [
    {"relevance": 0.9, "year": 2024, "diversity": 1},
    {"relevance": 0.8, "year": 2020, "diversity": 0.8},
    # plus de données ici
]

resultat = score_sources(sources)
print(resultat)
```

## Limitations et Bonnes Pratiques

- Pas de visualisations graphiques natives (matplotlib, seaborn non supportés en natif)
- Timeout strict : privilégier les traitements fractionnés et optimisés
- Pas d’interface notebook visuelle, uniquement textuelle
- Importance de modulariser les scripts pour facilité maintenance

---

*À venir : Orchestration multi-modèles avec Pro Search et gestion avancée des Spaces.*

---
```
