from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType

if __name__ == "__main__":
    # Créer la session Spark
    spark = SparkSession.builder \
        .appName("SpaceObjectsStreaming") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .getOrCreate()

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

    # Lire les données de Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "space_data") \
        .option("startingOffsets", "latest") \
        .load()

    # Parser les données JSON
    parsed = df.selectExpr("CAST(value AS STRING) as json") \
        .select(from_json("json", schema).alias("data")) \
        .select("data.*")

    # Filtrer les objets dangereux (vitesse > 25 km/s et taille > 10m)
    dangerous_objects = parsed.filter((col("vitesse") > 25) & (col("taille") > 10))

    # Configuration HDFS
    hdfs_host = "hadoop-namenode"
    hdfs_port = 9000
    hdfs_path = f"hdfs://{hdfs_host}:{hdfs_port}/space_data/dangerous_objects"

    # Écrire les résultats dans HDFS au format Parquet
    query = dangerous_objects \
        .writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", hdfs_path) \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .start()

    # Attendre la fin du streaming (ce qui n'arrive jamais dans ce cas)
    query.awaitTermination() 