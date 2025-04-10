# TP Big Data : Analyse de Données Astronomiques en Temps Réel

Ce projet implémente un système de surveillance d'objets célestes en temps réel utilisant Kafka, Spark, Hadoop et une interface web React.

## Architecture

- **Kafka** : Gestion du flux de données en temps réel
- **Spark Streaming** : Traitement des données en temps réel
- **Hadoop HDFS** : Stockage des données
- **API Flask** : Interface entre le frontend et les données
- **Frontend React** : Visualisation des données en 3D

## Prérequis

- Docker
- Docker Compose

## Structure du Projet

```
.
├── api/                 # API Flask
├── data-producer/       # Producteur de données Kafka
├── frontend/            # Application React
├── spark-apps/          # Applications Spark
│   ├── streaming.py     # Traitement en temps réel
│   └── batch_analysis.py # Analyse batch
├── hadoop.env           # Configuration Hadoop
├── docker-compose.yml   # Configuration Docker
├── spark-submit.sh      # Script pour lancer Spark Streaming
└── spark-batch.sh       # Script pour lancer l'analyse batch
```

## Installation et démarrage

1. Clonez le dépôt et naviguez dans le répertoire du projet.

2. Lancez les services avec Docker Compose :

```bash
docker-compose down -v  # Pour nettoyer l'environnement
docker-compose up -d    # Pour démarrer les services
```

3. Vérifiez que tous les services sont démarrés :

```bash
docker-compose ps
```

4. Lancez l'application Spark Streaming pour traiter les données en temps réel :

   **Sur Windows avec PowerShell** :

   ```powershell
   docker exec -it spark-master /spark/bin/spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1 /opt/spark-apps/streaming.py
   ```

   **Sur Windows avec Git Bash** (utilisez le script) :

   ```bash
   chmod +x spark-submit.sh
   ./spark-submit.sh
   ```

5. (Optionnel) Lancez l'analyse batch Spark pour obtenir des statistiques :

   **Sur Windows avec PowerShell** :

   ```powershell
   docker exec -it spark-master /spark/bin/spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1 /opt/spark-apps/batch_analysis.py
   ```

   **Sur Windows avec Git Bash** (utilisez le script) :

   ```bash
   chmod +x spark-batch.sh
   ./spark-batch.sh
   ```

## Accès aux services

- **Frontend** : http://localhost:3000

  - Interface web pour visualiser les objets célestes et les alertes

- **API** :

  - http://localhost:5000/objects (liste de tous les objets)
  - http://localhost:5000/alerts (objets dangereux uniquement)

- **Spark Master UI** : http://localhost:8080

  - Pour surveiller l'application Spark Streaming

- **Hadoop UI** : http://localhost:9870
  - Pour explorer le système de fichiers HDFS

## Résolution des problèmes courants

### Problèmes avec Git Bash sur Windows

Git Bash convertit automatiquement les chemins, ce qui peut causer des problèmes avec Docker. Utilisez une des solutions suivantes :

1. Utilisez PowerShell ou CMD à la place de Git Bash
2. Utilisez `export MSYS_NO_PATHCONV=1` avant les commandes Docker
3. Utilisez le double slash pour les chemins (ex: `//opt//spark-apps//streaming.py`)

### Données non visibles dans le frontend

Si vous ne voyez pas les données dans le frontend :

1. Vérifiez que l'application Spark Streaming est en cours d'exécution
2. Vérifiez les logs du producteur pour confirmer que les données sont envoyées à Kafka
3. Vérifiez les logs de l'API pour voir si elle peut accéder aux données HDFS
4. Vérifiez l'interface HDFS (http://localhost:9870) pour voir si les fichiers existent

### Problèmes avec HDFS

Si HDFS ne fonctionne pas correctement :

1. Vérifiez que le NameNode est actif : `docker-compose logs hadoop-namenode`
2. Vérifiez que le DataNode est actif : `docker-compose logs hadoop-datanode`
3. Essayez de redémarrer les services Hadoop :
   ```bash
   docker-compose restart hadoop-namenode hadoop-datanode
   ```

### Redémarrage des services

Pour redémarrer un service spécifique :

```bash
docker-compose restart [service_name]
```

## Fonctionnement

1. Le producteur (`data-producer`) génère des données d'objets célestes aléatoires et les envoie à Kafka.
2. L'application Spark Streaming (`spark-apps/streaming.py`) lit les données depuis Kafka, filtre les objets dangereux et les enregistre dans HDFS.
3. L'analyse batch Spark (`spark-apps/batch_analysis.py`) fournit des statistiques sur les objets détectés, y compris les 5 objets les plus rapides des dernières 24 heures.
4. L'API Flask (`api`) expose les données stockées dans HDFS via des endpoints REST.
5. Le frontend React (`frontend`) affiche les objets célestes et les alertes en temps réel.

## Arrêt des services

Pour arrêter tous les services :

```bash
docker-compose down
```

Pour arrêter les services et supprimer les volumes :

```bash
docker-compose down -v
```
