# Projet de Surveillance d'Objets Célestes

Ce projet implémente un système de surveillance en temps réel d'objets célestes potentiellement dangereux. Il utilise Apache Kafka, Spark Streaming, HDFS et une interface web pour visualiser les résultats.

## Architecture

- **Kafka** : Gestion du flux de données en temps réel
- **Spark Streaming** : Traitement des données en temps réel
- **HDFS** : Stockage persistant des données
- **API Flask** : Endpoints REST pour accéder aux données
- **Frontend React** : Visualisation des objets en 3D

## Prérequis

- Docker et Docker Compose
- Git Bash (pour Windows)

## Démarrage Rapide

Pour démarrer l'application complète, utilisez simplement :

```bash
# Démarrer l'application
./start-app.sh
```

Ce script unique :

1. Nettoie l'environnement précédent
2. Démarre tous les services Docker
3. Configure la connectivité entre les services
4. Télécharge les dépendances nécessaires
5. Initialise les répertoires HDFS
6. Lance l'application Spark Streaming

## Arrêt de l'Application

Pour arrêter proprement l'application :

```bash
# Arrêter l'application
./stop-app.sh
```

Ce script :

1. Arrête tous les conteneurs
2. Supprime les volumes Hadoop
3. Nettoie l'environnement

## Accès aux Services

- **Frontend :** http://localhost:3000
- **API Flask :**
  - Liste des objets : http://localhost:5000/objects
  - Alertes : http://localhost:5000/alerts
- **Spark UI :** http://localhost:8080
- **HDFS UI :** http://localhost:9870

## Structure du Projet

```
.
├── api/                 # API Flask
├── data-producer/       # Producteur de données Kafka
├── frontend/            # Interface React
├── spark-apps/          # Applications Spark
│   ├── streaming.py     # Traitement streaming
│   └── batch_analysis.py # Analyse batch
├── docker-compose.yml   # Configuration Docker
├── start-app.sh         # Script de démarrage
└── stop-app.sh          # Script d'arrêt
```
