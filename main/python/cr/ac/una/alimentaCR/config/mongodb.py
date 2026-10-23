"""
Configuracion de conexion a MongoDB.

MongoDB se utiliza unicamente para la bitacora de eventos del sistema
(coleccion "eventos" en la base de datos "alimentacr_bitacora"), como
parte de la persistencia poliglota descrita en el ADR-002.

Las credenciales y el host se toman de las mismas variables de entorno
definidas en docker-compose.yml (.env), de forma analoga a como
settings.py configura la conexion a PostgreSQL.
"""

from decouple import config
from pymongo import MongoClient

_cliente_mongo = None


def obtener_cliente_mongo():
    """
    Retorna una instancia unica del cliente MongoDB.

    En produccion utiliza MONGODB_URI (MongoDB Atlas).
    En desarrollo utiliza las variables de Docker Compose.
    """
    global _cliente_mongo

    if _cliente_mongo is None:
        mongodb_uri = config("MONGODB_URI", default="")

        if mongodb_uri:
            _cliente_mongo = MongoClient(mongodb_uri)
        else:
            _cliente_mongo = MongoClient(
                host=config("MONGO_HOST", default="localhost"),
                port=config("MONGO_PORT", default=27017, cast=int),
                username=config("MONGO_ROOT_USERNAME"),
                password=config("MONGO_ROOT_PASSWORD"),
                authSource="admin",
            )

    return _cliente_mongo


def obtener_base_datos_bitacora():
    """
    Retorna la base de datos "alimentacr_bitacora", donde vive la
    coleccion "eventos".
    """
    cliente = obtener_cliente_mongo()
    nombre_bd = config("MONGO_DATABASE", default="alimentacr_bitacora")
    return cliente[nombre_bd]