import re
from datetime import datetime, timezone, timedelta

TZ_ARG = timezone(timedelta(hours=-3))

def validar_body_crear_bloqueo(data: dict) -> tuple[dict, str | None]:
    if not data or not isinstance(data, dict):
        return {}, "Debe enviar un objeto JSON válido."

    campos_permitidos = {'id_cancha', 'fecha', 'hora_inicio', 'hora_fin', 'motivo'}
    if set(data.keys()) - campos_permitidos:
        return {}, "Se encontraron campos no permitidos en la solicitud."

    id_cancha = data.get('id_cancha')
    fecha = data.get('fecha')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    motivo = data.get('motivo')

    if not isinstance(id_cancha, int) or id_cancha <= 0:
        return {}, "El campo 'id_cancha' debe ser un entero positivo."

    if not fecha or not isinstance(fecha, str):
        return {}, "El campo 'fecha' es obligatorio y debe tener formato YYYY-MM-DD."

    try:
        datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        return {}, "El formato de 'fecha' debe ser YYYY-MM-DD."

    patron_hora = r"^([0-1]?[0-9]|2[0-3]):00:00$"
    if not hora_inicio or not re.match(patron_hora, hora_inicio):
        return {}, "El campo 'hora_inicio' debe tener el formato HH:00:00 (horas en punto)."

    if not hora_fin or not re.match(patron_hora, hora_fin):
        return {}, "El campo 'hora_fin' debe tener el formato HH:00:00 (horas en punto)."

    try:
        dt_inicio = datetime.strptime(f"{fecha} {hora_inicio}", '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZ_ARG)
        dt_fin = datetime.strptime(f"{fecha} {hora_fin}", '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZ_ARG)
    except ValueError:
        return {}, "La fecha u horario ingresado no es válido."

    if dt_inicio >= dt_fin:
        return {}, "La 'hora_inicio' debe ser menor que 'hora_fin'."

    ahora = datetime.now(TZ_ARG)
    if dt_inicio <= ahora:
        return {}, "El bloqueo debe comenzar en un momento futuro respecto al horario actual."

    if dt_inicio.hour < 8 or dt_fin.hour > 23:
        return {}, "El bloqueo debe quedar dentro del horario operativo del club (08:00 a 23:00)."

    if not motivo or not isinstance(motivo, str) or not motivo.strip():
        return {}, "El campo 'motivo' es obligatorio y no puede quedar vacío."

    datos_limpios = {
        'id_cancha': id_cancha,
        'fecha': fecha,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'motivo': motivo.strip()
    }
    return datos_limpios, None


def validar_filtros_listar_bloqueos(args: dict) -> tuple[dict, str | None]:
    try:
        limit = args.get('_limit', 10, type=int)
        offset = args.get('_offset', 0, type=int)
    except Exception:
        return {}, "Los parámetros '_limit' y '_offset' deben ser enteros."

    if limit < 1 or limit > 100:
        return {}, "El parámetro '_limit' debe estar entre 1 y 100."
    if offset < 0:
        return {}, "El parámetro '_offset' debe ser mayor o igual a cero."

    id_cancha = args.get('id_cancha', type=int)
    fecha = args.get('fecha', type=str)

    filtros = {
        'limit': limit,
        'offset': offset,
        'id_cancha': id_cancha,
        'fecha': fecha
    }
    return filtros, None 