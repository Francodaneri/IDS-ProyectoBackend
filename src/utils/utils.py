from flask import jsonify
from urllib.parse import urlencode

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
