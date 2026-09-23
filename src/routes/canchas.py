from flask import Blueprint, request, jsonify
from src.utils.utils import *
from src.validators.canchas_validators import  *
from src.services.canchas_services import *

canchas_bp = Blueprint('canchas', __name__)

@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    try:
        # 1. Validar query params de filtrado y paginación
        filtros, error_msg = validar_filtros_listar_canchas(request.args)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", error_msg, 400)

        # 2. Invocar servicio
        (canchas, total), err_negocio, status = listar_canchas_service(**filtros)

        # 3. Armar parámetros para HATEOAS
        query_params = {}
        if filtros['id_deporte'] is not None:
            query_params['id_deporte'] = filtros['id_deporte']
        if filtros['nombre']:
            query_params['nombre'] = filtros['nombre']
        if filtros['techada'] is not None:
            query_params['techada'] = str(filtros['techada']).lower()
        if filtros['activa'] is not None:
            query_params['activa'] = str(filtros['activa']).lower()

        links = construir_links_hateoas(
            request.base_url,
            query_params,
            total,
            filtros['limit'],
            filtros['offset']
        )

        return jsonify({
            "canchas": canchas,
            "_links": links
        }), 200

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error del servidor", str(e), 500)

@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def consultar_canchas_disponibles():
    try:
        filtros, error_msg = validar_filtros_canchas_disponibles(request.args)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Parámetro o intervalo inválido", error_msg, 400)

        (canchas, total), err_negocio, status = consultar_canchas_disponibles_service(**filtros)

        query_params = {
            'fecha': filtros['fecha'],
            'hora_inicio': filtros['hora_inicio'],
            'hora_fin': filtros['hora_fin']
        }
        if filtros['id_deporte'] is not None:
            query_params['id_deporte'] = filtros['id_deporte']
        if filtros['techada'] is not None:
            query_params['techada'] = str(filtros['techada']).lower()

        links = construir_links_hateoas(
            request.base_url,
            query_params,
            total,
            filtros['limit'],
            filtros['offset']
        )

        return jsonify({
            "canchas": canchas,
            "_links": links
        }), 200

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al consultar canchas disponibles", str(e), 500)

@canchas_bp.route('/canchas', methods=['POST'])
def crear_cancha():
    try:
        data = request.get_json()
        datos_cancha, error_msg = validar_body_crear_cancha(data)
        if error_msg:
            code = "ERROR_VALIDACION"
            msg = "Cuerpo de solicitud vacío" if not data else "Campo obligatorio inválido"
            if "precio_hora" in error_msg:
                msg = "Precio por hora inválido"
            elif "booleano" in error_msg:
                msg = "Campo booleano inválido"
            return generar_respuesta_error(code, msg, error_msg, 400)

        cancha_id, err_negocio, status = crear_cancha_service(**datos_cancha)
        if err_negocio:
            return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Deporte no encontrado", err_negocio, status)

        return "", 201

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al crear la cancha", str(e), 500)
    
@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def obtener_cancha(cancha_id: int):
    try:
        valido, error_msg = validar_id_recurso(cancha_id)
        if not valido:
            return generar_respuesta_error("ERROR_VALIDACION", "ID inválido", error_msg, 400)

        cancha, err_negocio, status = obtener_cancha_por_id_service(cancha_id)
        if err_negocio:
            return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Cancha no encontrada", err_negocio, status)

        return jsonify(cancha), 200

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al obtener la cancha", str(e), 500)

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['PATCH'])
def actualizar_cancha(cancha_id: int):
    try:
        data = request.get_json()
        datos_actualizar, error_msg = validar_body_actualizar_cancha(data)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Actualización inválida", error_msg, 400)

        res, err_negocio, status = actualizar_cancha_service(cancha_id, datos_actualizar)
        if err_negocio:
            return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Cancha no encontrada", err_negocio, status)

        return "", 204

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al actualizar la cancha", str(e), 500)

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['DELETE'])
def eliminar_cancha(cancha_id: int):
    try:
        valido, error_msg = validar_id_recurso(cancha_id)
        if not valido:
            return generar_respuesta_error("ERROR_VALIDACION", "ID inválido", error_msg, 400)

        res, err_negocio, status = eliminar_cancha_service(cancha_id)
        if err_negocio:
            code = "RECURSO_NO_ENCONTRADO" if status == 404 else "CONFLICTO_NEGOCIO"
            msg = "Cancha no encontrada" if status == 404 else "Cancha con reservas asociadas"
            return generar_respuesta_error(code, msg, err_negocio, status)

        return "", 204

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al eliminar la cancha", str(e), 500)