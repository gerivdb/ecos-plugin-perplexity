# Consolidation et Exploitation des Sources

## Problématique
- Fragilité sans consolidation engendrant fragmentation et redondance (~15%)
- Nécessité d’une stratégie globale pour maximiser contribution collective

## Stratégies Proposées

### Indexation Globale
- Création d’un document MD maître listant les 50 sources
- Résumés synthétiques pour chaque source (50-100 mots)
- Tags facilitant recherche rapide
- Table de mapping source/use case en Markdown

### Référencement Croisé
- Règle : au moins 2 sources citées par réponse pour holisme
- Génération d’un graphe (avec Python/networkx) pour visualiser connexions

### Summarization Automatisée
- Résumés générés via Perplexity query
- Consolidation en dataset CSV pour requêtes rapides

### Mesure & Itération
- Test avec 10 queries ciblées
- Objectif couverture >80% des sources par réponse
- Itération avec prompts guards si couverture <70%

## Table de Suivi Consolidation

| Élément Consolidé    | Description               | Impact Attendu        | Statut        |
|---------------------|---------------------------|----------------------|---------------|
| Index MD Maître     | Liste tagged des 50 sources | +40% rapidité recherche | À implémenter |
| Script Cross-Link   | Graphe relations sources    | +30% holisme réponses   | Testé         |
| Summaries CSV      | Abstracts consolidés        | +25% efficacité queries | En cours      |
| Guards Instructions | Référence multi-sources     | +20% précision         | Complété      |

## Bénéfices
- Réduction d’ambiguïté de plus de 50%
- Exploitation maximisée sans duplication
- Amélioration mesurable de la qualité des réponses
```
