import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Kafka
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:29092')
TOPIC = 'space_data'

logger.info(f"Utilisation du broker Kafka: {KAFKA_BROKER}")

# Types d'objets célestes
OBJECT_TYPES = ['astéroïde', 'comète', 'météorite', 'débris spatial']

def generate_space_object():
    """Génère un objet céleste aléatoire."""
    return {
        "id": f"space_{random.randint(10000, 99999)}",
        "timestamp": int(datetime.now().timestamp()),
        "position": {
            "x": random.uniform(-1000, 1000),
            "y": random.uniform(-1000, 1000),
            "z": random.uniform(-1000, 1000)
        },
        "vitesse": random.uniform(5, 35),  # km/s
        "taille": random.uniform(1, 30),   # mètres
        "type": random.choice(OBJECT_TYPES)
    }

def create_producer():
    """Crée un producteur Kafka avec gestion des erreurs."""
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3,
                request_timeout_ms=30000
            )
            return producer
        except Exception as e:
            retry_count += 1
            logger.error(f"Tentative {retry_count}/{max_retries} échouée: {str(e)}")
            if retry_count < max_retries:
                time.sleep(5)  # Attendre 5 secondes avant de réessayer
            else:
                raise

def main():
    logger.info(f"Tentative de connexion à Kafka sur {KAFKA_BROKER}...")
    
    try:
        producer = create_producer()
        logger.info("Producteur connecté avec succès!")

        while True:
            try:
                # Générer et envoyer un objet
                space_object = generate_space_object()
                producer.send(TOPIC, value=space_object)
                logger.info(f"Objet envoyé: {space_object['id']}")
                
                # Attendre entre 1 et 3 secondes
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi: {str(e)}")
                time.sleep(5)  # Attendre avant de réessayer
            
    except KeyboardInterrupt:
        logger.info("Arrêt du producteur...")
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}")
    finally:
        if 'producer' in locals():
            producer.close()

if __name__ == "__main__":
    main() 