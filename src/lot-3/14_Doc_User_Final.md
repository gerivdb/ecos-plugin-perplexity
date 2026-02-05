# Documentation Utilisateur Final - Espace Métier Perplexity AI

## Vue d'ensemble
Ce guide complet accompagne les utilisateurs métier dans l'utilisation quotidienne de l'espace Perplexity AI, avec des exemples concrets, des bonnes pratiques et des solutions aux problèmes courants.

## Guide de Démarrage Rapide

### Première Connexion

#### Accès à la Plateforme
1. **URL de connexion** : `https://metier.perplexity.ai`
2. **Identifiants** : Fournis par votre administrateur
3. **Navigateurs supportés** : Chrome (recommandé), Firefox, Safari, Edge

#### Interface Principale
```
┌─────────────────────────────────────────────────────────────────┐
│ 🏠 Perplexity AI Métier          👤 Jean Dupont    🔔 📊 ⚙️    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Dashboard      📝 Scripts      🔗 APIs      📈 Analyses     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    ESPACE DE TRAVAIL                       │ │
│  │                                                             │ │
│  │         Contenu dynamique selon section active             │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  💡 Conseils    📚 Documentation    🎯 Formations    💬 Support │
└─────────────────────────────────────────────────────────────────┘
```

### Navigation et Zones Clés

#### Barre de Navigation Principale
- **🏠 Accueil** : Dashboard et vue d'ensemble
- **📝 Scripts** : Création et gestion de scripts Python
- **🔗 APIs** : Configuration intégrations externes
- **📈 Analyses** : Rapports et visualisations
- **⚙️ Paramètres** : Configuration personnelle

#### Zone de Travail Contextuelle
- S'adapte selon la section active
- Outils et actions pertinents toujours visibles
- Historique et favoris accessibles

## Utilisation des Scripts Python

### Création de votre Premier Script

#### Étape 1 : Accès à l'Éditeur
1. Cliquez sur **📝 Scripts** dans le menu
2. Bouton **➕ Nouveau Script**
3. Choisissez un **modèle** ou partez de zéro

#### Étape 2 : Configuration de Base
```python
# Template automatique généré
"""
Script métier Perplexity AI
Nom: Mon Premier Script
Auteur: Jean Dupont
Date: 2025-09-02
"""

# 🎯 OBJECTIF DE CE SCRIPT
# Décrivez ici ce que fait votre script
# Exemple : Analyse des prix concurrents et recommandations pricing

# 📥 DONNÉES D'ENTRÉE ATTENDUES
# Spécifiez le format des données que vous allez traiter
# Exemple : Liste de dictionnaires avec 'produit', 'prix', 'concurrent'

# 📊 ÉTAPES PRINCIPALES
def analyser_donnees(donnees_entree):
    """
    Fonction principale d'analyse
    
    Args:
        donnees_entree (list): Données à analyser
        
    Returns:
        dict: Résultats de l'analyse
    """
    
    # 🔍 1. VALIDATION DES DONNÉES
    if not donnees_entree:
        return {"erreur": "Aucune donnée fournie"}
    
    # 📈 2. TRAITEMENT
    resultats = {}
    
    # Votre logique métier ici
    # Exemple simple : calcul moyenne prix
    prix = [item.get('prix', 0) for item in donnees_entree if 'prix' in item]
    
    if prix:
        resultats['prix_moyen'] = sum(prix) / len(prix)
        resultats['prix_min'] = min(prix)
        resultats['prix_max'] = max(prix)
        resultats['nb_produits'] = len(prix)
    
    # 💡 3. RECOMMANDATIONS
    if 'prix_moyen' in resultats:
        if resultats['prix_moyen'] > 100:
            resultats['recommandation'] = "Prix élevés - Vérifier positionnement"
        else:
            resultats['recommandation'] = "Prix compétitifs"
    
    return resultats

# 🚀 POINT D'ENTRÉE
# Cette section s'exécute quand le script est lancé
if __name__ == "__main__":
    # Exemple de données test
    donnees_test = [
        {'produit': 'A', 'prix': 99.99, 'concurrent': 'Comp1'},
        {'produit': 'B', 'prix': 149.50, 'concurrent': 'Comp2'},
        {'produit': 'C', 'prix': 89.90, 'concurrent': 'Comp1'}
    ]
    
    # Exécution analyse
    resultats = analyser_donnees(donnees_test)
    
    # Affichage résultats
    print("📊 RÉSULTATS DE L'ANALYSE")
    print("=" * 30)
    
    for cle, valeur in resultats.items():
        print(f"{cle}: {valeur}")
    
    print("\n✅ Analyse terminée avec succès!")
```

