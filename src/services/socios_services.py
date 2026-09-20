from src.repositories.socios_repository import obtener_socios_db, existe_socio_db, crear_socio_db, obtener_socio_por_id_db

class RecursoNoEncontradoError(Exception):
    """Excepción de negocio cuando no existe una entidad relacionada."""
    pass

def listar_socios_service(limit: int, offset: int, nombre: str, activo: bool):
    """
    Orquesta la obtención paginada de los socios desde la base de datos.
    """
    socios, total = obtener_socios_db(
        nombre=nombre,
        activo=activo,
        limit=limit,
        offset=offset
    )
    return socios, total

def crear_socio_service(nombre: str, email: str, activo: bool) -> int:
    """
    Valida la existencia del socio y delega la creación en el repositorio.
    """

    if existe_socio_db(email):
        raise ConflictoNegocioError(f"El email '{email}' ya se encuentra registrado.")

    socio_id= crear_socio_db(
        nombre=nombre,
        email=email,
        activo=activo
    )
    return socio_id

from src.repositories.socios_repository import (
    obtener_socios_por_id_db,
    actualizar_socios_db
)

class RecursoNoEncontradoError(Exception):
    """Excepción cuando el recurso no existe en la base de datos (HTTP 404)."""
    pass

class ConflictoNegocioError(Exception):
    """Excepción cuando una regla de negocio impide la operación (HTTP 409)."""
    pass


def obtener_socio_por_id_service(socio_id: int) -> dict:
    """Obtiene los datos de un socio específico por su ID."""
    socio = obtener_socio_por_id_db(socio_id)
    if not socio:
        raise RecursoNoEncontradoError(f"No existe ninguna socio con id {socio_id}.")
    return socio


def actualizar_socio_id_service(socio_id: int, datos_actualizacion: dict) -> None:
    """Actualiza parcialmente un socio si existe."""
    socio = obtener_socio_por_id_db(socio_id)
    if not socio:
        raise RecursoNoEncontradoError(f"No existe ningun socio con id {socio_id}.")

    nuevo_email = datos_actualizacion.get('email')
    if nuevo_email and nuevo_email != socio.get('email'):
        if existe_socio_db(nuevo_email):
            raise ConflictoNegocioError(f"El email '{nuevo_email}' ya se encuentra registrado.")

    actualizar_socio_db(socio_id, datos_actualizacion)