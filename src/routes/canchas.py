from flask import Blueprint, request, jsonify
from datetime import datetime

from src.utils.utils import *
from src.validators.canchas_validators import *
from src.services.canchas_services import *

canchas_bp = Blueprint('canchas', __name__)

@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    try:
        # 1. Validar parámetros de consulta (Query Params)
        filtros, error_msg = validar_filtros_listar_canchas(request.args)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", error_msg, 400)

        # 2. Invocar la capa de servicio
        canchas, total = listar_canchas_service(**filtros)

        # 3. Construir parámetros para la navegación HATEOAS
        query_params = {}
        if filtros['id_deporte'] is not None:
            query_params['id_deporte'] = filtros['id_deporte']
        if filtros['nombre']:
            query_params['nombre'] = filtros['nombre']
        if filtros['techada'] is not None:
            query_params['techada'] = str(filtros['techada']).lower()
        if filtros['activa'] is not None:
            query_params['activa'] = str(filtros['activa']).lower()

        links = construir_links_hateoas(request.base_url, query_params, total, filtros['limit'], filtros['offset'])

        return jsonify({
            "canchas": canchas,
            "_links": links
        }), 200

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error del servidor", str(e), 500)


@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def consultar_canchas_disponibles():
    try:
        fecha = request.args.get('fecha')
        hora_inicio = request.args.get('hora_inicio')
        hora_fin = request.args.get('hora_fin')

        if not fecha or not hora_inicio or not hora_fin:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "Parametros obligatorios faltantes",
                "debe indicar fecha, hora de inicio y hora de fin", 400
            )

        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "La fecha ingresada es invalida",
                "debe indicar la fecha en formato YYYY-MM-DD", 400
            )

        try:
            inicio = datetime.strptime(f"{fecha} {hora_inicio}", '%Y-%m-%d %H:%M:%S')
            fin = datetime.strptime(f"{fecha} {hora_fin}", '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "La hora ingresada es invalida",
                "la hora indicada debe tener un formato HH:MM:SS", 400
            )

        if inicio >= fin:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "La hora ingresada es invalida",
                "la hora de fin no puede ser menor a la hora de inicio", 400
            )

        id_deporte = request.args.get('id_deporte')
        techada = request.args.get('techada')
        if techada is not None and techada.lower() not in ['true', 'false']:
            return generar_respuesta_error(
                "ERROR_VALIDACION", "El valor del filtro techada, es invalido",
                "Techada, debe ser True o False", 400
            )

        canchas, total = consultar_canchas_disponibles_service(
            fecha, hora_inicio, hora_fin, id_deporte, techada
        )

        query_params = {
            'fecha': fecha,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin
        }
        if id_deporte is not None:
            query_params['id_deporte'] = id_deporte
        if techada is not None:
            query_params['techada'] = techada.lower()

        links = construir_links_hateoas(request.base_url, query_params, total, total, 0)
        return jsonify({"canchas": canchas, "_links": links}), 200

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO", "Error al consultar canchas disponibles", str(e), 500
        )


@canchas_bp.route('/canchas', methods=['POST'])
def crear_cancha():
    try:
        data = request.get_json()
        
        # 1. Validar cuerpo JSON
        datos_cancha, error_msg = validar_body_crear_cancha(data)
        if error_msg:
            code = "ERROR_VALIDACION"
            msg = "Cuerpo de solicitud vacío" if not data else "Campo obligatorio inválido"
            if "precio_hora" in error_msg:
                msg = "Precio por hora inválido"
            elif "booleano" in error_msg:
                msg = "Campo booleano inválido"
            return generar_respuesta_error(code, msg, error_msg, 400)

        # 2. Ejecutar la lógica de negocio en el servicio
        crear_cancha_service(**datos_cancha)

        # 3. Respuesta exitosa 201 Created
        return "", 201

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Deporte no encontrado", str(e), 404)
    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al crear la cancha", str(e), 500)

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def obtener_cancha(cancha_id: int):
    try:
        # 1. Validar ID
        valido, error_msg = validar_id_recurso(cancha_id)
        if not valido:
            return generar_respuesta_error("ERROR_VALIDACION", "ID inválido", error_msg, 400)

        # 2. Invocar servicio
        cancha = obtener_cancha_por_id_service(cancha_id)

        # 3. Responder 200 OK con los datos
        return jsonify(cancha), 200

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Cancha no encontrada", str(e), 404)
    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al obtener la cancha", str(e), 500)

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['PATCH'])
def actualizar_cancha(cancha_id: int):
    try:
        data = request.get_json()

        # 1. Validar cuerpo JSON
        datos_actualizar, error_msg = validar_body_actualizar_cancha(data)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Actualización inválida", error_msg, 400)

        # 2. Invocar servicio
        actualizar_cancha_service(cancha_id, datos_actualizar)

        # 3. Responder 204 No Content sin cuerpo [2, 3]
        return "", 204

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Cancha no encontrada", str(e), 404)
    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al actualizar la cancha", str(e), 500)

@canchas_bp.route('/canchas/<int:cancha_id>', methods=['DELETE'])
def eliminar_cancha(cancha_id: int):
    try:
        # 1. Invocar servicio para validar reservas e instruir la eliminación
        eliminar_cancha_service(cancha_id)

        # 2. Responder 204 No Content sin cuerpo [2, 3]
        return "", 204

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Cancha no encontrada", str(e), 404)
    except ConflictoNegocioError as e:
        return generar_respuesta_error("CONFLICTO_NEGOCIO", "Cancha con reservas asociadas", str(e), 409)
    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al eliminar la cancha", str(e), 500)

