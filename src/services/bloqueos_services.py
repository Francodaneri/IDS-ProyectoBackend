from src.repositories.canchas_repository import *
from src.repositories.bloqueos_repository import *

def crear_bloqueo_service(id_cancha: int, fecha: str, hora_inicio: str, hora_fin: str, motivo: str):
    cancha = obtener_cancha_por_id_db(id_cancha)
    if not cancha:
        return None, f"No existe ninguna cancha con id {id_cancha}.", 404

    if existe_reserva_superpuesta_bloqueo_db(id_cancha, fecha, hora_inicio, hora_fin):
        return None, "La cancha ya posee una reserva confirmada en el intervalo indicado.", 409

    if existe_bloqueo_superpuesto_db(id_cancha, fecha, hora_inicio, hora_fin):
        return None, "La cancha ya posee otro bloqueo de mantenimiento en el intervalo indicado.", 409

    bloqueo_id = crear_bloqueo_db(id_cancha, fecha, hora_inicio, hora_fin, motivo)
    bloqueo_creado = obtener_bloqueo_por_id_db(bloqueo_id)
    return bloqueo_creado, None, 201


def listar_bloqueos_service(id_cancha=None, fecha=None, limit=10, offset=0):
    bloqueos, total = listar_bloqueos_db(id_cancha=id_cancha, fecha=fecha, limit=limit, offset=offset)
    return (bloqueos, total), None, 200


def eliminar_bloqueo_service(bloqueo_id: int):
    bloqueo = obtener_bloqueo_por_id_db(bloqueo_id)
    if not bloqueo:
        return None, f"No existe ningún bloqueo con id {bloqueo_id}.", 404

    eliminar_bloqueo_db(bloqueo_id)
    return True, None, 204
