from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from zeep import Client
import grpc
import sys
import os
import json

# Import gRPC (Gestion d'erreur si les fichiers manquent)
try:
    import energy_pb2
    import energy_pb2_grpc
except ImportError:
    print("❌ ERREUR : Copiez energy_pb2.py et energy_pb2_grpc.py dans ce dossier !")
    sys.exit(1)

# Création du serveur FastAPI
app = FastAPI(
    title="Smart City Gateway 🏙️",
    description="Point d'entrée unique pour l'Air, le Trafic, la Mobilité et l'Énergie.",
    version="3.0 (AI Integrated)"
)

# --- 1. CONFIGURATION CORS (INDISPENSABLE POUR REACT) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines (dont localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. ADRESSES DES MICROSERVICES ---
SOAP_URL = os.getenv('SOAP_URL', 'http://localhost:8001/?wsdl')
GRAPHQL_URL = os.getenv('GRAPHQL_URL', 'http://localhost:5000/graphql')
REST_URL = os.getenv('REST_URL', 'http://localhost:8002/transports')
GRPC_HOST = os.getenv('GRPC_HOST', '127.0.0.1:50051')

# --- ADRESSE DE L'INTELLIGENCE ARTIFICIELLE (OLLAMA) ---
# IMPORTANT : On utilise ton IP Wi-Fi pour que Docker puisse sortir et parler à Windows
OLLAMA_URL = "http://172.20.10.6:11434/api/generate"

print(f"🔧 CONFIGURATION CHARGÉE :")
print(f"   - SOAP : {SOAP_URL}")
print(f"   - GQL  : {GRAPHQL_URL}")
print(f"   - REST : {REST_URL}")
print(f"   - gRPC : {GRPC_HOST}")
print(f"   - AI   : {OLLAMA_URL}")


# Modèle de données pour le Chat
class ChatRequest(BaseModel):
    question: str


# --- 3. FONCTION D'AIDE : PARLER A OLLAMA ---
def ask_ollama(context, question):
    # NOM EXACT DU MODÈLE (Celui de 'ollama list')
    model_name = "llama3:latest"

    prompt = f"""
    Tu es l'assistant intelligent de Tunis (Smart City).
    Voici les données techniques actuelles : {context}

    L'utilisateur demande : "{question}"

    Réponds-lui de manière naturelle, utile et brève (en français). 
    Si les données indiquent un problème (bouchon, retard), préviens l'utilisateur.
    Base-toi UNIQUEMENT sur les données fournies.
    """
    try:
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        print(f"🧠 Envoi à Ollama ({OLLAMA_URL}) avec le modèle '{model_name}'...")

        # AJOUT DU TIMEOUT (120 secondes) pour éviter que ça coupe si ton PC est lent
        response = requests.post(OLLAMA_URL, json=data, timeout=120)

        # --- DEBUG : On regarde ce que Ollama répond vraiment ---
        if response.status_code == 200:
            json_resp = response.json()
            if "error" in json_resp:
                print(f"❌ OLLAMA A REFUSÉ : {json_resp['error']}")
                return f"Erreur du cerveau : {json_resp['error']}"
            return json_resp['response']
        else:
            print(f"❌ ERREUR HTTP OLLAMA : {response.status_code} - {response.text}")
            return "Je n'arrive pas à joindre l'IA."

    except Exception as e:
        print(f"❌ CRASH PYTHON : {e}")
        return "Je n'arrive pas à joindre mon cerveau IA (Ollama), mais voici les données brutes : " + str(context)


# --- 4. ROUTES CLASSIQUES (POUR LE DASHBOARD) ---