#### Étape 3 : Test et Validation

**🧪 Mode Test**
1. Cliquez sur **▶️ Tester** dans l'éditeur
2. Fournissez des données exemple dans la zone dédiée
3. Vérifiez les résultats dans l'onglet sortie

**📋 Exemple de Données Test**
```json
[
  {
    "produit": "Ordinateur Portable XYZ",
    "prix": 899.99,
    "concurrent": "TechMart",
    "date": "2025-09-02"
  },
  {
    "produit": "Ordinateur Portable XYZ", 
    "prix": 929.00,
    "concurrent": "ElectroPlus",
    "date": "2025-09-02"
  }
]
```

**✅ Validation Automatique**
- Vérification syntaxe Python
- Tests sécurité (imports dangereux détectés)
- Estimation temps d'exécution
- Validation format données

### Scripts Métier Pré-configurés

#### 💰 Scripts Pricing
```python
# Template : Analyse Pricing Concurrentiel
import pandas as pd
import numpy as np
from datetime import datetime

def analyser_prix_concurrents(donnees_prix, notre_prix_actuel, marge_min=0.15):
    """
    Analyse complète du pricing concurrentiel
    
    📊 Fonctionnalités :
    - Positionnement vs concurrence
    - Recommandations pricing
    - Alertes sur écarts significatifs
    - Calcul impact marge
    """
    
    df = pd.DataFrame(donnees_prix)
    
    # Statistiques concurrence
    stats = {
        'prix_moyen_marche': df['prix'].mean(),
        'prix_median_marche': df['prix'].median(),
        'prix_min_marche': df['prix'].min(),
        'prix_max_marche': df['prix'].max(),
        'nombre_concurrents': len(df),
        'ecart_type': df['prix'].std()
    }
    
    # Position concurrentielle
    position = 'milieu'
    if notre_prix_actuel <= stats['prix_min_marche']:
        position = 'leader_prix'
    elif notre_prix_actuel >= stats['prix_max_marche']:
        position = 'premium'
    
    # Recommandations
    recommandations = []
    prix_recommande = notre_prix_actuel
    
    # Si trop au-dessus du marché
    if notre_prix_actuel > stats['prix_moyen_marche'] * 1.2:
        prix_recommande = stats['prix_moyen_marche'] * 1.1
        recommandations.append({
            'type': 'baisse_prix',
            'message': f'Prix actuel {notre_prix_actuel}€ trop élevé vs marché',
            'action': f'Recommandation: {prix_recommande:.2f}€'
        })
    
    # Si opportunité de hausse
    elif notre_prix_actuel < stats['prix_moyen_marche'] * 0.9:
        prix_recommande = stats['prix_moyen_marche'] * 0.95
        recommandations.append({
            'type': 'hausse_prix',
            'message': f'Opportunité hausse prix détectée',
            'action': f'Recommandation: {prix_recommande:.2f}€'
        })
    
    # Validation marge
    if prix_recommande < notre_prix_actuel * (1 + marge_min):
        recommandations.append({
            'type': 'alerte_marge',
            'message': f'Attention: marge minimum {marge_min*100}% non respectée',
            'action': 'Vérifier coûts et rentabilité'
        })
    
    return {
        'statistiques_marche': stats,
        'position_concurrentielle': position,
        'prix_recommande': prix_recommande,
        'recommandations': recommandations,
        'derniere_analyse': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

# 🎯 UTILISATION
donnees_exemple = [
    {'concurrent': 'CompA', 'prix': 89.90, 'produit': 'Widget Pro'},
    {'concurrent': 'CompB', 'prix': 94.50, 'produit': 'Widget Pro'},
    {'concurrent': 'CompC', 'prix': 87.00, 'produit': 'Widget Pro'},
]

resultats = analyser_prix_concurrents(donnees_exemple, notre_prix_actuel=99.00)
```

