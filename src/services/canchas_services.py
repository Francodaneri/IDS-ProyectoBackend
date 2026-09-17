from src.repositories.canchas_repository import obtener_canchas_db, existe_deporte_db, crear_cancha_db

class RecursoNoEncontradoError(Exception):
    """Excepción de negocio cuando no existe una entidad relacionada [4]."""
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