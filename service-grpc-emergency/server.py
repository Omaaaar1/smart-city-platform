import grpc
from concurrent import futures
import time

# Import des fichiers générés automatiquement
import energy_pb2
import energy_pb2_grpc

# Simulation d'une base de données
ENERGY_DB = {
    "Batiment_A": {"kwh": 150.5, "status": "Normal"},
    "Batiment_B": {"kwh": 450.0, "status": "Surcharge"},
    "Batiment_C": {"kwh": 30.2, "status": "Économie"},
}


class EnergyService(energy_pb2_grpc.EnergyServiceServicer):
    def GetEnergyData(self, request, context):
        building_id = request.building_id
        print(f"Demande reçue pour : {building_id}")

        data = ENERGY_DB.get(building_id)

        if data:
            return energy_pb2.EnergyResponse(
                building_id=building_id,
                consumption_kwh=data['kwh'],
                status=data['status']
            )
        else:
            # Si le bâtiment n'existe pas, on renvoie des valeurs par défaut
            return energy_pb2.EnergyResponse(
                building_id=building_id,
                consumption_kwh=0.0,
                status="Inconnu"
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    energy_pb2_grpc.add_EnergyServiceServicer_to_server(EnergyService(), server)

    # Le serveur écoute sur le port 50052
    server.add_insecure_port('localhost:50051')
    print("Serveur gRPC Énergie démarré sur le port 50051...")
    server.start()

    try:
        while True:
            time.sleep(86400)  # Un jour en secondes
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()