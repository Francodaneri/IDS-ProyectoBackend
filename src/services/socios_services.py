from src.repositories.socios_repository import obtener_socios_db, existe_socio_db, crear_socio_db

class RecursoNoEncontradoError(Exception):
    """Excepción de negocio cuando no existe una entidad relacionada [4]."""
    pass

def listar_socios_service(limit: int, offset: int, nombre: str = None,):
    """
    Orquesta la obtención paginada de las canchas desde la base de datos [3, 5].
    """
    socios, total = obtener_socios_db(
        id_socios=id_socios,
        nombre=nombre,
        limit=limit,
        offset=offset
    )
    return socios, total

def crear_socio_service(nombre: str, id_socios: int,) -> int:
    """
    Valida la existencia del socio y delega la creación en el repositorio [4, 6].
    """
    if not existe_socio_db(id_socios):
        raise RecursoNoEncontradoError(f"No existe ningún socio registrado con id {id_socios}.")

    socios_id= crear_socios_db(
        nombre=nombre,
        id_socios=id_socios,
    )
    return socio_id

from src.repositories.socios_repository import (
    obtener_socios_por_id_db,
    actualizar_socios_db,
)

class RecursoNoEncontradoError(Exception):
    """Excepción cuando el recurso no existe en la base de datos (HTTP 404)."""
    pass

class ConflictoNegocioError(Exception):
    """Excepción cuando una regla de negocio impide la operación (HTTP 409)."""
    pass


def obtener_socio_por_id_service(socio_id: int) -> dict:
    """Obtiene los datos de un socio específico por su ID [1]."""
    socio = obtener_socio_por_id_db(cancha_id)
    if not cancha:
        raise RecursoNoEncontradoError(f"No existe ninguna cancha con id {cancha_id}.")
    return cancha


def actualizar_socio_id_service(socio_id: int, datos_actualizacion: dict) -> None:
    """
    Actualiza parcialmente un socio si existe [1].
    
    """
    socio = obtener_socio_por_id_db(oc_id)
    if not cancha:
        raise RecursoNoEncontradoError(f"No existe ninguna cancha con id {cancha_id}.")

    actualizar_cancha_db(cancha_id, datos_actualizacion)