import json
import random
import time
from datetime import datetime
from confluent_kafka import Producer
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Kafka
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = 'space_data'

logger.info(f"Utilisation du broker Kafka: {KAFKA_BROKER}")

# Nombre d'objets célestes à générer par intervalle
MIN_OBJECTS = 2
MAX_OBJECTS = 5

# Intervalle de temps entre les générations d'objets (secondes)
GENERATION_INTERVAL = 2

# Probabilité qu'un objet soit dangereux (vitesse > 25 km/s et taille > 10m)
DANGEROUS_PROBABILITY = 0.3

def create_producer():
    """Crée un producteur Kafka."""
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'client.id': 'space-data-producer'
    }
    return Producer(conf)

def generate_object():
    """Génère un objet céleste aléatoire."""
    # Identifiant unique
    obj_id = f"space_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Timestamp actuel
    timestamp = int(datetime.now().timestamp())
    
    # Position dans l'espace
    position = {
        "x": random.uniform(-1000, 1000),  # en unités arbitraires
        "y": random.uniform(-1000, 1000),
        "z": random.uniform(-1000, 1000)
    }
    
    # Vitesse (km/s)
    if random.random() < DANGEROUS_PROBABILITY:
        # Objet potentiellement dangereux: vitesse élevée
        vitesse = random.uniform(25, 35)
    else:
        # Objet normal: vitesse modérée
        vitesse = random.uniform(5, 25)
    
    # Taille (mètres)
    if random.random() < DANGEROUS_PROBABILITY:
        # Objet potentiellement dangereux: grande taille
        taille = random.uniform(10, 20)
    else:
        # Objet normal: taille modérée
        taille = random.uniform(1, 10)
    
    # Type d'objet
    types = ["astéroïde", "comète", "météorite", "débris spatial"]
    types_weights = [0.4, 0.3, 0.2, 0.1]  # Les astéroïdes sont plus communs
    obj_type = random.choices(types, weights=types_weights, k=1)[0]
    
    return {
        "id": obj_id,
        "timestamp": timestamp,
        "position": position,
        "vitesse": vitesse,
        "taille": taille,
        "type": obj_type
    }

def delivery_report(err, msg):
    """Callback appelé pour chaque message produit pour confirmer la livraison."""
    if err is not None:
        print(f"Erreur de livraison: {err}")
    else:
        print(f"Message envoyé à {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

def run_producer():
    """Fonction principale qui génère et envoie des données à Kafka."""
    producer = create_producer()
    
    print(f"Connexion au broker Kafka: {KAFKA_BROKER}")
    print(f"Envoi de données au topic: {KAFKA_TOPIC}")
    print("Génération de données d'objets célestes...")
    
    try:
        while True:
            # Générer un nombre aléatoire d'objets
            num_objects = random.randint(MIN_OBJECTS, MAX_OBJECTS)
            
            for _ in range(num_objects):
                # Générer un objet céleste
                obj = generate_object()
                
                # Convertir en JSON
                value = json.dumps(obj)
                
                # Envoyer à Kafka
                producer.produce(KAFKA_TOPIC, value.encode('utf-8'), callback=delivery_report)
            
            # Flush les messages
            producer.flush()
            
            # Attendre l'intervalle de temps
            time.sleep(GENERATION_INTERVAL)
    
    except KeyboardInterrupt:
        print("Producteur arrêté par l'utilisateur")
    except Exception as e:
        print(f"Erreur dans le producteur: {e}")
    finally:
        # Assurer que tous les messages sont envoyés avant de terminer
        producer.flush()
        print("Producteur terminé")

if __name__ == "__main__":
    run_producer() 