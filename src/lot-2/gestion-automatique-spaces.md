# Gestion Automatisée et Collaborative des Spaces dans Perplexity AI

## Introduction aux Spaces

Les **Spaces** (anciennement Collections) sont des environnements personnalisés pour organiser, collaborer et analyser des ensembles de données et documents. Ils permettent le travail collaboratif et l’application d’instructions IA spécifiques par espace [23][49][51].

## Capacités techniques

- **Jusqu’à 50 fichiers** uploadés par Space (taille max 25MB chacun) [23][60]
- **Formats supportés** :
  - Documents : PDF, DOCX, PPTX, TXT, code source
  - Audio/Vidéo : MP3, WAV, MP4, MOV, WebM, etc.
  - Images : JPEG, PNG, HEIC (jusqu’à 40MB)
- **Collaboration** : jusqu’à 10 utilisateurs simultanés avec gestion des permissions [23]
- **Instructions personnalisées** : prompts spécifiques à chaque Space pour orienter les recherches et analyses

## Automatisation via Python

- **Chargement scripté** de fichiers multiples et leur indexation automatique
- **Application automatique d’instructions IA** (exemples : classification, tagging)
- **Traitement et synthèse intelligente** des contenus uploadés pour veiller à l’exhaustivité
- **Génération automatique de rapports consolidés** résumant les contenus du Space

## Exemple de script Python simple pour uploader et paramétrer un Space

```
def preparer_space(fichiers, instructions, utilisateurs):
    space = {
        "files": fichiers,
        "custom_instructions": instructions,
        "collaboration": {"users": utilisateurs, "permissions": ["read", "write"]}
    }
    # Appel API Perplexity pour créer/configurer le Space
    # response = api_client.create_space(space)
    # return response
```

## Bonnes pratiques

- Organiser les fichiers par catégorie/thématique pour optimiser la recherche
- Utiliser des instructions IA adaptées aux besoins métiers
- Synchroniser les modifications avec l’ensemble des collaborateurs
- Automatiser la mise à jour des Spaces via pipelines Python réguliers

---

*Le prochain document portera sur la génération, optimisation et publication automatisées des Pages.*

---
```