#### 🏨 Scripts Booking Hôtelier
```python
# Template : Optimisation Taux d'Occupation
import pandas as pd
from datetime import datetime, timedelta

def optimiser_tarification_dynamique(reservations, capacite_totale, horizon_jours=30):
    """
    Système de tarification dynamique basé sur l'occupation
    
    📊 Analyse :
    - Taux d'occupation par période
    - Tendances de réservation
    - Prix recommandés par segment
    - Alertes sur périodes creuses
    """
    
    df = pd.DataFrame(reservations)
    df['date_arrivee'] = pd.to_datetime(df['date_arrivee'])
    df['date_depart'] = pd.to_datetime(df['date_depart'])
    
    # Calcul occupation quotidienne
    date_debut = datetime.now().date()
    date_fin = date_debut + timedelta(days=horizon_jours)
    
    occupation_quotidienne = []
    
    for i in range(horizon_jours):
        date_courante = date_debut + timedelta(days=i)
        
        # Réservations pour cette date
        reservations_date = df[
            (df['date_arrivee'].dt.date <= date_courante) &
            (df['date_depart'].dt.date > date_courante)
        ]
        
        chambres_occupees = reservations_date['nb_chambres'].sum()
        taux_occupation = (chambres_occupees / capacite_totale) * 100
        
        occupation_quotidienne.append({
            'date': date_courante.strftime('%Y-%m-%d'),
            'jour_semaine': date_courante.strftime('%A'),
            'chambres_occupees': chambres_occupees,
            'taux_occupation': taux_occupation,
            'chambres_disponibles': capacite_totale - chambres_occupees
        })
    
    # Recommandations tarifaires
    recommandations = []
    
    for jour in occupation_quotidienne:
        taux = jour['taux_occupation']
        
        if taux < 30:
            # Occupation faible - baisse prix
            recommandations.append({
                'date': jour['date'],
                'action': 'reduction_prix',
                'pourcentage': -15,
                'raison': f'Taux occupation faible ({taux:.1f}%)'
            })
        elif taux > 85:
            # Occupation élevée - hausse prix
            recommandations.append({
                'date': jour['date'],
                'action': 'hausse_prix',
                'pourcentage': 20,
                'raison': f'Forte demande ({taux:.1f}%)'
            })
        elif taux > 70:
            # Occupation bonne - hausse modérée
            recommandations.append({
                'date': jour['date'],
                'action': 'hausse_prix',
                'pourcentage': 10,
                'raison': f'Demande soutenue ({taux:.1f}%)'
            })
    
    # Statistiques générales
    taux_moyen = sum([j['taux_occupation'] for j in occupation_quotidienne]) / len(occupation_quotidienne)
    
    alertes = []
    if taux_moyen < 40:
        alertes.append('Taux occupation général faible - Revoir stratégie marketing')
    
    # Détection patterns week-end
    taux_weekend = []
    taux_semaine = []
    
    for jour in occupation_quotidienne:
        if jour['jour_semaine'] in ['Friday', 'Saturday', 'Sunday']:
            taux_weekend.append(jour['taux_occupation'])
        else:
            taux_semaine.append(jour['taux_occupation'])
    
    if taux_weekend and taux_semaine:
        if sum(taux_weekend)/len(taux_weekend) < sum(taux_semaine)/len(taux_semaine):
            alertes.append('Occupation week-ends plus faible que semaine')
    
    return {
        'occupation_quotidienne': occupation_quotidienne,
        'taux_occupation_moyen': taux_moyen,
        'recommandations_tarifaires': recommandations,
        'alertes': alertes,
        'horizon_analyse': f'{horizon_jours} jours',
        'capacite_totale': capacite_totale
    }

# 🎯 EXEMPLE D'UTILISATION
reservations_exemple = [
    {'date_arrivee': '2025-09-03', 'date_depart': '2025-09-05', 'nb_chambres': 2, 'type': 'standard'},
    {'date_arrivee': '2025-09-04', 'date_depart': '2025-09-07', 'nb_chambres': 1, 'type': 'suite'},
    {'date_arrivee': '2025-09-10', 'date_depart': '2025-09-12', 'nb_chambres': 3, 'type': 'standard'},
]

resultats = optimiser_tarification_dynamique(reservations_exemple, capacite_totale=20)
```

