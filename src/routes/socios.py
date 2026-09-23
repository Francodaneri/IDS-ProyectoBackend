from flask import Blueprint, request, jsonify
from src.utils.utils import *
from src.validators.socios_validators import *
from src.services.socios_services import *

socios_bp = Blueprint('socios', __name__)

@socios_bp.route('/socios', methods=['GET'])
def listar_socios():
    try:
        filtros, error_msg = validar_filtros_listar_socios(request.args)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", error_msg, 400)

        (socios, total), err_negocio, status = listar_socios_service(**filtros)

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
        datos_socio, error_msg = validar_body_crear_socio(data)
        if error_msg:
            code = "ERROR_VALIDACION"
            msg = "Cuerpo de solicitud vacío" if not data else "Campo obligatorio inválido"
            if "nombre" in error_msg:
                msg = "Nombre inválido"
            elif "email" in error_msg:
                msg = "Email inválido"
            return generar_respuesta_error(code, msg, error_msg, 400)

        socio_id, err_negocio, status = crear_socio_service(**datos_socio)
        if err_negocio:
            return generar_respuesta_error("CONFLICTO_NEGOCIO", "Correo ya registrado", err_negocio, status)

        return "", 201

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al crear el socio", str(e), 500)

@socios_bp.route('/socios/<int:socio_id>', methods=['GET'])
def obtener_socio_id(socio_id: int):
    try:
        valido, error_msg = validar_id_recurso(socio_id)
        if not valido:
            return generar_respuesta_error("ERROR_VALIDACION", "ID inválido", error_msg, 400)

        socio, err_negocio, status = obtener_socio_por_id_service(socio_id)
        if err_negocio:
            return generar_respuesta_error("RECURSO_NO_ENCONTRADO", "Socio no encontrado", err_negocio, status)

        return jsonify(socio), 200

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al buscar Socio", str(e), 500)

@socios_bp.route('/socios/<int:socio_id>', methods=['PATCH'])
def actualizar_socio_id(socio_id: int):
    try:
        data = request.get_json()
        datos_actualizar, error_msg = validar_body_actualizar_socio(data)
        if error_msg:
            return generar_respuesta_error("ERROR_VALIDACION", "Actualización inválida", error_msg, 400)

        res, err_negocio, status = actualizar_socio_id_service(socio_id, datos_actualizar)
        if err_negocio:
            code = "RECURSO_NO_ENCONTRADO" if status == 404 else "CONFLICTO_NEGOCIO"
            msg = "Socio no encontrado" if status == 404 else "Correo ya registrado"
            return generar_respuesta_error(code, msg, err_negocio, status)

        return "", 204

    except Exception as e:
        return generar_respuesta_error("ERROR_INTERNO", "Error al actualizar el Socio", str(e), 500)