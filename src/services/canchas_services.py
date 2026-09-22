from src.repositories.canchas_repository import (
    obtener_canchas_db,
    existe_deporte_db,
    crear_cancha_db,
    obtener_cancha_por_id_db,
    actualizar_cancha_db,
    cancha_tiene_reservas_db,
    eliminar_cancha_db,
    obtener_canchas_disponibles_db
)

class RecursoNoEncontradoError(Exception):
    """Excepción de negocio cuando no existe una entidad relacionada"""
    pass

class ConflictoNegocioError(Exception):
    """Excepción cuando una regla de negocio impide la operación (HTTP 409)."""
    pass

def listar_canchas_service(limit: int, offset: int, id_deporte: int = None, nombre: str = None, techada: bool = None, activa: bool = None):
    """
    Orquesta la obtención paginada de las canchas desde la base de datos [3, 5].
    """
    canchas, total = obtener_canchas_db(
        id_deporte=id_deporte,
        nombre=nombre,
        techada=techada,
        activa=activa,
        limit=limit,
        offset=offset
    )
    return canchas, total

def crear_cancha_service(nombre: str, id_deporte: int, precio_hora: int, techada: bool = False, activa: bool = True) -> int:
    """
    Valida la existencia del deporte y delega la creación en el repositorio [4, 6].
    """
    if not existe_deporte_db(id_deporte):
        raise RecursoNoEncontradoError(f"No existe ningún deporte registrado con id {id_deporte}.")

    cancha_id = crear_cancha_db(
        nombre=nombre,
        id_deporte=id_deporte,
        precio_hora=precio_hora,
        techada=techada,
        activa=activa
    )
    return cancha_id

def obtener_cancha_por_id_service(cancha_id: int) -> dict:
    """Obtiene los datos de una cancha específica por su ID [1]."""
    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        raise RecursoNoEncontradoError(f"No existe ninguna cancha con id {cancha_id}.")
    return cancha

def actualizar_cancha_service(cancha_id: int, datos_actualizacion: dict) -> None:
    """
    Actualiza parcialmente una cancha si existe [1].
    Cambiar la tarifa no modifica el importe de las reservas ya registradas [1].
    """
    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        raise RecursoNoEncontradoError(f"No existe ninguna cancha con id {cancha_id}.")

    actualizar_cancha_db(cancha_id, datos_actualizacion)

def eliminar_cancha_service(cancha_id: int) -> None:
    """
    Elimina una cancha únicamente si no posee ninguna reserva asociada [2].
    Si tiene reservas, lanza ConflictoNegocioError para responder HTTP 409 Conflict [2, 3].
    """
    cancha = obtener_cancha_por_id_db(cancha_id)
    if not cancha:
        raise RecursoNoEncontradoError(f"No existe ninguna cancha con id {cancha_id}.")

    if cancha_tiene_reservas_db(cancha_id):
        raise ConflictoNegocioError(
            "La cancha tiene reservas asociadas y no se puede eliminar. "
            "Puede desactivarse mediante PATCH actualizando activa=false."
        )

    eliminar_cancha_db(cancha_id)

def consultar_canchas_disponibles_service(
        fecha,
        hora_inicio,
  hora_fin,
        id_deporte=None,
        techada=None
):
        return obtener_canchas_disponibles_db(
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                id_deporte=id_deporte,
                techada=techada,
        )

    