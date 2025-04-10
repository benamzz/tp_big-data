from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime, window, count, avg, max, desc, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType, StructType
import time
from datetime import datetime, timedelta

def main():
    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("SpaceObjectsBatchAnalysis") \
        .getOrCreate()

    # Configuration HDFS
    hdfs_host = "hadoop-namenode"
    hdfs_port = 9000
    hdfs_path = f"hdfs://{hdfs_host}:{hdfs_port}/space_data/dangerous_objects"
    
    # Afficher les informations de démarrage
    print("====================================================")
    print("ANALYSE BATCH DES OBJETS CÉLESTES")
    print("====================================================")
    print(f"Heure de l'analyse: {datetime.now()}")
    print(f"Source des données: {hdfs_path}")
    print("====================================================")

    try:
        # Lire tous les fichiers Parquet depuis HDFS
        df = spark.read.parquet(hdfs_path)
        
        # Convertir le timestamp Unix en timestamp lisible
        df = df.withColumn("detection_time", from_unixtime(col("timestamp")))
        
        # Calculer le nombre total d'objets
        total_objects = df.count()
        print(f"Nombre total d'objets détectés: {total_objects}")
        
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
        output_path = f"hdfs://{hdfs_host}:{hdfs_port}/space_data/batch_analysis"
        
        # Sauvegarder les statistiques par type
        type_stats.write.mode("overwrite").parquet(f"{output_path}/type_stats")
        
        # Sauvegarder le top 5 des objets les plus rapides
        if recent_count > 0:
            top_speed_objects = top_speed_objects.withColumn("analysis_time", lit(current_time))
            top_speed_objects.write.mode("overwrite").parquet(f"{output_path}/top_speed_objects")
        
        print(f"\nRésultats de l'analyse sauvegardés dans {output_path}")
        print("====================================================")
        
    except Exception as e:
        print(f"Erreur lors de l'analyse batch: {str(e)}")

if __name__ == "__main__":
    main() 