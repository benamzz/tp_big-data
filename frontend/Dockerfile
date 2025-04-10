FROM node:16-alpine

WORKDIR /app

# Copier les fichiers de configuration
COPY package.json .

# Installer les dépendances (cela générera automatiquement package-lock.json)
RUN npm install

# Copier le reste des fichiers
COPY . .

EXPOSE 3000

CMD ["npm", "start"] 