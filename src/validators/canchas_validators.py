def validar_filtros_listar_canchas(args: dict) -> tuple[dict, str | None]:
    """
    Extrae y valida los parámetros de consulta para el listado de canchas [2, 3, 5].
    Retorna una tupla (filtros_procesados, mensaje_error).
    """
    limit = args.get('_limit', 10, type=int)
    offset = args.get('_offset', 0, type=int)
    id_deporte = args.get('id_deporte', type=int)
    nombre = args.get('nombre', type=str)

    techada = None
    techada_raw = args.get('techada')
    if techada_raw is not None:
        if techada_raw.lower() not in ['true', 'false']:
            return {}, "El filtro 'techada' debe ser 'true' o 'false'."
        techada = (techada_raw.lower() == 'true')

    activa = None
    activa_raw = args.get('activa')
    if activa_raw is not None:
        if activa_raw.lower() not in ['true', 'false']:
            return {}, "El filtro 'activa' debe ser 'true' o 'false'."
        activa = (activa_raw.lower() == 'true')

    filtros = {
        'limit': limit,
        'offset': offset,
        'id_deporte': id_deporte,
        'nombre': nombre,
        'techada': techada,
        'activa': activa
    }
    return filtros, None


def validar_body_crear_cancha(data: dict) -> tuple[dict, str | None]:
    """
    Valida la estructura y restricciones del cuerpo JSON para la creación de una cancha [4-6].
    Retorna una tupla (datos_limpios, mensaje_error).
    """
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido."

    nombre = data.get('nombre')
    id_deporte = data.get('id_deporte')
    precio_hora = data.get('precio_hora')

    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        return {}, "El campo 'nombre' no puede estar vacío."

    if id_deporte is None or not isinstance(id_deporte, int):
        return {}, "El campo 'id_deporte' debe ser un entero."

    if precio_hora is None or not isinstance(precio_hora, int) or precio_hora <= 0:
        return {}, "El campo 'precio_hora' debe ser un entero positivo mayor a cero (en centavos)."

    techada = data.get('techada', False)
    if not isinstance(techada, bool):
        return {}, "El campo 'techada' debe ser un valor booleano (true/false)."

    activa = data.get('activa', True)
    if not isinstance(activa, bool):
        return {}, "El campo 'activa' debe ser un valor booleano (true/false)."

    datos_limpios = {
        'nombre': nombre.strip(),
        'id_deporte': id_deporte,
        'precio_hora': precio_hora,
        'techada': techada,
        'activa': activa
    }
    return datos_limpios, None

def validar_id_recurso(recurso_id: int) -> tuple[bool, str | None]:
    """Valida que el ID recibido en la ruta sea un entero positivo."""
    if not isinstance(recurso_id, int) or recurso_id <= 0:
        return False, "El identificador del recurso debe ser un entero positivo."
    return True, None


def validar_body_actualizar_cancha(data: dict) -> tuple[dict, str | None]:
    """
    Valida los campos del cuerpo JSON para la actualización parcial (PATCH) [1, 5].
    Campos permitidos: nombre, precio_hora, techada, activa.
    Nota: El id_deporte no puede ser modificado una vez creada la cancha [1].
    """
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido con los campos a actualizar."

    campos_permitidos = {'nombre', 'precio_hora', 'techada', 'activa'}
    campos_enviados = set(data.keys())

    # Rechazar si se envían campos desconocidos o no editables (como id_deporte) [1, 6]
    if not campos_enviados.issubset(campos_permitidos):
        no_permitidos = campos_enviados - campos_permitidos
        return {}, f"Los siguientes campos no se pueden modificar o son desconocidos: {', '.join(no_permitidos)}."

    datos_limpios = {}

    if 'nombre' in data:
        nombre = data['nombre']
        if not nombre or not isinstance(nombre, str) or not nombre.strip():
            return {}, "El campo 'nombre' no puede quedar vacío."
        datos_limpios['nombre'] = nombre.strip()

    if 'precio_hora' in data:
        precio_hora = data['precio_hora']
        if not isinstance(precio_hora, int) or precio_hora <= 0:
            return {}, "El campo 'precio_hora' debe ser un entero positivo mayor a cero (en centavos)."
        datos_limpios['precio_hora'] = precio_hora

    if 'techada' in data:
        techada = data['techada']
        if not isinstance(techada, bool):
            return {}, "El campo 'techada' debe ser un booleano (true/false)."
        datos_limpios['techada'] = techada

    if 'activa' in data:
        activa = data['activa']
        if not isinstance(activa, bool):
            return {}, "El campo 'activa' debe ser un booleano (true/false)."
        datos_limpios['activa'] = activa

    if not datos_limpios:
        return {}, "Debe incluir al menos un campo válido para actualizar."

    return datos_limpios, None