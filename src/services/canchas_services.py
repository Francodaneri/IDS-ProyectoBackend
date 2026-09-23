from src.repositories.canchas_repository import *

def listar_canchas_service(limit: int, offset: int, id_deporte: int = None, nombre: str = None, techada: bool = None, activa: bool = None):
    canchas, total = obtener_canchas_db(
        id_deporte=id_deporte,
        nombre=nombre,
        techada=techada,
        activa=activa,
        limit=limit,
        offset=offset
    )
    return (canchas, total), None, 200

def crear_cancha_service(nombre: str, id_deporte: int, precio_hora: int, techada: bool = False, activa: bool = True):
    if not existe_deporte_db(id_deporte):
        return None, f"No existe ningún deporte registrado con id {id_deporte}.", 404

    cancha_id = crear_cancha_db(
        nombre=nombre,
        id_deporte=id_deporte,
        precio_hora=precio_hora,
        techada=techada,
        activa=activa
    )
    return cancha_id, None, 201

def obtener_cancha_por_id_service(cancha_id: int):
    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        return None, f"No existe ninguna cancha con id {cancha_id}.", 404
    return cancha, None, 200

def actualizar_cancha_service(cancha_id: int, datos_actualizacion: dict):
    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        return None, f"No existe ninguna cancha con id {cancha_id}.", 404

    actualizar_cancha_db(cancha_id, datos_actualizacion)
    return True, None, 204

def eliminar_cancha_service(cancha_id: int):
    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        return None, f"No existe ninguna cancha con id {cancha_id}.", 404

    if cancha_tiene_reservas_db(cancha_id):
        return None, "La cancha tiene reservas asociadas y no se puede eliminar. Puede desactivarse mediante PATCH actualizando activa=false.", 409

    eliminar_cancha_db(cancha_id)
    return True, None, 204

def consultar_canchas_disponibles_service(fecha: str, hora_inicio: str, hora_fin: str, id_deporte: int = None, techada: bool = None, limit: int = 10, offset: int = 0):
    canchas, total = obtener_canchas_disponibles_db(
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        id_deporte=id_deporte,
        techada=techada,
        limit=limit,
        offset=offset
    )
    return (canchas, total), None, 200