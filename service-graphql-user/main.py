import strawberry
from flask import Flask
from strawberry.flask.views import GraphQLView
from typing import Optional


# 1. Définition du Modèle de données (Schema)
# Avec Strawberry, on utilise des classes Python normales avec des types
@strawberry.type
class TrafficData:
    road_id: str
    congestion_level: str
    average_speed: int


# 2. Définition des Requêtes (Query)
@strawberry.type
class Query:
    @strawberry.field
    def get_traffic(self, road_id: str) -> Optional[TrafficData]:
        # Simulation de la base de données
        # Simulation trafic Grand Tunis
        traffic_mock_db = {
            "GP9": {"congestion_level": "Saturé", "average_speed": 15},  # Route de la Marsa
            "Route X": {"congestion_level": "Fluide", "average_speed": 70},  # Bardo / Manar
            "Z4": {"congestion_level": "Bloqué", "average_speed": 5},  # Centre-Ville / Sortie Sud
            "X20": {"congestion_level": "Modéré", "average_speed": 40},  # Ennasr / Ariana
            "GP1": {"congestion_level": "Bouché", "average_speed": 20},  # Ben Arous / Mourouj
            "Lac": {"congestion_level": "Fluide", "average_speed": 50}  # Les Berges du Lac
        }

        data = traffic_mock_db.get(road_id)

        if data:
            return TrafficData(
                road_id=road_id,
                congestion_level=data['congestion_level'],
                average_speed=data['average_speed']
            )
        return None


# 3. Création du Schéma global
schema = strawberry.Schema(query=Query)

# 4. Configuration de l'application Flask
app = Flask(__name__)

# Route pour l'interface GraphQL
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema),
)

if __name__ == '__main__':
    print("Serveur GraphQL (Strawberry) démarré sur http://0.0.0.0:5000/graphql")
    # IMPORTANT : host="0.0.0.0" pour Docker !
    app.run(host="0.0.0.0", port=5000, debug=True)