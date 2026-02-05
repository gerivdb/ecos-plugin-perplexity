# Orchestration Multi-Modèles avec Pro Search dans Perplexity AI

## Introduction à Pro Search

Pro Search est une fonctionnalité avancée de Perplexity AI qui permet de résoudre des questions complexes par un raisonnement multi-étapes. Il combine plusieurs modèles IA pour effectuer des recherches parallèles et synthétiser des réponses précises et détaillées.

## Fonctionnalités

- Découpage automatique des questions complexes en sous-questions plus simples
- Recherche simultanée avec différents modèles (GPT-5, Claude 4.0, Sonar Large, Gemini 2.5 Pro)
- Synthèse et agrégation des résultats avec citations transparentes
- Intégration de calculs complexes via Wolfram Alpha

## Exemple d’orchestration Python asynchrone

```
import asyncio

async def interroger_modele(modele, question, client_api):
    reponse = await client_api.ask(model=modele, query=question)
    return reponse

async def orchestration(questions, modeles, client_api):
    taches = []
    for q, m in zip(questions, modeles):
        taches.append(interroger_modele(m, q, client_api))
    resultats = await asyncio.gather(*taches)
    return resultats

# Exemples de questions et modèles
questions = [
    "Quels sont les défis énergétiques en Europe post-2020 ?",
    "Quelle est la tendance des véhicules électriques en 2025 ?"
]
modeles = ["GPT-5", "Claude 4.0"]

# client_api doit être initialisé selon SDK Perplexity/OpenAI
# resultats = asyncio.run(orchestration(questions, modeles, client_api))
# print(resultats)
```

## Bénéfices

- Amélioration de la précision par recoupement multi-modèles
- Réduction du temps d’attente par exécution parallèle
- Possibilité d’automatiser le suivi itératif des réponses

---

*Prochain fichier : Gestion et automatisation des Spaces.*

---
```
