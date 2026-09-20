def validar_filtros_listar_reservas(args: dict) -> tuple[dict, str | None]:
    try:
        limit = args.get('_limit', 10, type=int)
        offset = args.get('_offset', 0, type=int)
    except Exception:
        return {}, "Los parámetros '_limit' y '_offset' deben ser valores numéricos enteros."

    if limit is not None and (limit < 1 or limit > 100):
        return {}, "El parámetro '_limit' debe ser un entero entre 1 y 100."

    if offset is not None and offset < 0:
        return {}, "El parámetro '_offset' debe ser un entero mayor o igual a cero."

    id_cancha = args.get('id_cancha', type=int)
    id_socio = args.get('id_socio', type=int)
    estado = args.get('estado', type=str)
    fecha_desde = args.get('fecha_desde', type=str)
    fecha_hasta = args.get('fecha_hasta', type=str)

    estados_validos = {'confirmada', 'cancelada', 'finalizada'}
    if estado and estado not in estados_validos:
        return {}, f"El filtro 'estado' debe ser uno de: {', '.join(estados_validos)}."

    if fecha_desde and fecha_hasta:
        if fecha_desde[:10] > fecha_hasta[:10]:
            return {}, "El filtro 'fecha_desde' debe ser menor o igual que 'fecha_hasta'."

    filtros = {
        'limit': limit if limit is not None else 10,
        'offset': offset if offset is not None else 0,
        'id_cancha': id_cancha,
        'id_socio': id_socio,
        'estado': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    }
    return filtros, None

def validar_body_crear_reserva(data: dict) -> tuple[dict, str | None]:
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido."

    campos_permitidos = {'id_socio', 'id_cancha', 'fecha_hora_inicio', 'fecha_hora_fin'}
    campos_enviados = set(data.keys())

    desconocidos_o_prohibidos = campos_enviados - campos_permitidos
    if desconocidos_o_prohibidos:
        return {}, f"Los siguientes campos son desconocidos o no deben enviarse: {', '.join(desconocidos_o_prohibidos)}."

    id_socio = data.get('id_socio')
    id_cancha = data.get('id_cancha')
    fecha_hora_inicio = data.get('fecha_hora_inicio')
    fecha_hora_fin = data.get('fecha_hora_fin')

    if id_socio is None or not isinstance(id_socio, int) or id_socio <= 0:
        return {}, "El campo 'id_socio' es obligatorio y debe ser un entero positivo."

    if id_cancha is None or not isinstance(id_cancha, int) or id_cancha <= 0:
        return {}, "El campo 'id_cancha' es obligatorio y debe ser un entero positivo."

    if not fecha_hora_inicio or not isinstance(fecha_hora_inicio, str):
        return {}, "El campo 'fecha_hora_inicio' es obligatorio y debe ser un texto en formato ISO 8601."

    if not fecha_hora_fin or not isinstance(fecha_hora_fin, str):
        return {}, "El campo 'fecha_hora_fin' es obligatorio y debe ser un texto en formato ISO 8601."

    datos_limpios = {
        'id_socio': id_socio,
        'id_cancha': id_cancha,
        'fecha_hora_inicio': fecha_hora_inicio.strip(),
        'fecha_hora_fin': fecha_hora_fin.strip()
    }
    return datos_limpios, None

def validar_body_cambiar_estado(data: dict) -> tuple[dict, str | None]:
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido."

    campos_permitidos = {'estado'}
    campos_enviados = set(data.keys())
    desconocidos = campos_enviados - campos_permitidos
    if desconocidos:
        return {}, f"Se encontraron campos desconocidos no permitidos: {', '.join(desconocidos)}."

    estado = data.get('estado')
    estados_validos = {'confirmada', 'cancelada', 'finalizada'}

    if not estado or not isinstance(estado, str) or estado not in estados_validos:
        return {}, f"El campo 'estado' es obligatorio y debe ser uno de: {', '.join(estados_validos)}."

    return {'estado': estado}, None

def validar_id_recurso(recurso_id: int) -> tuple[bool, str | None]:
    if not isinstance(recurso_id, int) or recurso_id <= 0:
        return False, "El identificador del recurso debe ser un entero positivo."
    return True, None