### Bonnes Pratiques Scripts

#### ✅ Code de Qualité

**🏗️ Structure Recommandée**
```python
"""
Script : [Nom Explicite]
Objectif : [Description claire]
Auteur : [Nom]
Version : 1.0
Dernière MAJ : [Date]

Données d'entrée :
- Format attendu
- Champs obligatoires
- Exemples

Données de sortie :
- Structure résultat
- Métriques calculées
- Actions recommandées
"""

# 1️⃣ IMPORTS ET CONFIGURATION
import pandas as pd  # ✅ Autorisé
import numpy as np   # ✅ Autorisé
from datetime import datetime, timedelta  # ✅ Autorisé

# Configuration
SEUIL_ALERTE = 0.1
MARGE_SECURITE = 0.05

# 2️⃣ FONCTIONS UTILITAIRES
def valider_donnees(donnees):
    """Valide format et cohérence des données d'entrée"""
    if not isinstance(donnees, list):
        raise ValueError("Données doivent être une liste")
    
    for item in donnees:
        if not isinstance(item, dict):
            raise ValueError("Chaque élément doit être un dictionnaire")
    
    return True

def calculer_statistiques(valeurs):
    """Calcule statistiques descriptives"""
    if not valeurs:
        return {}
    
    return {
        'moyenne': sum(valeurs) / len(valeurs),
        'mediane': sorted(valeurs)[len(valeurs)//2],
        'minimum': min(valeurs),
        'maximum': max(valeurs),
        'count': len(valeurs)
    }

# 3️⃣ FONCTION PRINCIPALE
def traitement_principal(donnees_entree):
    """Logique métier principale - bien documentée"""
    
    # Validation
    valider_donnees(donnees_entree)
    
    # Traitement
    resultats = {}
    
    # ... votre logique ici ...
    
    return resultats

# 4️⃣ EXECUTION ET TESTS
if __name__ == "__main__":
    # Données de test
    test_data = [
        # Vos données exemple
    ]
    
    try:
        resultats = traitement_principal(test_data)
        print("✅ Traitement réussi")
        print(f"Résultats: {resultats}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
```

**🚫 À Éviter - Erreurs Courantes**
```python
# ❌ Mauvaises pratiques

# Imports dangereux (bloqués par sécurité)
import os           # ❌ Bloqué
import subprocess   # ❌ Bloqué  
import requests     # ❌ Non disponible (utiliser APIs configurées)

# Code non structuré
prix = [89, 95, 92]  # ❌ Variables globales peu claires
resultat = sum(prix) / len(prix)  # ❌ Logique directe sans fonction

# Pas de gestion d'erreur
donnees[0]['prix']  # ❌ Crash si données vides ou mal formées

# Variables mal nommées
x = donnees  # ❌ Nom peu explicite
y = []       # ❌ Purpose non claire

# Pas de documentation
def calcul(a, b):  # ❌ Pas de docstring
    return a + b

# Logique complexe sans commentaires
# ❌ Code difficile à comprendre sans explication
if sum([x['p'] for x in d if 'p' in x]) / len([x for x in d if 'p' in x]) > 100:
    return True
```

## Intégration APIs Externes

### Configuration d'une Nouvelle API

#### Étape 1 : Accès Configuration
1. Menu **🔗 APIs** > **➕ Nouvelle Intégration**
2. Choisir le type d'API (REST, GraphQL, Webhook)
3. Remplir informations de base

#### Étape 2 : Configuration Détaillée

