from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType
import time
import os
import socket

def test_hdfs_connection(spark, hdfs_path, max_retries=5, retry_interval=10):
    """Teste la connexion HDFS avec plusieurs tentatives"""
    print(f"Test de connexion HDFS vers {hdfs_path}")
    
    for attempt in range(1, max_retries + 1):
        try:
            # Vérifier si on peut résoudre le nom d'hôte
            namenode_host = hdfs_path.split("//")[1].split(":")[0]
            try:
                namenode_ip = socket.gethostbyname(namenode_host)
                print(f"Résolution du nom d'hôte {namenode_host} -> {namenode_ip}")
            except socket.gaierror:
                print(f"Impossible de résoudre le nom d'hôte {namenode_host}")
                
            # Créer un petit DataFrame et essayer de l'écrire
            test_df = spark.createDataFrame([(1, f"test-{attempt}")], ["id", "value"])
            test_df.write.mode("overwrite").parquet(hdfs_path + "/test")
            print(f"✅ Test d'écriture HDFS réussi à la tentative {attempt}")
            return True
        except Exception as e:
            print(f"❌ Échec de connexion HDFS (tentative {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                print(f"Nouvel essai dans {retry_interval} secondes...")
                time.sleep(retry_interval)
    
    return False

if __name__ == "__main__":
    print("====================================================")
    print("DÉMARRAGE DE L'APPLICATION SPARK STREAMING")
    print("====================================================")
    
    # Attendre un peu que tous les services soient prêts
    print("Attente avant démarrage (5s)...")
    time.sleep(5)
    
    try:
        # Créer la session Spark avec plus de configurations pour HDFS
        print("Initialisation de la session Spark...")
        spark = SparkSession.builder \
            .appName("SpaceObjectsStreaming") \
            .master("spark://spark-master:7077") \
            .config("spark.hadoop.fs.defaultFS", "hdfs://hadoop-namenode:9000") \
            .getOrCreate()
            
        # Afficher la configuration du système de fichiers
        print("Configuration du système de fichiers:")
        print(spark.sparkContext._jsc.hadoopConfiguration().get("fs.defaultFS"))
        
        # Définir le schéma des données JSON
        schema = StructType([
            StructField("id", StringType(), True),
            StructField("timestamp", LongType(), True),
            StructField("position", 
                       StructType([
                           StructField("x", DoubleType(), True),
                           StructField("y", DoubleType(), True),
                           StructField("z", DoubleType(), True)
                       ]), True),
            StructField("vitesse", DoubleType(), True),
            StructField("taille", DoubleType(), True),
            StructField("type", StringType(), True)
        ])

        print("Connexion à Kafka...")
        # Lire les données de Kafka
        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:29092") \
            .option("subscribe", "space_data") \
            .option("startingOffsets", "latest") \
            .load()
            
        print("Parsing des données JSON...")
        # Parser les données JSON
        parsed = df.selectExpr("CAST(value AS STRING) as json") \
            .select(from_json("json", schema).alias("data")) \
            .select("data.*")

        # Filtrer les objets dangereux (vitesse > 25 km/s et taille > 10m)
        print("Filtrage des objets dangereux...")
        dangerous_objects = parsed.filter((col("vitesse") > 25) & (col("taille") > 10))

        # Configuration pour sauvegarder vers HDFS
        hdfs_host = "hadoop-namenode"
        hdfs_port = 9000
        hdfs_path = f"hdfs://{hdfs_host}:{hdfs_port}/space_data/dangerous_objects"
        
        print(f"Préparation de l'écriture vers HDFS: {hdfs_path}")
        
        # Test de connexion HDFS avec plusieurs tentatives
        if not test_hdfs_connection(spark, hdfs_path):
            print("ERREUR: Impossible de se connecter à HDFS après plusieurs tentatives")
            # Alternative: écrire en local si HDFS n'est pas disponible
            print("Configuration du stockage local comme solution de secours...")
            hdfs_path = "file:///tmp/space_data/dangerous_objects"
            os.makedirs("/tmp/space_data/dangerous_objects", exist_ok=True)
            print(f"Les données seront écrites localement: {hdfs_path}")
        
        # Écrire les résultats dans HDFS au format Parquet
        print("Démarrage du stream...")
        query = dangerous_objects \
            .writeStream \
            .outputMode("append") \
            .format("parquet") \
            .option("path", hdfs_path) \
            .option("checkpointLocation", "/tmp/checkpoint") \
            .start()

        print("Stream démarré avec succès! En attente de données...")
        # Attendre la fin du streaming (ce qui n'arrive jamais dans ce cas)
        query.awaitTermination()
        
    except Exception as e:
        print(f"ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc() 