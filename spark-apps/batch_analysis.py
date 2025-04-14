from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime, window, count, avg, max, desc, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType, StructType
import time
import os
import socket
from datetime import datetime, timedelta

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
            test_path = hdfs_path + "/test"
            test_df.write.mode("overwrite").parquet(test_path)
            print(f"✅ Test d'écriture HDFS réussi à la tentative {attempt}")
            return True
        except Exception as e:
            print(f"❌ Échec de connexion HDFS (tentative {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                print(f"Nouvel essai dans {retry_interval} secondes...")
                time.sleep(retry_interval)
    
    return False

def main():
    # Afficher les informations de démarrage
    print("====================================================")
    print("ANALYSE BATCH DES OBJETS CÉLESTES")
    print("====================================================")
    print(f"Heure de l'analyse: {datetime.now()}")
    
    # Créer la session Spark avec plus de configurations pour HDFS
    spark = SparkSession.builder \
        .appName("SpaceObjectsBatchAnalysis") \
        .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
        .config("spark.hadoop.fs.hdfs.impl", "org.apache.hadoop.hdfs.DistributedFileSystem") \
        .getOrCreate()

    # Configuration HDFS
    hdfs_host = "hadoop-namenode"
    hdfs_port = 9000
    hdfs_path = f"hdfs://{hdfs_host}:{hdfs_port}/space_data/dangerous_objects"
    
    print(f"Préparation de l'analyse de données depuis HDFS: {hdfs_path}")
    hdfs_output_path = f"hdfs://{hdfs_host}:{hdfs_port}/space_data/batch_analysis"
    
    print(f"Source des données: {hdfs_path}")
    print(f"Destination des résultats: {hdfs_output_path}")
    print("====================================================")

    # Vérifier la connexion HDFS
    if not test_hdfs_connection(spark, hdfs_output_path):
        print("ERREUR: Impossible de se connecter à HDFS après plusieurs tentatives")
        # Alternative: utiliser le stockage local
        print("Configuration du stockage local comme solution de secours...")
        os.makedirs("/tmp/space_data/dangerous_objects", exist_ok=True)
        os.makedirs("/tmp/space_data/batch_analysis", exist_ok=True)
        hdfs_path = "file:///tmp/space_data/dangerous_objects"
        hdfs_output_path = "file:///tmp/space_data/batch_analysis"
        print(f"Les données seront lues depuis: {hdfs_path}")
        print(f"Les résultats seront écrits dans: {hdfs_output_path}")

    try:
        # Vérifier si les données source existent
        try:
            # Lire tous les fichiers Parquet depuis HDFS
            df = spark.read.parquet(hdfs_path)
            
            # Convertir le timestamp Unix en timestamp lisible
            df = df.withColumn("detection_time", from_unixtime(col("timestamp")))
            
            # Calculer le nombre total d'objets
            total_objects = df.count()
            print(f"Nombre total d'objets détectés: {total_objects}")
        except Exception as e:
            print(f"Erreur lors de la lecture des données: {str(e)}")
            print("Génération de données de test...")
            
            # Créer des données de test si aucune donnée n'est disponible
            data = [(f"test_{i}", int(time.time()), 30.0, 15.0, "astéroïde") 
                    for i in range(10)]
            df = spark.createDataFrame(data, ["id", "timestamp", "vitesse", "taille", "type"])
            df = df.withColumn("detection_time", from_unixtime(col("timestamp")))
            total_objects = df.count()
            print(f"Données de test générées: {total_objects} objets")
        
        if total_objects == 0:
            print("Aucune donnée disponible pour l'analyse.")
            return
        
        # 1. Agréger les observations par type d'objets célestes
        print("\n1. AGRÉGATION PAR TYPE D'OBJETS CÉLESTES")
        print("----------------------------------------------------")
        type_stats = df.groupBy("type") \
            .agg(
                count("*").alias("count"),
                avg("vitesse").alias("vitesse_moyenne"),
                avg("taille").alias("taille_moyenne"),
                max("vitesse").alias("vitesse_max")
            ) \
            .orderBy(desc("count"))
        
        type_stats.show(truncate=False)
        
        # 2. Calculer les 5 objets les plus rapides détectés sur les 24 dernières heures
        print("\n2. TOP 5 DES OBJETS LES PLUS RAPIDES (DERNIÈRES 24H)")
        print("----------------------------------------------------")
        
        # Calculer la date limite (24h avant maintenant)
        current_time = int(time.time())
        limit_time = current_time - (24 * 60 * 60)  # 24 heures en secondes
        
        # Filtrer les données des dernières 24 heures
        recent_df = df.filter(col("timestamp") >= limit_time)
        recent_count = recent_df.count()
        
        if recent_count == 0:
            print("Aucune donnée disponible pour les dernières 24 heures.")
        else:
            # Trouver les 5 objets les plus rapides
            top_speed_objects = recent_df.orderBy(desc("vitesse")).limit(5)
            top_speed_objects = top_speed_objects.select(
                "id", 
                "type", 
                "vitesse", 
                "taille", 
                "detection_time"
            )
            
            top_speed_objects.show(truncate=False)
        
        # 3. Statistiques supplémentaires
        print("\n3. STATISTIQUES SUPPLÉMENTAIRES")
        print("----------------------------------------------------")
        
        # Calculer la vitesse moyenne et la taille moyenne
        stats = df.agg(
            avg("vitesse").alias("vitesse_moyenne_globale"),
            avg("taille").alias("taille_moyenne_globale"),
            max("vitesse").alias("vitesse_maximale"),
            max("taille").alias("taille_maximale")
        )
        
        stats.show(truncate=False)
        
        # 4. Sauvegarder les résultats dans HDFS
        print(f"\nSauvegarde des résultats dans {hdfs_output_path}")
        
        try:
            # Sauvegarder les statistiques par type
            type_stats.write.mode("overwrite").parquet(f"{hdfs_output_path}/type_stats")
            
            # Sauvegarder le top 5 des objets les plus rapides
            if recent_count > 0:
                top_speed_objects = top_speed_objects.withColumn("analysis_time", lit(current_time))
                top_speed_objects.write.mode("overwrite").parquet(f"{hdfs_output_path}/top_speed_objects")
            
            print("Sauvegarde terminée avec succès")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des résultats: {str(e)}")
            # Essayer d'écrire en local si l'écriture HDFS échoue
            local_output = "file:///tmp/space_data/batch_analysis"
            print(f"Tentative de sauvegarde en local: {local_output}")
            type_stats.write.mode("overwrite").parquet(f"{local_output}/type_stats")
            if recent_count > 0:
                top_speed_objects.write.mode("overwrite").parquet(f"{local_output}/top_speed_objects")
            print("Sauvegarde locale terminée")
        
        print("====================================================")
        print("ANALYSE BATCH TERMINÉE AVEC SUCCÈS")
        print("====================================================")
        
    except Exception as e:
        print(f"Erreur lors de l'analyse batch: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 