**📋 Formulaire Configuration API**
```
┌─────────────────────────────────────────────────────────────────┐
│                    🔗 CONFIGURATION API                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📝 Nom de l'intégration                                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ API Prix Concurrent XYZ                                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 🔗 URL de base                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ https://api.concurrent-xyz.com/v1                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 🔑 Type d'authentification                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ◉ Clé API     ○ Bearer Token     ○ OAuth 2.0              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 🗝️ Clé d'API                                                    │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ••••••••••••••••••••••••                                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ⚙️ Paramètres avancés                                           │
│ ├─ Limite de taux: [60] requêtes/minute                        │
│ ├─ Timeout: [30] secondes                                      │
│ ├─ Retry automatique: [✓] Activé (3 tentatives)               │
│ ├─ Cache réponses: [✓] Activé (5 minutes)                     │
│ └─ Monitoring: [✓] Alertes si pannes                           │
│                                                                 │
│           [🧪 Tester Connexion]    [💾 Sauvegarder]            │
└─────────────────────────────────────────────────────────────────┘
```

#### Étape 3 : Test de Connexion

**🧪 Tests Automatiques**
- Connectivité réseau
- Authentification valide  
- Format réponses conforme
- Temps de réponse acceptable
- Limites de taux respectées

**✅ Rapport de Test**
```
📊 RÉSULTATS DES TESTS

🔗 Connectivité
  ✅ URL accessible
  ✅ SSL/TLS valide
  ⏱️ Temps réponse: 247ms

🔐 Authentification  
  ✅ Clé API valide
  ✅ Permissions suffisantes
  ⚠️ Expire dans 89 jours

📡 Endpoints testés
  ✅ GET /prices - 200 OK
  ✅ GET /products - 200 OK  
  ❌ POST /orders - 403 Forbidden (permissions insuffisantes)

⚡ Performance
  ✅ Limite taux: 60/min respectée
  ✅ Cache fonctionne: -78% temps réponse
  
🚨 RECOMMANDATIONS
  • Demander permissions POST pour endpoint /orders
  • Renouveler clé API avant expiration
  • Monitoring activé avec alertes email
```

### Utilisation API dans Scripts

#### 📞 Appels API Simples
```python
# Dans vos scripts Python
# L'API est automatiquement disponible via le nom configuré

def recuperer_prix_concurrents(produit_sku):
    """Récupère prix depuis API configurée"""
    
    # 🔗 Appel API automatique (auth/cache/retry géré)
    reponse = api_call(
        api_name="API Prix Concurrent XYZ",  # Nom configuré
        endpoint="/prices",
        method="GET",
        params={
            "sku": produit_sku,
            "currency": "EUR",
            "country": "FR"
        }
    )
    
    # ✅ Vérification réponse
    if reponse.get('success'):
        prix_data = reponse['data']
        return {
            'prix_concurrent': prix_data.get('price'),
            'disponible': prix_data.get('in_stock'),
            'derniere_maj': prix_data.get('updated_at'),
            'source': 'API Prix Concurrent XYZ'
        }
    else:
        # ❌ Gestion erreur
        return {
            'erreur': reponse.get('error', 'API indisponible'),
            'source': 'API Prix Concurrent XYZ'
        }

# 🎯 UTILISATION
prix_info = recuperer_prix_concurrents("PROD123")
print(f"Prix concurrent: {prix_info}")
```

#### 🔄 Appels API Multiples et Parallèles
```python
def analyser_marche_complet(liste_produits):
    """Analyse marché pour plusieurs produits en parallèle"""
    
    resultats = []
    
    # 🚀 Traitement par lots pour performance
    for produit_sku in liste_produits:
        
        # 📞 Appels parallèles aux APIs configurées  
        calls_paralleles = [
            {
                'api_name': 'API Prix Concurrent XYZ',
                'endpoint': f'/prices/{produit_sku}',
                'method': 'GET'
            },
            {
                'api_name': 'API Stock Fournisseur',
                'endpoint': f'/inventory/{produit_sku}',
                'method': 'GET'
            },
            {
                'api_name': 'API Avis Clients',
                'endpoint': f'/reviews',
                'method': 'GET',
                'params': {'product_id': produit_sku}
            }
        ]
        
        # ⚡ Exécution parallèle (gérée automatiquement)
        reponses = api_call_batch(calls_paralleles)
        
        # 📊 Consolidation résultats
        analyse_produit = {
            'sku': produit_sku,
            'prix_concurrent': reponses[0].get('data', {}).get('price'),
            'stock_fournisseur': reponses[1].get('data', {}).get('quantity', 0),
            'note_moyenne': reponses[2].get('data', {}).get('average_rating'),
            'timestamp': datetime.now().isoformat()
        }
        
        resultats.append(analyse_produit)
    
    return resultats

# 🎯 Exemple traitement 50 produits
produits = [f"PROD{i:03d}" for i in range(1, 51)]
analyse_marche = analyser_marche_complet(produits)

print(f"✅ Analyse de {len(analyse_marche)} produits terminée")
```

