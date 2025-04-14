FROM python:3.9-slim

WORKDIR /app

# Installer Java et les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    default-jdk \
    wget \
    curl \
    procps \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Définir JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Télécharger et installer Hadoop
RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-3.2.1/hadoop-3.2.1.tar.gz && \
    tar -xzf hadoop-3.2.1.tar.gz -C /opt/ && \
    rm hadoop-3.2.1.tar.gz

# Configurer les variables d'environnement pour Hadoop
ENV HADOOP_HOME=/opt/hadoop-3.2.1
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV HADOOP_OPTS="$HADOOP_OPTS -Djava.library.path=$HADOOP_HOME/lib/native"
ENV CLASSPATH=$HADOOP_CONF_DIR:$HADOOP_HOME/share/hadoop/common/lib/*:$HADOOP_HOME/share/hadoop/common/*:$HADOOP_HOME/share/hadoop/hdfs/*:$HADOOP_HOME/share/hadoop/hdfs/lib/*:$HADOOP_HOME/share/hadoop/mapreduce/*:$HADOOP_HOME/share/hadoop/yarn/*

# S'assurer que les scripts ont les permissions d'exécution
RUN chmod -R +x $HADOOP_HOME/bin $HADOOP_HOME/sbin

# Créer le répertoire de configuration
RUN mkdir -p $HADOOP_CONF_DIR

# Configurer HDFS avec la bonne balise XML
RUN echo '<?xml version="1.0" encoding="UTF-8"?>' > $HADOOP_CONF_DIR/core-site.xml && \
    echo '<configuration>' >> $HADOOP_CONF_DIR/core-site.xml && \
    echo '    <property>' >> $HADOOP_CONF_DIR/core-site.xml && \
    echo '        <name>fs.defaultFS</name>' >> $HADOOP_CONF_DIR/core-site.xml && \
    echo '        <value>hdfs://hadoop-namenode:9000</value>' >> $HADOOP_CONF_DIR/core-site.xml && \
    echo '    </property>' >> $HADOOP_CONF_DIR/core-site.xml && \
    echo '</configuration>' >> $HADOOP_CONF_DIR/core-site.xml

# Créer l'environnement virtuel Python
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "app.py"] 