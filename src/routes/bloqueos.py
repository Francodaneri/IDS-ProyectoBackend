from flask import Blueprint, request, jsonify
from src.utils.utils import *
from src.validators.canchas_validators import *
from src.validators.bloqueos_validators import *
from src.services.bloqueos_services import *

bloqueos_bp = Blueprint('bloqueos', __name__)

@bloqueos_bp.route('/bloqueos', methods=['POST'])
def crear_bloqueo():
    try:
        data = request.get_json()
        datos_bloqueo, error_msg = validar_body_crear_bloqueo(data)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Solicitud inválida", error_msg, 400)

        bloqueo, err_negocio, status = crear_bloqueo_service(**datos_bloqueo)
        if err_negocio:
            code = "RECURSO_NO_ENCONTRADO" if status == 404 else "CONFLICTO_NEGOCIO"
            msg = "Cancha no encontrada" if status == 404 else "Conflicto al crear el bloqueo"
            return generar_respuesta_error(code, msg, err_negocio, status)

        return jsonify(bloqueo), 201

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al crear el bloqueo", str(e), 500)


@bloqueos_bp.route('/bloqueos', methods=['GET'])
def listar_bloqueos():
    try:
        filtros, error_msg = validar_filtros_listar_bloqueos(request.args)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", error_msg, 400)

        (bloqueos, total), err_negocio, status = listar_bloqueos_service(**filtros)
        if err_negocio:
            return generar_respuesta_error("ERROR_NEGOCIO", "Error al listar bloqueos", err_negocio, status)

        query_params = {}
        if filtros['id_cancha'] is not None:
            query_params['id_cancha'] = filtros['id_cancha']
        if filtros['fecha']:
            query_params['fecha'] = filtros['fecha']

        links = construir_links_hateoas(request.base_url, query_params, total, filtros['limit'], filtros['offset'])

        return jsonify({
            "bloqueos": bloqueos,
            "_links": links
        }), 200

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error del servidor", str(e), 500)


@bloqueos_bp.route('/bloqueos/<int:bloqueo_id>', methods=['DELETE'])
def eliminar_bloqueo(bloqueo_id: int):
    try:
        valido, error_msg = validar_id_recurso(bloqueo_id)
        if not valido:
            return generar_respuesta_error("ERROR_VALIDACION", "ID inválido", error_msg, 400)

        res, err_negocio, status = eliminar_bloqueo_service(bloqueo_id)
        if err_negocio:
            return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Bloqueo no encontrado", err_negocio, status)

        return "", 204

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al eliminar el bloqueo", str(e), 500)