### Monitoring et Alertes API

#### 📊 Dashboard Intégrations
```
┌─────────────────────────────────────────────────────────────────┐
│                    📡 ÉTAT DES INTÉGRATIONS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ API Prix Concurrent XYZ          🟢 OPÉRATIONNELLE             │
│ ├─ Dernière vérification: Il y a 2 min                         │
│ ├─ Temps réponse moyen: 234ms                                  │ 
│ ├─ Requêtes aujourd'hui: 1,247 / 5,000 (25%)                  │
│ └─ Disponibilité 7j: 99.8%                                     │
│                                                                 │
│ API Stock Fournisseur            🟡 RALENTIE                   │
│ ├─ Dernière vérification: Il y a 5 min                         │
│ ├─ Temps réponse moyen: 2,100ms ⚠️                             │
│ ├─ Requêtes aujourd'hui: 456 / 2,000 (23%)                    │
│ └─ Disponibilité 7j: 97.2%                                     │
│                                                                 │
│ API Avis Clients                 🔴 ERREUR                     │
│ ├─ Dernière vérification: Il y a 12 min                        │
│ ├─ Erreur: 503 Service Unavailable                             │
│ ├─ Requêtes aujourd'hui: 89 / 1,000 (9%) - ❌ Échecs 45%      │
│ └─ Disponibilité 7j: 94.1%                                     │
│                                                                 │
│ [📈 Voir Détails] [⚙️ Configuration] [🔔 Gérer Alertes]        │
└─────────────────────────────────────────────────────────────────┘
```

#### 🚨 Configuration Alertes

**Types d'Alertes Disponibles**
- 🔴 **API Indisponible** : Panne détectée
- 🟡 **Performance Dégradée** : Temps réponse > seuil
- ⚠️ **Limite Taux Atteinte** : Approche quota
- 🔑 **Authentification** : Problème credentials
- 📊 **Usage Anormal** : Pattern d'utilisation inhabituel

**Canal de Notification**
- 📧 Email (recommandé)
- 💬 Slack/Teams
- 📱 SMS (urgences uniquement)
- 🔔 Push navigateur

## Analyses et Rapports

### Création de Rapports Automatisés

#### 📊 Assistant de Rapport
1. **Menu Analyses** > **➕ Nouveau Rapport**
2. **Type de rapport** : Choisir modèle ou personnalisé
3. **Source de données** : Scripts, APIs, ou les deux
4. **Fréquence** : Unique, quotidien, hebdomadaire, mensuel

#### 📋 Exemple : Rapport Hebdomadaire Pricing

**🎯 Configuration Rapport**
```
┌─────────────────────────────────────────────────────────────────┐
│                   📊 CONFIGURATION RAPPORT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📝 Nom du rapport                                               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Rapport Hebdomadaire - Analyse Pricing Concurrentiel       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 📅 Fréquence d'exécution                                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ○ Unique  ○ Quotidien  ◉ Hebdomadaire  ○ Mensuel           │ │
│ │ Jour: [Lundi] à [09:00]                                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 🔢 Sources de données                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✓ Script "Analyse Prix Concurrents v2.1"                   │ │
│ │ ✓ API "Prix Concurrent XYZ"                                 │ │
│ │ ✓ API "Stock Fournisseur"                                   │ │
│ │ ○ API "Avis Clients" (désactivée - erreurs)                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 📈 Sections du rapport                                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ✓ Résumé exécutif avec KPIs                                 │ │
│ │ ✓ Évolution prix vs concurrence                             │ │
│ │ ✓ Produits nécessitant action pricing                       │ │
│ │ ✓ Recommandations automatisées                              │ │
│ │ ✓ Graphiques de tendances                                   │ │
│ │ ✓ Tableau détaillé par produit                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 👥 Destinataires                                                │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ jean.dupont@entreprise.com (Responsable Pricing)            │ │
│ │ marie.martin@entreprise.com (Directrice Commerciale)        │ │
│ │ equipe-marketing@entreprise.com (Équipe Marketing)          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│         [🧪 Aperçu]  [📅 Programmer]  [💾 Sauvegarder]         │
└─────────────────────────────────────────────────────────────────┘
```

