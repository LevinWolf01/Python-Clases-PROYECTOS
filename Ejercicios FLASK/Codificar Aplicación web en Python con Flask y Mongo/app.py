from flask import Flask
import pymongo

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./static/imagenes"

# --- CONEXIÓN A ATLAS ---
# Reemplaza <usuario> y <password> por tus credenciales reales (sin los símbolos < >)
URI_ATLAS = "mongodb+srv://Pers1:12345@cluster0.ckrbifg.mongodb.net/?appName=Cluster0"
miConexion = pymongo.MongoClient(URI_ATLAS)

#========================================================================================================

baseDatos = miConexion["GESTIONPRODUCTOS"]
productos = baseDatos["PRODUCTOS"]

from controladores.controllerProducto import *

if __name__ == "__main__":
    app.run(port=3000, debug=True)