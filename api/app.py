from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os
import glob
import logging
import pyarrow.parquet as pq
from pyarrow import fs
import random
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration HDFS
HDFS_HOST = "hadoop-namenode"
HDFS_PORT = 9000
HDFS_PATH = "/space_data/dangerous_objects"

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil de l'API."""
    return jsonify({
        "message": "API de surveillance des objets célestes",
        "endpoints": [
            "/objects - Liste des objets célestes détectés",
            "/alerts - Liste des objets dangereux"
        ]
    })

@app.route('/objects', methods=['GET'])
def get_objects():
    """Récupère la liste des objets célestes détectés."""
    try:
        logger.info(f"Recherche de fichiers dans HDFS: {HDFS_PATH}")
        
        # Connexion à HDFS
        hdfs = fs.HadoopFileSystem(host=HDFS_HOST, port=HDFS_PORT)
        
        # Vérifier si le chemin existe
        if not hdfs.exists(HDFS_PATH):
            logger.warning(f"Le chemin HDFS {HDFS_PATH} n'existe pas")
            return jsonify({"error": "Aucune donnée disponible. Le répertoire HDFS n'existe pas."}), 404
        
        # Lister les fichiers Parquet
        file_selector = fs.FileSelector(HDFS_PATH, recursive=True)
        file_info = hdfs.get_file_info(file_selector)
        parquet_files = [f.path for f in file_info if f.path.endswith('.parquet')]
        
        logger.info(f"Fichiers trouvés dans HDFS: {parquet_files}")
        
        if not parquet_files:
            logger.warning("Aucun fichier Parquet trouvé dans HDFS")
            return jsonify({"error": "Aucun fichier de données trouvé. Vérifiez que Spark Streaming fonctionne correctement."}), 404
        
        # Lire les fichiers Parquet depuis HDFS
        all_data = []
        for file_path in parquet_files:
            try:
                logger.info(f"Lecture du fichier HDFS: {file_path}")
                # Création de la source de données HDFS
                hdfs_file = fs.HadoopFileSystem(HDFS_HOST, HDFS_PORT)
                dataset = pq.ParquetDataset(file_path, filesystem=hdfs_file)
                table = dataset.read()
                df_part = table.to_pandas()
                all_data.append(df_part)
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
                continue
        
        if not all_data:
            logger.warning("Impossible de lire les fichiers Parquet depuis HDFS")
            return jsonify({"error": "Impossible de lire les fichiers de données. Format de données incorrect."}), 500
        
        # Concaténer tous les DataFrames
        df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Données chargées depuis HDFS: {len(df)} objets")
        
        # Conversion en JSON
        objects = df.to_dict('records')
        return jsonify(objects)
    
    except Exception as e:
        logger.error(f"Erreur générale: {str(e)}")
        return jsonify({"error": f"Erreur lors de la récupération des données: {str(e)}"}), 500

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Récupère la liste des objets dangereux."""
    try:
        logger.info(f"Recherche de fichiers dans HDFS: {HDFS_PATH}")
        
        # Connexion à HDFS
        hdfs = fs.HadoopFileSystem(host=HDFS_HOST, port=HDFS_PORT)
        
        # Vérifier si le chemin existe
        if not hdfs.exists(HDFS_PATH):
            logger.warning(f"Le chemin HDFS {HDFS_PATH} n'existe pas")
            return jsonify({"error": "Aucune donnée disponible. Le répertoire HDFS n'existe pas."}), 404
        
        # Lister les fichiers Parquet
        file_selector = fs.FileSelector(HDFS_PATH, recursive=True)
        file_info = hdfs.get_file_info(file_selector)
        parquet_files = [f.path for f in file_info if f.path.endswith('.parquet')]
        
        logger.info(f"Fichiers trouvés dans HDFS: {parquet_files}")
        
        if not parquet_files:
            logger.warning("Aucun fichier Parquet trouvé dans HDFS")
            return jsonify({"error": "Aucun fichier de données trouvé. Vérifiez que Spark Streaming fonctionne correctement."}), 404
        
        # Lire les fichiers Parquet depuis HDFS
        all_data = []
        for file_path in parquet_files:
            try:
                logger.info(f"Lecture du fichier HDFS: {file_path}")
                # Création de la source de données HDFS
                hdfs_file = fs.HadoopFileSystem(HDFS_HOST, HDFS_PORT)
                dataset = pq.ParquetDataset(file_path, filesystem=hdfs_file)
                table = dataset.read()
                df_part = table.to_pandas()
                all_data.append(df_part)
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
                continue
        
        if not all_data:
            logger.warning("Impossible de lire les fichiers Parquet depuis HDFS")
            return jsonify({"error": "Impossible de lire les fichiers de données. Format de données incorrect."}), 500
        
        # Concaténer tous les DataFrames
        df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Données chargées depuis HDFS: {len(df)} objets")
        
        # Filtrage des objets dangereux (en théorie non nécessaire car tous sont déjà dangereux)
        dangerous = df[(df['vitesse'] > 25) & (df['taille'] > 10)]
        logger.info(f"Objets dangereux: {len(dangerous)} sur {len(df)}")
        
        # Conversion en JSON
        alerts = dangerous.to_dict('records')
        return jsonify(alerts)
    
    except Exception as e:
        logger.error(f"Erreur générale: {str(e)}")
        return jsonify({"error": f"Erreur lors de la récupération des données: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)