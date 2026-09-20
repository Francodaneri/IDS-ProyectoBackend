from flask import Blueprint, request, jsonify
from src.utils.utils import generar_respuesta_error, construir_links_hateoas
from src.validators.reservas_validators import (
    validar_filtros_listar_reservas,
    validar_body_crear_reserva,
    validar_body_cambiar_estado,
    validar_id_recurso
)
from src.services.reservas_services import (
    crear_reserva_service,
    obtener_reserva_por_id_service,
    listar_reservas_service,
    cambiar_estado_reserva_service,
    RecursoNoEncontradoError,
    ConflictoNegocioError
)

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/reservas', methods=['GET'])
def listar_reservas():
    try:
        filtros, error_msg = validar_filtros_listar_reservas(request.args)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", error_msg, 400)

        reservas, total = listar_reservas_service(**filtros)

        query_params = {}
        if filtros['id_cancha'] is not None:
            query_params['id_cancha'] = filtros['id_cancha']
        if filtros['id_socio'] is not None:
            query_params['id_socio'] = filtros['id_socio']
        if filtros['estado']:
            query_params['estado'] = filtros['estado']
        if filtros['fecha_desde']:
            query_params['fecha_desde'] = filtros['fecha_desde']
        if filtros['fecha_hasta']:
            query_params['fecha_hasta'] = filtros['fecha_hasta']

        links = construir_links_hateoas(
            request.base_url,
            query_params,
            total,
            filtros['limit'],
            filtros['offset']
        )

        return jsonify({
            "reservas": reservas,
            "_links": links
        }), 200

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO",
            "Error del servidor",
            str(e),
            500
        )

@reservas_bp.route('/reservas', methods=['POST'])
def crear_reserva():
    try:
        data = request.get_json()

        datos_reserva, error_msg = validar_body_crear_reserva(data)
        if error_msg:
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Solicitud inválida",
                error_msg,
                400
            )

        reserva_id = crear_reserva_service(**datos_reserva)
        reserva_creada = obtener_reserva_por_id_service(reserva_id)

        return jsonify(reserva_creada), 201

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error(
            "RECURSO_NO_ENCONTRADO",
            "Recurso no encontrado",
            str(e),
            404
        )

    except ConflictoNegocioError as e:
        return generar_respuesta_error(
            "CONFLICTO_NEGOCIO",
            "Conflicto al crear la reserva",
            str(e),
            409
        )

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO",
            "Error al crear la reserva",
            str(e),
            500
        )

@reservas_bp.route('/reservas/<int:reserva_id>', methods=['GET'])
def obtener_reserva_por_id(reserva_id: int):
    try:
        valido, error_msg = validar_id_recurso(reserva_id)
        if not valido:
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "ID inválido",
                error_msg,
                400
            )

        reserva = obtener_reserva_por_id_service(reserva_id)
        return jsonify(reserva), 200

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error(
            "RECURSO_NO_ENCONTRADO",
            "Reserva no encontrada",
            str(e),
            404
        )

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO",
            "Error al buscar la reserva",
            str(e),
            500
        )

@reservas_bp.route('/reservas/<int:reserva_id>/estado', methods=['PUT'])
def actualizar_estado_reserva(reserva_id: int):
    try:
        valido, error_msg = validar_id_recurso(reserva_id)
        if not valido:
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "ID inválido",
                error_msg,
                400
            )

        data = request.get_json()
        datos_estado, error_msg = validar_body_cambiar_estado(data)
        if error_msg:
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Estado inválido",
                error_msg,
                400
            )

        reserva_actualizada = cambiar_estado_reserva_service(reserva_id, datos_estado['estado'])

        return jsonify(reserva_actualizada), 200

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error(
            "RECURSO_NO_ENCONTRADO",
            "Reserva no encontrada",
            str(e),
            404
        )

    except ConflictoNegocioError as e:
        return generar_respuesta_error(
            "CONFLICTO_NEGOCIO",
            "Transición de estado no permitida",
            str(e),
            409
        )

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO",
            "Error al actualizar la reserva",
            str(e),
            500
        )