#### 📧 Exemple de Rapport Généré

**Objet Email** : `[HEBDOMADAIRE] Rapport Pricing Concurrentiel - Semaine 36`

```
📊 RAPPORT HEBDOMADAIRE - ANALYSE PRICING
Période: 2 - 8 septembre 2025
Généré automatiquement le lundi 9 septembre 2025 à 09:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RÉSUMÉ EXÉCUTIF

✅ 127 produits analysés cette semaine
📈 Prix moyen marché: +2.3% vs semaine précédente  
💰 Nos prix: 3.7% au-dessus de la moyenne marché
🔴 23 produits nécessitent action pricing URGENTE
🟡 45 produits à surveiller de près

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 INDICATEURS CLÉS

• Position concurrentielle globale: MOYENNE+
• Écart prix moyen vs concurrence: +3.7%
• Produits sous-performants: 18% du catalogue  
• Opportunités de hausse identifiées: 31 produits
• Alertes seuil marge: 7 produits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 ACTIONS PRIORITAIRES

📉 BAISSES RECOMMANDÉES (23 produits)
┌─────────────────────────────────────────────────┐
│ Widget Pro X1    | 99.90€ → 89.90€ (-10%)     │
│ Gadget Elite     | 149.00€ → 139.00€ (-7%)    │  
│ Module Advanced  | 199.50€ → 179.90€ (-10%)   │
│ ... voir tableau détaillé ci-dessous           │
└─────────────────────────────────────────────────┘

📈 HAUSSES POSSIBLES (31 produits)  
┌─────────────────────────────────────────────────┐
│ Basic Tool       | 39.90€ → 44.90€ (+13%)     │
│ Standard Kit     | 69.00€ → 74.90€ (+9%)      │
│ Pro Bundle       | 129.90€ → 139.90€ (+8%)    │
│ ... voir tableau détaillé ci-dessous           │
└─────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Graphiques et tableaux détaillés en pièces jointes]

📎 PIÈCES JOINTES
• rapport_pricing_detaille_S36.xlsx
• graphiques_tendances_S36.png  
• recommandations_actions_S36.pdf

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️ Ce rapport a été généré automatiquement par Perplexity AI
📞 Support: support-metier@perplexity.ai | 📚 Documentation
🔗 Accéder au dashboard: https://metier.perplexity.ai/dashboard
```

### Personnalisation des Analyses

#### 🎨 Créateur de Dashboard Personnalisé

**Interface Drag & Drop**
```
┌─────────────────────────────────────────────────────────────────┐
│                🎨 CRÉATEUR DASHBOARD PERSONNALISÉ               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🧱 WIDGETS DISPONIBLES          📊 ZONE DE CONSTRUCTION        │
│ ┌─────────────────────────┐     ┌─────────────────────────────┐ │
│ │ 📊 Graphique Ligne      │     │ ┌─────────┐  ┌─────────────┐│ │
│ │ 📈 Graphique Barres     │ →   │ │ KPI 1   │  │ KPI 2       ││ │  
│ │ 🍩 Graphique Donut      │     │ └─────────┘  └─────────────┘│ │
│ │ 📋 Tableau Données      │     │ ┌─────────────────────────────┐│ │
│ │ 🔢 Carte KPI           │     │ │                           ││ │
│ │ ⚠️  Alertes            │     │ │     Graphique Principal    ││ │
│ │ 📅 Calendrier          │     │ │                           ││ │
│ │ 🗺️ Carte              │     │ │                           ││ │
│ └─────────────────────────┘     └─────────────────────────────┘│ │
│                                                                 │
│ ⚙️ PROPRIÉTÉS DU WIDGET SÉLECTIONNÉ                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Widget: Graphique Principal                                  │ │
│ │ Type: Graphique en lignes                                   │ │
│ │ Source: Script "Analyse Pricing"                            │ │
│ │ Données: prix_evolution_7j                                  │ │
│ │ Couleurs: [Bleu] [Vert] [Rouge]                            │ │
│ │ Période: [7 derniers jours] [Auto-refresh: 1h]             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│     [👀 Aperçu]  [💾 Sauvegarder]  [📤 Partager]              │
└─────────────────────────────────────────────────────────────────┘
```