@app.get("/api/air/{city}", tags=["Environnement"])
def get_air_quality(city: str):
    try:
        client = Client(SOAP_URL)
        res = client.service.get_air_quality(city=city)
        return {"data": {"aqi": res.aqi, "status": res.status, "station": res.station}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur SOAP: {str(e)}")


@app.get("/api/traffic/{road_id}", tags=["Transport"])
def get_traffic(road_id: str):
    query = """query($roadId: String!) { getTraffic(roadId: $roadId) { congestionLevel averageSpeed } }"""
    try:
        res = requests.post(GRAPHQL_URL, json={'query': query, 'variables': {"roadId": road_id}})
        if res.status_code == 200:
            data = res.json().get('data', {}).get('getTraffic')
            return {"data": data}
        raise HTTPException(status_code=res.status_code, detail="Erreur GraphQL")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur connexion: {str(e)}")


@app.get("/api/mobility", tags=["Transport"])
def get_public_transports():
    try:
        res = requests.get(REST_URL)
        return {"data": res.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur REST: {str(e)}")


@app.get("/api/energy/{building_id}", tags=["Énergie"])
def get_energy_consumption(building_id: str):
    try:
        with grpc.insecure_channel(GRPC_HOST) as channel:
            stub = energy_pb2_grpc.EnergyServiceStub(channel)
            res = stub.GetEnergyData(energy_pb2.EnergyRequest(building_id=building_id))
            return {"data": {"consumption_kwh": res.consumption_kwh, "status": res.status}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur gRPC: {str(e)}")


# --- 5. ROUTE INTELLIGENTE : CHATBOT GRAND TUNIS 🧠 ---
@app.post("/api/chat", tags=["IA"])
def chat_with_city(request: ChatRequest):
    user_text = request.question.lower()
    context_data = {}

    print(f"📩 Question sur le Grand Tunis : {user_text}")

    # CARTE INTELLIGENTE (Quartier -> Route Principale)
    neighborhood_map = {
        # Banlieue Nord
        "marsa": "GP9", "carthage": "GP9", "goulette": "GP9", "aouina": "GP9", "sidi bou": "GP9",
        # Lac
        "lac": "Lac", "kram": "Lac",
        # Ariana / Menzah / Ennasr
        "ariana": "X20", "ennasr": "X20", "menzah": "X20", "ghazela": "X20",
        # Bardo / Manouba
        "bardo": "Route X", "manouba": "Route X", "campus": "Route X", "manar": "Route X",
        # Banlieue Sud
        "mourouj": "GP1", "rades": "GP1", "ezzahra": "GP1", "hammam lif": "GP1", "ben arous": "GP1",
        # Centre
        "centre": "Z4", "tunis": "Z4", "passage": "Z4"
    }

    # ANALYSE AUTOMATIQUE
    detected_place = None

    # On parcourt la carte
    for place, road in neighborhood_map.items():
        if place in user_text:
            detected_place = place

            # A. Transports (Bus/Metro/TGM) via REST
            try:
                res = requests.get(REST_URL)
                all_transports = res.json()
                relevant = [t for t in all_transports if place in t['destination'].lower()]

                if relevant:
                    context_data[f"Transport vers {place.capitalize()}"] = str(relevant)
                else:
                    context_data[f"Transport vers {place.capitalize()}"] = "Pas de ligne directe trouvée."
            except:
                pass

            # B. Trafic Route Principale via GraphQL
            try:
                query = """query($roadId: String!) { getTraffic(roadId: $roadId) { congestionLevel averageSpeed } }"""
                res = requests.post(GRAPHQL_URL, json={'query': query, 'variables': {"roadId": road}})
                data = res.json().get('data', {}).get('getTraffic')

                if data:
                    context_data[
                        f"Route Principale ({road})"] = f"Vitesse={data['averageSpeed']}km/h, État={data['congestionLevel']}"
            except:
                pass

            # C. Météo (Air) via SOAP - On prend Tunis par défaut
            try:
                client = Client(SOAP_URL)
                res = client.service.get_air_quality(city="Tunis")
                context_data[f"Air sur le Grand Tunis"] = f"AQI={res.aqi}, Status={res.status}"
            except:
                pass

    # SI RIEN TROUVÉ
    if not context_data:
        context_data = "Aucune donnée précise trouvée dans les capteurs. Dis à l'utilisateur que tu gères les zones : Marsa, Lac, Bardo, Centre-Ville, Ennasr, Mourouj..."

    # ENVOI A OLLAMA
    print(f"📊 Données envoyées à l'IA : {context_data}")
    ai_response = ask_ollama(context_data, request.question)

    return {"response": ai_response}


# Lancement
if __name__ == "__main__":
    import uvicorn

    print("🚀 Démarrage de la Gateway sur http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)