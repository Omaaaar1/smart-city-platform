import sys
import time
import grpc
import requests
from zeep import Client

# Import des fichiers gRPC
try:
    import energy_pb2
    import energy_pb2_grpc
except ImportError:
    print("❌ ERREUR : Manque energy_pb2.py et energy_pb2_grpc.py")
    sys.exit(1)

# --- CONFIGURATION DES PORTS ---
SOAP_URL = 'http://localhost:8001/?wsdl'
GRAPHQL_URL = 'http://localhost:5000/graphql'
REST_URL = 'http://localhost:8002/transports'# L'adresse de ton service REST
GRPC_HOST = '127.0.0.1:50051'


# --- 1. SOAP (Air) ---
def check_air_soap(city):
    print(f"\n☁️  [SOAP] Service Air ({city})...")
    try:
        client = Client(SOAP_URL)
        res = client.service.get_air_quality(city=city)
        print(f"    ✅ AQI: {res.aqi} | Status: {res.status}")
    except Exception as e:
        print(f"    ❌ Erreur SOAP: {e}")


# --- 2. GRAPHQL (Trafic) ---
def check_traffic_graphql(road_id):
    print(f"\n🚗  [GraphQL] Service Trafic ({road_id})...")
    query = """
    query($roadId: String!) {
      getTraffic(roadId: $roadId) {
        congestionLevel
        averageSpeed
      }
    }
    """
    try:
        res = requests.post(GRAPHQL_URL, json={'query': query, 'variables': {"roadId": road_id}})
        if res.status_code == 200:
            data = res.json().get('data', {}).get('getTraffic')
            if data:
                print(f"    ✅ Vitesse: {data['averageSpeed']} km/h | État: {data['congestionLevel']}")
        else:
            print(f"    ❌ Erreur GraphQL: {res.status_code}")
    except Exception as e:
        print(f"    ❌ Erreur Connexion GraphQL: {e}")


# --- 3. REST (Mobilité) ---
def check_mobility_rest(destination):
    print(f"\n🚲  [REST] Service Mobilité ({destination})...")
    try:
        # On appelle l'URL REST.
        # Si ton service attend un paramètre, adapte l'URL (ex: f"{REST_URL}/{destination}")
        # Ici on fait un appel simple pour tester la connexion
        res = requests.get(REST_URL)

        if res.status_code == 200:
            # On suppose que le REST renvoie du JSON
            try:
                data = res.json()
                print(f"    ✅ Réponse REST : {data}")
            except:
                print(f"    ✅ Réponse REST (Texte) : {res.text}")
        else:
            print(f"    ⚠️  Service joint mais erreur HTTP {res.status_code}")
            print(f"        (Vérifie que l'URL '{REST_URL}' est la bonne)")
    except Exception as e:
        print(f"    ❌ Erreur Connexion REST: {e}")


# --- 4. gRPC (Énergie) ---
def check_energy_grpc(building_id):
    print(f"\n⚡  [gRPC] Service Énergie ({building_id})...")
    try:
        with grpc.insecure_channel(GRPC_HOST) as channel:
            stub = energy_pb2_grpc.EnergyServiceStub(channel)
            res = stub.GetEnergyData(energy_pb2.EnergyRequest(building_id=building_id))
            print(f"    ✅ Conso: {res.consumption_kwh} kWh | Status: {res.status}")
    except Exception as e:
        print(f"    ❌ Erreur gRPC: {e}")


# --- Lancement ---
if __name__ == "__main__":
    print("==================================================")
    print("🤖  SMART CITY AI ORCHESTRATOR - TEST GLOBAL (4 SERVICES)")
    print("==================================================")

    check_air_soap("Paris")
    time.sleep(0.5)

    check_traffic_graphql("A1")
    time.sleep(0.5)

    # VOICI LA LIGNE QUI MANQUAIT :
    check_mobility_rest("Centre-Ville")
    time.sleep(0.5)

    check_energy_grpc("Batiment_A")

    print("\n==================================================")
    print("🏁  FIN DU DIAGNOSTIC")