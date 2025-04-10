FROM python:3.9-slim

WORKDIR /app

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY producer.py .

# Commande pour lancer le producteur
CMD ["python", "producer.py"] 