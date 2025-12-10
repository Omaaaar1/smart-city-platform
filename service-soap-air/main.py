import logging
# On utilise wsgiref pour créer un serveur web simple
from wsgiref.simple_server import make_server

# Importations de Spyne (la librairie SOAP)
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

# Configuration des logs pour voir les erreurs
logging.basicConfig(level=logging.DEBUG)


# Modèle de données : À quoi ressemble une "Réponse Air" ?
class AirData(ComplexModel):
    station = Unicode
    aqi = Integer  # Air Quality Index
    co2 = Float  # Niveau CO2
    status = Unicode  # "Bon", "Moyen", "Dangereux"


# Définition du Service (La logique métier)
class AirQualityService(ServiceBase):
    @rpc(Unicode, _returns=AirData)
    def get_air_quality(ctx, city):
        print(f"Demande reçue pour la ville : {city}")

        # Petite base de données simulée
        city_db = {
            "Tunis": {"aqi": 55, "co2": 410.5, "status": "Moyen"},
            "Marsa": {"aqi": 25, "co2": 380.0, "status": "Excellent"},
            "Carthage": {"aqi": 30, "co2": 385.2, "status": "Bon"},
            "Bardo": {"aqi": 110, "co2": 500.1, "status": "Pollué"},
            "Sfax": {"aqi": 140, "co2": 600.0, "status": "Très Pollué"},
        }

        # On cherche la ville (en ignorant majuscules/minuscules)
        data = None
        for key in city_db:
            if key.lower() == city.lower():
                data = city_db[key]
                break

        if data:
            return AirData(
                station=f"Capteur {city}",
                aqi=data['aqi'],
                co2=data['co2'],
                status=data['status']
            )
        else:
            # Valeur par défaut si ville inconnue
            return AirData(
                station="Inconnue",
                aqi=0,
                co2=0.0,
                status="Données non disponibles"
            )

# Création de l'application SOAP
application = Application(
    [AirQualityService],
    tns='smartcity.air',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

# Transformation en application Web WSGI
wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    port = 8001
    print(f"Serveur SOAP démarré sur http://0.0.0.0:{port}")
    print(f"WSDL disponible à : http://localhost:{port}/?wsdl")

    server = make_server('0.0.0.0', port, wsgi_application)
    server.serve_forever()