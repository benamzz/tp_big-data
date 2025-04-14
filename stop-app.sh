#!/bin/bash

# Désactiver la conversion de chemins dans Git Bash
export MSYS_NO_PATHCONV=1

echo "===== ARRÊT DE L'APPLICATION DE SURVEILLANCE D'OBJETS CÉLESTES ====="

# 1. Arrêter tous les conteneurs
echo "Arrêt des conteneurs..."
docker-compose down

# 2. Supprimer les volumes Hadoop
echo "Suppression des volumes Hadoop..."
docker volume rm $(docker volume ls -q | grep -E 'hadoop_namenode|hadoop_datanode') 2>/dev/null || true

echo "===== APPLICATION ARRÊTÉE ====="
echo "Pour redémarrer l'application, utilisez : ./start-app.sh" 