from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Service Mobilité (REST)", version="1.0")

# 1. Modèle de données (Pydantic)
class Transport(BaseModel):
    id: int
    type: str       # "Bus", "Metro"
    ligne: str      # "28D", "M1"
    destination: str
    status: str     # "A l'heure", "Retard"

# 2. Base de données simulée (Liste en mémoire)
# 2. Base de données simulée (Grand Tunis)
db_transports = [
    # Banlieue Nord (Marsa / Carthage)
    Transport(id=1, type="TGM", ligne="Nord", destination="La Marsa", status="Opérationnel"),
    Transport(id=2, type="Bus", ligne="20b", destination="Gammarth", status="Retard 15min"),
    Transport(id=3, type="TGM", ligne="Nord", destination="Carthage", status="A l'heure"),

    # Centre / Banlieue Ouest (Bardo / Manouba)
    Transport(id=4, type="Metro", ligne="4", destination="Bardo", status="A l'heure"),
    Transport(id=5, type="Metro", ligne="4", destination="Manouba", status="Saturé"),
    Transport(id=6, type="Bus", ligne="33", destination="Mourouj", status="Bouchons"),

    # Banlieue Sud (Rades / Hamam Lif)
    Transport(id=7, type="Train", ligne="Banlieue", destination="Rades", status="Retard 10min"),
    Transport(id=8, type="Train", ligne="Banlieue", destination="Hammam Lif", status="Annulé"),

    # Ariana / Menzah
    Transport(id=9, type="Metro", ligne="2", destination="Ariana", status="A l'heure"),
    Transport(id=10, type="Bus", ligne="63", destination="Menzah", status="A l'heure"),

    # Berges du Lac
    Transport(id=11, type="Bus", ligne="28D", destination="Lac 2", status="Fluide")
]

# --- Opérations CRUD (Create, Read, Update, Delete) ---

# READ ALL
@app.get("/transports", response_model=List[Transport])
def get_transports():
    return db_transports

# READ ONE
@app.get("/transports/{transport_id}", response_model=Transport)
def get_transport_by_id(transport_id: int):
    # Recherche dans la liste
    for t in db_transports:
        if t.id == transport_id:
            return t
    raise HTTPException(status_code=404, detail="Transport non trouvé")

# CREATE
@app.post("/transports", response_model=Transport)
def add_transport(transport: Transport):
    db_transports.append(transport)
    return transport

# DELETE
@app.delete("/transports/{transport_id}")
def delete_transport(transport_id: int):
    global db_transports
    # On garde tous les transports SAUF celui qu'on veut supprimer
    db_transports = [t for t in db_transports if t.id != transport_id]
    return {"message": "Transport supprimé"}

if __name__ == "__main__":
    print("Démarrage du service REST sur le port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)