# STRATUM RELAY — ecos-plugin-perplexity (L3)

**VAGUE**: 4 | **Synchro**: 2026-05-30 | **Hub**: gerivdb/LLM-REPO

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

## Agents locaux (Vague 4)

```yaml
# .roomodes — profil agent ecos-plugin-perplexity
agent: perplexity-bridge
strate: L3
role: Perplexity/SuperMemory plugin
rules: ecos-plugin-perplexity/rules/plugin_rules.yaml
hub_ref: ECOS-CLI
```

L'agent `perplexity-bridge` etend ECOS-CLI avec les capacites Perplexity et SuperMemory, gere l'Intent Hash, et synchronise Notion.

## Auto-conformite (Vague 4)

- **Guard 1 — Plugin-only access** : L'API Perplexity n'est jamais appelee directement. Tout passe par le plugin.
- **Guard 2 — Rate limit compliance** : Le plugin respecte strictement les limites de taux de l'API Perplexity.
- **Guard 3 — Cache before call** : Avant chaque appel API, le cache est consulte. Pas de requete redondante.

## Vague de mise a jour

| Vague | Contenu | Statut |
|-------|---------|--------|
| 2 | Identite + regles + Karpathy-Recall 5Q | Deploye |
| 3 | Recall etendu a 10Q + section Dependances | Deploye |
| **4 (courante)** | Agents locaux + auto-conformite | Deploye |

---

*Genere par `VERSUS/urban_ontology_verse/TOOLS/relay_propagator.py` v4.0*
*UrbanVerse v4.0.0 — gerivdb/VERSUS (L8)*
*IntentHash: 0xPHASE8_PERPLEXITY_V4_20260530*