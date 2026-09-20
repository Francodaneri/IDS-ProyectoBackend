from flask import Blueprint, request, jsonify
from src.utils.utils import *
from src.validators.socios_validators import *
from src.services.socios_services import *

socios_bp = Blueprint('socios', __name__)

@socios_bp.route('/socios', methods=['GET'])
def listar_socios():
    try:
        # 1. Validar parámetros de consulta (Query Params)
        filtros, error_msg = validar_filtros_listar_socios(request.args)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", error_msg, 400)

        # 2. Invocar la capa de servicio
        socios, total = listar_socios_service(**filtros)

        # 3. Construir parámetros para la navegación HATEOAS
        query_params = {}
        if filtros['nombre']:
            query_params['nombre'] = filtros['nombre']
        if filtros['activo'] is not None:
            query_params['activo'] = str(filtros['activo']).lower()

        links = construir_links_hateoas(request.base_url, query_params, total, filtros['limit'], filtros['offset'])

        return jsonify({
            "socios": socios,
            "_links": links
        }), 200

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error del servidor", str(e), 500)


@socios_bp.route('/socios', methods=['POST'])
def crear_socio():
    try:
        data = request.get_json()
        
        # 1. Validar cuerpo JSON
        datos_socio, error_msg = validar_body_crear_socio(data)
        if error_msg:
            code = "ERROR_VALIDACION"
            msg = "Cuerpo de solicitud vacío" if not data else "Campo obligatorio inválido"
            if "nombre" in error_msg:
                msg = "Nombre inválido"
            elif "email" in error_msg:
                msg = "Email inválido"
            return generar_respuesta_error(code, msg, error_msg, 400)

        # 2. Ejecutar la lógica de negocio en el servicio
        crear_socio_service(**datos_socio)

        # 3. Respuesta exitosa 201 Created
        return "", 201
    
    except ConflictoNegocioError as e:
        return generar_respuesta_error("CONFLICTO_NEGOCIO", "Correo ya registrado", str(e), 409)
    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al crear el socio", str(e), 500)


@socios_bp.route('/socios/<int:socio_id>', methods=['GET'])
def obtener_socio_id(socio_id: int):
    try:
        # 1. Validar ID
        valido, error_msg = validar_id_recurso(socio_id)
        if not valido:
            return generar_respuesta_error("ERROR_VALIDACION", "ID inválido", error_msg, 400)

        # 2. Invocar servicio
        socio = obtener_socio_por_id_service(socio_id)

        # 3. Responder 200 OK con los datos
        return jsonify(socio), 200

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Socio no encontrado", str(e), 404)
    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al buscar Socio", str(e), 500)


@socios_bp.route('/socios/<int:socio_id>', methods=['PATCH'])
def actualizar_socio_id(socio_id: int):
    try:
        data = request.get_json()

        # 1. Validar cuerpo JSON
        datos_actualizar, error_msg = validar_body_actualizar_socio(data)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Actualización inválida", error_msg, 400)

        # 2. Invocar servicio
        actualizar_socio_service(socio_id, datos_actualizar)

        # 3. Responder 204 No Content sin cuerpo [2, 3]
        return "", 204

    except RecursoNoEncontradoError as e:
        return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Socio no encontrado", str(e), 404)
    except ConflictoNegocioError as e:
        return generar_respuesta_error("CONFLICTO_NEGOCIO", "Correo ya registrado", str(e), 409)
    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al actualizar el Socio", str(e), 500)