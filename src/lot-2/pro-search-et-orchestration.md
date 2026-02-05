# Orchestration Avancée avec Pro Search et IA Multi-Modèles dans Perplexity AI

## Présentation de Pro Search

**Pro Search** offre un raisonnement multi-étapes permettant de traiter des questions complexes en plusieurs sous-problèmes distincts. Ce mode utilise des modèles multiples (GPT-5, Claude 4.0, Sonar Large, Gemini 2.5 Pro) pour une exploration approfondie [12][45][48].

### Fonctionnalités clés :

- Découpage automatique des questions complexes en tâches plus simples
- Recherche parallèle sur **3x plus de sources** que Quick Search
- Agrégation et synthèse cohérente des résultats multiples
- Citations précises et transparence des sources

## Workflow d’orchestration Python

1. **Décomposez la question globale** en plusieurs sous-questions adressées à différents modèles ou focus modes.
2. **Lancez les requêtes en parallèle** via API en Python, avec gestion asynchrone.
3. **Collectez et normalisez** les réponses, détectez contradictions ou chevauchements.
4. **Synthétisez un rapport final** avec pondération des sources et des réponses.
5. **Suivez automatiquement** les questions complémentaires générées par le système.

## Exemple simplifié de script Python pour orchestrer des requêtes Pro Search

```
import asyncio

async def query_model_async(model_name, question, api_client):
    response = await api_client.ask(model=model_name, query=question)
    return response

async def orchestrate_queries(questions, models, api_client):
    tasks = []
    for q, m in zip(questions, models):
        tasks.append(query_model_async(m, q, api_client))
    results = await asyncio.gather(*tasks)
    return results

# Exemple d'utilisation
questions = [
    "Quels sont les défis énergétiques en Europe post-2020 ?",
    "Quelle est la tendance des véhicules électriques en 2025 ?"
]
models = ["GPT-5", "Claude 4.0"]

# api_client doit être initialisé selon SDK Perplexity/ OpenAI
# results = asyncio.run(orchestrate_queries(questions, models, api_client))
# print(results)
```

## Intégrations complémentaires

- **Wolfram Alpha** pour calculs mathématiques avancés intégrés dans certaines requêtes [53].
- **Suivi algo** des requêtes itératives via Threads pour approfondissement systématique.

---

*Prochain sujet : Gestion automatisée et collaborative des Spaces.*

---
```