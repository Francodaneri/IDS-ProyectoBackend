from flask import Blueprint, jsonify
from src.utils.utils import (generar_respuesta_error,construir_links_hateoas)
from src.repositories.deporte_repository import obtener_deportes_desde_db

deportes_bp = Blueprint('deportes', __name__)

@deportes_bp.route('/deportes', methods=['GET'])
def listar_deportes():
    try:
        deportes = obtener_deportes_desde_db()
        # Devuelve respuesta exitosa 200 OK con el esquema DeportesListResponse
        return jsonify({"deportes": deportes}), 200
    except Exception as e:
        # Devuelve la estructura de error estandarizada 500 Internal Server Error
        return generar_respuesta_error(
                    "ERROR_INTERNO",
                    "Error al obtener la lista de deportes",
                    str(e),
                    500
                )