## Support et Résolution de Problèmes

### Questions Fréquentes

#### ❓ Mon script ne s'exécute pas
**🔍 Diagnostic rapide :**
1. Vérifier la syntaxe Python (indentation, deux-points)
2. Contrôler les imports (seules librairies autorisées)  
3. Valider les données d'entrée (format JSON correct)
4. Vérifier les limites (timeout 5min, mémoire 2GB)

**💡 Solutions courantes :**
- **Erreur de syntaxe** : Utiliser l'éditeur intégré avec coloration
- **Import bloqué** : Consulter liste librairies autorisées
- **Données malformées** : Valider JSON avec outil intégré
- **Timeout** : Optimiser code ou diviser en sous-tâches

#### ❓ L'API ne répond pas
**🔍 Vérifications :**
1. **État API** : Dashboard intégrations > Vérifier statut
2. **Credentials** : Tester connexion depuis configuration
3. **Limites taux** : Consulter compteurs utilisation
4. **Format requête** : Vérifier paramètres et headers

**💡 Actions possibles :**
- **API en panne** : Activer notifications et attendre rétablissement
- **Authentification échouée** : Renouveler clés API
- **Quota dépassé** : Attendre reset ou upgrader plan
- **Mauvaise configuration** : Re-tester avec assistant configuration

#### ❓ Les rapports ne sont pas générés
**🔍 Points de contrôle :**
1. **Sources de données** : Vérifier que scripts/APIs fonctionnent
2. **Planning** : Confirmer horaires et fréquence
3. **Destinataires** : Emails valides et boîtes non pleines
4. **Permissions** : Droits suffisants pour exécution

### Contact Support

#### 🎫 Créer un Ticket de Support
1. **Menu Aide** > **📞 Contacter Support**
2. **Catégorie** : Technique, Fonctionnel, ou Formation
3. **Priorité** : Basse, Normale, Élevée, Critique
4. **Description** : Détails problème + captures d'écran

#### 📞 Support Téléphonique
- **France** : +33 1 xx xx xx xx
- **Heures** : 9h-18h du lundi au vendredi
- **Urgences** : 24h/7j pour abonnements Premium

#### 💬 Chat en Direct
- **Disponible** : Icône 💬 en bas à droite
- **Heures** : 9h-18h en semaine
- **Temps réponse** : < 5 minutes en moyenne

---

## 🎓 Ressources Formation

### 📚 Documentation Avancée
- **Guide Développeur** : Scripts Python avancés
- **API Reference** : Documentation complète intégrations
- **Best Practices** : Modèles et recommandations
- **Changelog** : Nouvelles fonctionnalités et améliorations

### 🎥 Vidéos Tutoriels
- **Démarrage Rapide** : 10 minutes pour débuter
- **Scripts Python** : De débutant à expert (série 5 vidéos)
- **Intégrations API** : Configuration et utilisation avancée
- **Rapports Automatisés** : Créer des analyses impactantes

### 🏆 Certifications Disponibles
- **Utilisateur Perplexity AI** : Maîtrise fonctionnalités de base
- **Expert Scripts Python** : Développement scripts métier
- **Spécialiste Intégrations** : APIs et automatisations
- **Analyste Données** : Rapports et tableaux de bord

**Félicitations ! Vous disposez maintenant de tous les outils pour maîtriser l'espace métier Perplexity AI. N'hésitez pas à explorer, expérimenter et contacter le support si besoin. Bonne analyse ! 🚀**