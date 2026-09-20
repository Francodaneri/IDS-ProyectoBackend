import re
def validar_filtros_listar_socios(args: dict) -> tuple[dict, str | None]:
    """
    Extrae y valida los parámetros de consulta para el listado de socios.
    Retorna una tupla (filtros_procesados, mensaje_error).
    """
    limit = args.get('_limit', 10, type=int)
    offset = args.get('_offset', 0, type=int)
    nombre = args.get('nombre', type=str)

    activo = None
    activo_raw = args.get('activo')
    if activo_raw is not None:
        if activo_raw.lower() not in ['true', 'false']:
            return {}, "El filtro 'activo' debe ser 'true' o 'false'."
        activo = (activo_raw.lower() == 'true')

    filtros = {
        'limit': limit,
        'offset': offset,
        'nombre': nombre,
        'activo': activo
    }
    return filtros, None


def validar_body_crear_socio(data: dict) -> tuple[dict, str | None]:
    """
    Valida la estructura y restricciones del cuerpo JSON para la creación de un socio.
    Retorna una tupla (datos_limpios, mensaje_error).
    """
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido."

    nombre = data.get('nombre')
    email = data.get('email')

    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        return {}, "El campo 'nombre' no puede estar vacío."

    if not email or not isinstance(email, str) or not email.strip():
        return {}, "El campo 'email' esta vacio."

    email = email.strip().lower()
    patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(patron_email, email):
        return {}, "Formato de 'email' inválido."

    activo = data.get('activo', True)
    if not isinstance(activo, bool):
        return {}, "El campo 'activo' debe ser un valor booleano (true/false)."

    datos_limpios = {
        'nombre': nombre.strip(),
        'email' : email,
        'activo': activo
    }
    return datos_limpios, None

def validar_id_recurso(recurso_id: int) -> tuple[bool, str | None]:
    """Valida que el ID recibido en la ruta sea un entero positivo."""
    if not isinstance(recurso_id, int) or recurso_id <= 0:
        return False, "El identificador del recurso debe ser un entero positivo."
    return True, None


def validar_body_actualizar_socio(data: dict) -> tuple[dict, str | None]:
    """
    Valida los campos del cuerpo JSON para la actualización parcial (PATCH).
    Campos permitidos: nombre, email, activo.
    """
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido con los campos a actualizar."

    campos_permitidos = {'nombre', 'email', 'activo'}
    campos_enviados = set(data.keys())

    # Rechazar si se envían campos desconocidos o no editables (como id_deporte)
    if not campos_enviados.issubset(campos_permitidos):
        no_permitidos = campos_enviados - campos_permitidos
        return {}, f"Los siguientes campos no se pueden modificar o son desconocidos: {', '.join(no_permitidos)}."

    datos_limpios = {}

    if 'nombre' in data:
        nombre = data['nombre']
        if not nombre or not isinstance(nombre, str) or not nombre.strip():
            return {}, "El campo 'nombre' no puede quedar vacío."
        datos_limpios['nombre'] = nombre.strip()

    if 'email' in data:
        email = data['email']
        if not email or not isinstance(email, str) or not email.strip():
            return {}, "El campo 'email' no puede quedar vacío."
        
        email = email.strip().lower()
        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron_email, email):
            return {}, "Formato de 'email' inválido."
        
        datos_limpios['email'] = email

    if 'activo' in data:
        activo = data['activo']
        if not isinstance(activo, bool):
            return {}, "El campo 'activo' debe ser un booleano (true/false)."
        datos_limpios['activo'] = activo

    if not datos_limpios:
        return {}, "Debe incluir al menos un campo válido para actualizar."

    return datos_limpios, None