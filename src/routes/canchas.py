from flask import Blueprint, request, jsonify
from src.utils.utils import generar_respuesta_error, construir_links_hateoas
from src.validators.canchas_validators import validar_filtros_listar_canchas, validar_body_crear_cancha
from src.services.canchas_services import listar_canchas_service, crear_cancha_service, RecursoNoEncontradoError

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
