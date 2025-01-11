# Split Delivery Vehicle Routing Problem (SDVRP) Solver

Ce projet propose une solution interactive au problème de routage de véhicules avec livraisons fractionnées (SD-VRP), implémentant à la fois des méthodes exactes via Gurobi et des approches métaheuristiques.

## Équipe
- HAMMALE MOURAD
- DOHA CHBIHI
- AYA BOUKHARI
- MOHAMED BENKIRANE
- HABBANI MOHAMMED

## Table des matières
1. [Description](#description)
2. [Installation](#installation)
3. [Structure du Projet](#structure-du-projet)
4. [Algorithmes Implémentés](#algorithmes-implémentés)
5. [Licence Gurobi](#licence-gurobi)
6. [Utilisation](#utilisation)

## Description
Le SDVRP est une variante du problème classique VRP où les demandes des clients peuvent être satisfaites par plusieurs véhicules. Le projet implémente :
- Une résolution exacte via Gurobi pour les petites instances
- Une approche métaheuristique pour les grandes instances
- Une interface utilisateur interactive via Streamlit

## Installation

### Prérequis
- Python 3.8+
- Gurobi 10.0.3 avec licence valide

### Configuration
1. Cloner le repository :
```bash
git clone [URL_du_repo]
cd [nom_du_dossier]
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Structure du Projet
```
├── app.py                # Interface utilisateur Streamlit
├── solve.py             # Solveur exact (cas 0-6)
├── test.py              # Solveur exact (cas 7-32)
├── metaheuristic.py     # Solveur métaheuristique
├── requirements.txt     # Dépendances
├── gurobi.lic          # Licence Gurobi
└── Case*.txt           # Fichiers d'instances
```

## Algorithmes Implémentés

### Solveur Exact (Gurobi)
- **Modèle mathématique** : 
  - Variables binaires pour les arcs (x_ijk)
  - Variables continues pour les quantités livrées (y_ik)
  - Objectif : minimisation de la distance totale
- **Contraintes principales** :
  - Conservation du flux
  - Capacité des véhicules
  - Satisfaction des demandes
  - Élimination des sous-tours

### Métaheuristique (Recherche Tabou)
- **Initialisation** : Solution gloutonne basée sur la distance et la demande
- **Voisinage** :
  - Déplacement de clients entre routes
  - Division de livraisons
  - Fusion de routes similaires
- **Critères** :
  - Liste tabou de taille dynamique
  - Critère d'aspiration basé sur le coût
  - Diversification après stagnation

## Licence Gurobi

### Obtention d'une licence académique gratuite
1. Créer un compte sur [Gurobi Academic Program](https://www.gurobi.com/academia/academic-program-and-licenses/)
2. Utiliser une adresse email universitaire
3. Suivre les instructions pour générer une licence
4. Placer le fichier `gurobi.lic` dans le répertoire du projet



## Utilisation

### Lancer l'application
```bash
streamlit run app.py
```

### Interface utilisateur
1. Sélectionner la méthode de résolution :
   - Métaheuristique
   - Solveur Exact (Gurobi)

2. Choisir le fichier d'instance (Case0.txt à Case32.txt)

3. Définir les paramètres :
   - Temps maximum de résolution
   - Nombre d'itérations (métaheuristique)

### Visualisation des résultats
- Résumé de la solution
- Détails des routes
- Visualisation graphique
- Téléchargement de la solution

## Notes importantes
- Les cas 0-6 sont résolus avec solve.py
- Les cas 7-32 sont résolus avec sdvrp_solver.py
- La métaheuristique peut être utilisée pour tous les cas
- La licence académique Gurobi est nécessaire pour les méthodes exactes

