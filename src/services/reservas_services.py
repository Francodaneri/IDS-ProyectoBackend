from datetime import datetime, timezone, timedelta
from src.repositories.reservas_repository import (
    obtener_socio_por_id_db,
    obtener_cancha_por_id_db,
    verificar_superposicion_cancha_db,
    verificar_superposicion_socio_db,
    crear_reserva_db,
    obtener_reserva_por_id_db,
    listar_reservas_db,
    actualizar_estado_reserva_db
)

class RecursoNoEncontradoError(Exception):
    pass

class ConflictoNegocioError(Exception):
    pass

TZ_ARG = timezone(timedelta(hours=-3))

def _formatear_fecha_iso(dt):
    """Garantiza formato ISO 8601 exacto YYYY-MM-DDTHH:MM:SS.ffffff-03:00."""
    if dt is None:
        return None
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ_ARG)
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00')
    return str(dt)

def _preparar_reserva_response(reserva):
    if not reserva:
        return None
    res_copy = dict(reserva)
    res_copy['fecha_hora_inicio'] = _formatear_fecha_iso(res_copy['fecha_hora_inicio'])
    res_copy['fecha_hora_fin'] = _formatear_fecha_iso(res_copy['fecha_hora_fin'])
    return res_copy

def crear_reserva_service(id_socio: int, id_cancha: int, fecha_hora_inicio: str, fecha_hora_fin: str):
    try:
        dt_inicio = datetime.fromisoformat(fecha_hora_inicio)
        dt_fin = datetime.fromisoformat(fecha_hora_fin)
    except Exception:
        raise ConflictoNegocioError("Formato de fecha inválido. Debe ser ISO 8601 con offset GMT-3.")

    if dt_inicio.tzinfo is None:
        dt_inicio = dt_inicio.replace(tzinfo=TZ_ARG)
    if dt_fin.tzinfo is None:
        dt_fin = dt_fin.replace(tzinfo=TZ_ARG)

    ahora = datetime.now(TZ_ARG)

    if dt_inicio >= dt_fin:
        raise ConflictoNegocioError("La fecha_hora_inicio debe ser menor que la fecha_hora_fin.")

    if dt_inicio <= ahora:
        raise ConflictoNegocioError("La reserva debe comenzar en un momento futuro respecto al horario actual.")

    if dt_inicio.date() != dt_fin.date():
        raise ConflictoNegocioError("La reserva no puede cruzar la medianoche.")

    if dt_inicio.minute != 0 or dt_inicio.second != 0 or dt_inicio.microsecond != 0 or \
       dt_fin.minute != 0 or dt_fin.second != 0 or dt_fin.microsecond != 0:
        raise ConflictoNegocioError("Las reservas deben comenzar y finalizar en horas exactas.")

    duracion_horas = (dt_fin - dt_inicio).total_seconds() / 3600.0
    if duracion_horas not in (1.0, 2.0, 3.0):
        raise ConflictoNegocioError("La duración de la reserva debe ser de 1, 2 o 3 horas exactas.")

    if dt_inicio.hour < 8 or dt_fin.hour > 23:
        raise ConflictoNegocioError("La reserva debe estar dentro del horario operativo del club (08:00 a 23:00).")

    socio = obtener_socio_por_id_db(id_socio)
    if not socio:
        raise RecursoNoEncontradoError(f"Socio con ID {id_socio} no encontrado.")
    if not socio.get('activo'):
        raise ConflictoNegocioError(f"El socio con ID {id_socio} está inactivo.")

    cancha = obtener_cancha_por_id_db(id_cancha)
    if not cancha:
        raise RecursoNoEncontradoError(f"Cancha con ID {id_cancha} no encontrada.")
    if not cancha.get('activa'):
        raise ConflictoNegocioError(f"La cancha con ID {id_cancha} está inactiva.")

    inicio_db = dt_inicio.strftime('%Y-%m-%d %H:%M:%S')
    fin_db = dt_fin.strftime('%Y-%m-%d %H:%M:%S')

    if verificar_superposicion_cancha_db(id_cancha, inicio_db, fin_db):
        raise ConflictoNegocioError("La cancha ya tiene una reserva confirmada en ese horario.")

    if verificar_superposicion_socio_db(id_socio, inicio_db, fin_db):
        raise ConflictoNegocioError("El socio ya tiene una reserva confirmada en ese horario.")

    precio_hora = cancha['precio_hora']
    precio_total = int(duracion_horas * precio_hora)

    reserva_id = crear_reserva_db(
        id_socio=id_socio,
        id_cancha=id_cancha,
        inicio=inicio_db,
        fin=fin_db,
        precio_hora=precio_hora,
        precio_total=precio_total,
        estado='confirmada'
    )

    return reserva_id

def obtener_reserva_por_id_service(reserva_id: int):
    reserva = obtener_reserva_por_id_db(reserva_id)
    if not reserva:
        raise RecursoNoEncontradoError(f"Reserva con ID {reserva_id} no encontrada.")
    return _preparar_reserva_response(reserva)

def listar_reservas_service(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None, limit=10, offset=0):
    reservas, total = listar_reservas_db(
        id_cancha=id_cancha,
        id_socio=id_socio,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset
    )
    reservas_format = [_preparar_reserva_response(r) for r in reservas]
    return reservas_format, total

def cambiar_estado_reserva_service(reserva_id: int, nuevo_estado: str):
    reserva = obtener_reserva_por_id_db(reserva_id)
    if not reserva:
        raise RecursoNoEncontradoError(f"Reserva con ID {reserva_id} no encontrada.")

    estado_actual = reserva['estado']

    # Repetir el estado actual es idempotente (devuelve la reserva sin modificar)
    if estado_actual == nuevo_estado:
        return _preparar_reserva_response(reserva)

    transiciones_validas = {
        'confirmada': ['cancelada', 'finalizada'],
        'cancelada': [],
        'finalizada': []
    }

    if nuevo_estado not in transiciones_validas.get(estado_actual, []):
        raise ConflictoNegocioError(
            f"No se permite cambiar el estado de '{estado_actual}' a '{nuevo_estado}'."
        )

    ahora = datetime.now(TZ_ARG)

    dt_inicio = reserva['fecha_hora_inicio']
    if isinstance(dt_inicio, str):
        dt_inicio = datetime.fromisoformat(dt_inicio)
    if dt_inicio.tzinfo is None:
        dt_inicio = dt_inicio.replace(tzinfo=TZ_ARG)

    dt_fin = reserva['fecha_hora_fin']
    if isinstance(dt_fin, str):
        dt_fin = datetime.fromisoformat(dt_fin)
    if dt_fin.tzinfo is None:
        dt_fin = dt_fin.replace(tzinfo=TZ_ARG)

    # Regla: cancelada -> El horario de inicio todavía no llegó (ahora < dt_inicio)
    if nuevo_estado == 'cancelada':
        if ahora >= dt_inicio:
            raise ConflictoNegocioError(
                "No se puede cancelar una reserva cuyo horario de inicio ya ha comenzado o pasado."
            )

    # Regla: finalizada -> Se alcanzó o superó el horario de finalización (ahora >= dt_fin)
    if nuevo_estado == 'finalizada':
        if ahora < dt_fin:
            raise ConflictoNegocioError(
                "No se puede finalizar una reserva cuyo horario de finalización aún no se ha alcanzado."
            )

    actualizar_estado_reserva_db(reserva_id, nuevo_estado)
    return obtener_reserva_por_id_service(reserva_id)