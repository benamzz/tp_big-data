#!/bin/bash

# Désactiver la conversion de chemin dans Git Bash (nécessaire sur Windows)
export MSYS_NO_PATHCONV=1

# Exécuter l'application Spark Streaming
docker exec -it spark-master /spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1 \
    /opt/spark-apps/streaming.py 