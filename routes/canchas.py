from flask import Blueprint, request, jsonify
from urllib.parse import urlencode
from repositories.canchas_repository import (
    obtener_canchas_db,
    existe_deporte_db,
    crear_cancha_db
)

canchas_bp = Blueprint('canchas', __name__)

def generar_respuesta_error(code, message, description, status_code):
    """Helper para estructurar respuestas de error estandarizadas."""
    return jsonify({
        "errors": [
            {
                "code": code,
                "message": message,
                "level": "error",
                "description": description
            }
        ]
    }), status_code


def construir_links_hateoas(base_url, query_params, total, limit, offset):
    """Genera el objeto _links con navegación HATEOAS (_first, _prev, _next, _last)."""
    def make_url(new_offset):
        params = query_params.copy()
        params['_limit'] = limit
        params['_offset'] = new_offset
        return f"{base_url}?{urlencode(params)}"

    last_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    links = {
        "_first": {"href": make_url(0)},
        "_prev": {"href": make_url(max(0, offset - limit))} if offset > 0 else None,
        "_next": {"href": make_url(offset + limit)} if (offset + limit) < total else None,
        "_last": {"href": make_url(last_offset)}
    }
    return links


@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    try:
        # 1. Paginación por defecto
        limit = request.args.get('_limit', 10, type=int)
        offset = request.args.get('_offset', 0, type=int)

        # 2. Inicializar variables de filtros en None (¡Paso clave para evitar el error!)
        id_deporte = request.args.get('id_deporte', type=int)
        nombre = request.args.get('nombre', type=str)
        techada = None
        activa = None

        # 3. Procesar filtro 'techada' si vino en la URL
        techada_raw = request.args.get('techada')
        if techada_raw is not None:
            if techada_raw.lower() not in ['true', 'false']:
                return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", "El filtro 'techada' debe ser 'true' o 'false'.", 400)
            techada = (techada_raw.lower() == 'true')

        # 4. Procesar filtro 'activa' si vino en la URL
        activa_raw = request.args.get('activa')
        if activa_raw is not None:
            if activa_raw.lower() not in ['true', 'false']:
                return generar_respuesta_error("ERROR_VALIDACION", "Filtro inválido", "El filtro 'activa' debe ser 'true' o 'false'.", 400)
            activa = (activa_raw.lower() == 'true')

        # 5. Llamar al repositorio (ahora 'activa' siempre tendrá un valor: True, False o None)
        canchas, total = obtener_canchas_db(
            id_deporte=id_deporte,
            nombre=nombre,
            techada=techada,
            activa=activa,
            limit=limit,
            offset=offset
        )

        # 6. Armar links HATEOAS y respuesta...
        query_params = {}
        if id_deporte is not None: query_params['id_deporte'] = id_deporte
        if nombre: query_params['nombre'] = nombre
        if techada is not None: query_params['techada'] = str(techada).lower()
        if activa is not None: query_params['activa'] = str(activa).lower()

        links = construir_links_hateoas(request.base_url, query_params, total, limit, offset)

        return jsonify({
            "canchas": canchas,
            "_links": links
        }), 200

    except Exception as e:
        # Devuelve la estructura de error estandarizada 500 Internal Server Error
        return generar_respuesta_error(
            "ERROR_INTERNO",
            "Error del servidor",
            str(e),
            500
        )

@canchas_bp.route('/canchas', methods=['POST'])
def crear_cancha():
    try:
        data = request.get_json()
        if not data:
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Cuerpo de solicitud vacío",
                "Debe enviar un objeto JSON válido.",
                400
            )

        # 1. Validar campos obligatorios
        nombre = data.get('nombre')
        id_deporte = data.get('id_deporte')
        precio_hora = data.get('precio_hora')

        if not nombre or not isinstance(nombre, str) or not nombre.strip():
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Campo obligatorio inválido",
                "El campo 'nombre' no puede estar vacío.",
                400
            )

        if id_deporte is None or not isinstance(id_deporte, int):
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Campo obligatorio inválido",
                "El campo 'id_deporte' debe ser un entero.",
                400
            )

        # El precio por hora debe ser un entero positivo mayor a cero (expresado en centavos) [1, 2]
        if precio_hora is None or not isinstance(precio_hora, int) or precio_hora <= 0:
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Precio por hora inválido",
                "El campo 'precio_hora' debe ser un entero positivo mayor a cero (en centavos).",
                400
            )

        # 2. Validar opcionales y asignación de valores por defecto [3]
        techada = data.get('techada', False)
        if not isinstance(techada, bool):
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Campo booleano inválido",
                "El campo 'techada' debe ser un valor booleano (true/false).",
                400
            )

        activa = data.get('activa', True)
        if not isinstance(activa, bool):
            return generar_respuesta_error(
                "ERROR_VALIDACION",
                "Campo booleano inválido",
                "El campo 'activa' debe ser un valor booleano (true/false).",
                400
            )

        # 3. Verificar que el deporte exista en la DB [2]
        if not existe_deporte_db(id_deporte):
            return generar_respuesta_error(
                "RECURSO_NO_ENCONTRADO",
                "Deporte no encontrado",
                f"No existe ningún deporte registrado con id {id_deporte}.",
                404
            )

        # 4. Insertar la cancha
        cancha_id = crear_cancha_db(
            nombre=nombre.strip(),
            id_deporte=id_deporte,
            precio_hora=precio_hora,
            techada=techada,
            activa=activa
        )

        # Respuesta 201 Created según la especificación OpenAPI [4, 5]
        return "", 201

    except Exception as e:
        return generar_respuesta_error(
            "ERROR_INTERNO",
            "Error al crear la cancha",
            str(e),
            500
        )