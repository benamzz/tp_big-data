#!/bin/bash

# Désactiver la conversion de chemins dans Git Bash
export MSYS_NO_PATHCONV=1


echo "Nettoyage de l'environnement précédent..."
docker-compose down -v

#Supprimer les volumes Hadoop
echo "Suppression des volumes Hadoop..."
docker volume rm $(docker volume ls -q | grep -E 'hadoop_namenode|hadoop_datanode') 2>/dev/null || true

# Démarrer tous les services
echo "Démarrage des services Docker..."
docker-compose up -d

# Attendre que les services soient prêts
echo "Attente du démarrage des services (30s)..."
sleep 30

# Vérifier l'état des conteneurs
echo "Vérification de l'état des conteneurs..."
docker-compose ps

# Configuration réseau
echo "Configuration des entrées hosts pour la résolution des noms..."
NAMENODE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' hadoop-namenode)
DATANODE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' hadoop-datanode)
SPARK_MASTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' spark-master)

# Ajouter les entrées dans /etc/hosts de tous les conteneurs
docker exec hadoop-namenode bash -c "echo '$DATANODE_IP hadoop-datanode' >> /etc/hosts"
docker exec hadoop-datanode bash -c "echo '$NAMENODE_IP hadoop-namenode' >> /etc/hosts"
docker exec spark-master bash -c "echo '$NAMENODE_IP hadoop-namenode' >> /etc/hosts"
docker exec spark-master bash -c "echo '$DATANODE_IP hadoop-datanode' >> /etc/hosts"

# Configuration de Hadoop dans Spark
echo "Configuration de Hadoop dans Spark..."
docker exec spark-master bash -c "mkdir -p /etc/hadoop/conf"
docker exec spark-master bash -c "cat > /etc/hadoop/conf/core-site.xml << 'EOF'
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://hadoop-namenode:9000</value>
    </property>
</configuration>
EOF"
docker exec spark-master bash -c "echo 'export HADOOP_CONF_DIR=/etc/hadoop/conf' >> /spark/conf/spark-env.sh"
docker exec spark-master bash -c "echo 'spark.hadoop.fs.defaultFS hdfs://hadoop-namenode:9000' >> /spark/conf/spark-defaults.conf"

# Initialisation des répertoires HDFS
echo "Initialisation des répertoires HDFS..."
docker exec hadoop-namenode hdfs dfs -mkdir -p /space_data/dangerous_objects
docker exec hadoop-namenode hdfs dfs -mkdir -p /space_data/batch_analysis
docker exec hadoop-namenode hdfs dfs -mkdir -p /tmp/checkpoint
docker exec hadoop-namenode hdfs dfs -chmod -R 777 /space_data
docker exec hadoop-namenode hdfs dfs -chmod -R 777 /tmp

# Téléchargement des dépendances Kafka pour Spark
echo "Téléchargement des dépendances Kafka..."
docker exec spark-master mkdir -p /opt/spark/jars/kafka-deps
docker exec spark-master bash -c "cd /opt/spark/jars/kafka-deps && \
    wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.1.1/spark-sql-kafka-0-10_2.12-3.1.1.jar && \
    wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.1.1/spark-token-provider-kafka-0-10_2.12-3.1.1.jar && \
    wget -q https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.6.0/kafka-clients-2.6.0.jar && \
    wget -q https://repo1.maven.org/maven2/com/github/luben/zstd-jni/1.4.8-1/zstd-jni-1.4.8-1.jar && \
    wget -q https://repo1.maven.org/maven2/org/lz4/lz4-java/1.7.1/lz4-java-1.7.1.jar && \
    wget -q https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.8.2/snappy-java-1.1.8.2.jar && \
    wget -q https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.30/slf4j-api-1.7.30.jar && \
    wget -q https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.6.2/commons-pool2-2.6.2.jar"

# Lancement des applications Spark
echo "Lancement des applications Spark..."
docker exec spark-master /spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.executor.memory=1g \
    --conf spark.driver.memory=1g \
    --conf "spark.hadoop.fs.defaultFS=hdfs://hadoop-namenode:9000" \
    --conf "spark.hadoop.dfs.client.use.datanode.hostname=true" \
    --conf "spark.driver.extraJavaOptions=-Djava.security.krb5.realm= -Djava.security.krb5.kdc=" \
    --jars /opt/spark/jars/kafka-deps/spark-sql-kafka-0-10_2.12-3.1.1.jar,/opt/spark/jars/kafka-deps/kafka-clients-2.6.0.jar,/opt/spark/jars/kafka-deps/zstd-jni-1.4.8-1.jar,/opt/spark/jars/kafka-deps/lz4-java-1.7.1.jar,/opt/spark/jars/kafka-deps/snappy-java-1.1.8.2.jar,/opt/spark/jars/kafka-deps/slf4j-api-1.7.30.jar,/opt/spark/jars/kafka-deps/spark-token-provider-kafka-0-10_2.12-3.1.1.jar,/opt/spark/jars/kafka-deps/commons-pool2-2.6.2.jar \
    /opt/spark-apps/streaming.py &

echo "===== Lets goooo !!! ====="
echo "Accès aux services :"
echo "- Frontend : http://localhost:3000"
echo "- API : http://localhost:5000"
echo "- Spark UI : http://localhost:8080"
echo "- HDFS UI : http://localhost:9870" 