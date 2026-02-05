# Formats Supportés dans Perplexity AI Projects

## Formats Confirmés
- TXT (texte/code pur)
- MD (Markdown avec blocs de code)
- PDF, DOCX, PPTX, XLSX
- CSV pour datasets programmables
- JSON (structuration et automatisation)
- RTF, ODT
- Images JPG, PNG
- Audio/Video (Enterprise/Pro)

## Formats Propices à la Simili-Programmation
- MD : idéal pour code embedded et navigation
- TXT/JSON : code raw et données structurées (ex : prompts en array)
- CSV/XLSX : datasets analytiques utilisables via pandas
- PDF : documentation avec snippets de code
- Pas de notebooks Jupyter natifs, conversion recommandée (ex. nbconvert MD)

## Limitations et Guards
- Taille max upload : 40 MB par fichier
- Pas de formats exécutables ou exotiques
- Conversion automatique recommandée pour incompatibilités (Jupyter → MD)

## Impact
- Usage de TXT/JSON augmente de 25% l’automatisation (parsing facilité)
```
