# STRATUM RELAY — ecos-plugin-perplexity (L3)

**VAGUE**: 3 | **Synchro**: 2026-05-29 | **Hub**: gerivdb/LLM-REPO

- **Strate** : `L3` — Systeme moteur CLI
- **Role canonique** : Plugin Perplexity/SuperMemory pour ECOS-CLI — Intent Hash, Notion sync
- **Parent** : L2 (ECOS-CLI)

## Regles locales
- R1 — ecos-plugin-perplexity etend ECOS-CLI avec Perplexity et SuperMemory.
- R2 — Intent Hash et Notion sync sont geres par ce plugin.
- Anti-pattern: utiliser l'API Perplexity directement sans passer par le plugin.

## Karpathy-Recall local (Vague 3 — 10Q)
1. Quel est le role d'ecos-plugin-perplexity ?
2. Pourquoi Intent Hash est-il important dans l'ecosysteme ?
3. Quelle est la difference entre ce plugin et OPENCLAW-CLI ?
4. Pourquoi ne pas utiliser l'API Perplexity directement ?
5. Dans quelle phase UrbanVerse ce STRATUM_RELAY a-t-il ete deploye ?
6. Comment ecos-plugin-perplexity genere-t-il l'Intent Hash et quel est le format de sortie ?
7. Quelles commandes SuperMemory le plugin expose-t-il et comment les invoquer ?
8. Comment le plugin synchronise-t-il les donnes avec Notion (webhooks, polling, push) ?
9. Comment ecos-plugin-perplexity gere-t-il les taux limites (rate limiting) de l'API Perplexity ?
10. Quels sont les modes de cache du plugin et comment eviter les requetes API redondantes ?

## Dependances directes

- **Parent (amont)** : ECOS-CLI (L3) — ecos-plugin-perplexity s'installe en tant que plugin d'extension d'ECOS-CLI.
- **Enfants (aval)** : Aucun — le plugin est une extension terminale d'ECOS-CLI sans enfants directs.

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| 2 | Identite + regles + Karpathy-Recall 5Q | Deploye |
| **3 (courante)** | Recall etendu a 10Q + section Dependances | Deploye |
| 4 (suivante) | Cache multi-niveaux + sync temps reel Notion | Planifie |
