# On part de la version légère de Python
FROM python:3.12-slim

# On crée le dossier de travail
WORKDIR /app

# --- ETAPE AJOUTÉE : Installation de Git ---
# On met à jour Linux et on installe git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# On installe les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le code
COPY . .

# On ouvre le port 8001
EXPOSE 8001

# La commande de démarrage
CMD ["python", "main.py"]