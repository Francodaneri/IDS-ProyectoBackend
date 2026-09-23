from src.repositories.socios_repository import *

def listar_socios_service(limit: int, offset: int, nombre: str, activo: bool):
    socios, total = obtener_socios_db(
        nombre=nombre,
        activo=activo,
        limit=limit,
        offset=offset
    )
    return (socios, total), None, 200

def crear_socio_service(nombre: str, email: str, activo: bool):
    if existe_socio_db(email):
        return None, f"El email '{email}' ya se encuentra registrado.", 409

    socio_id = crear_socio_db(
        nombre=nombre,
        email=email,
        activo=activo
    )
    return socio_id, None, 201

def obtener_socio_por_id_service(socio_id: int):
    socio = obtener_socio_por_id_db(socio_id)
    if not socio:
        return None, f"No existe ningun socio con id {socio_id}.", 404
    return socio, None, 200

def actualizar_socio_id_service(socio_id: int, datos_actualizacion: dict):
    socio = obtener_socio_por_id_db(socio_id)
    if not socio:
        return None, f"No existe ningun socio con id {socio_id}.", 404

    nuevo_email = datos_actualizacion.get('email')
    if nuevo_email and nuevo_email != socio.get('email'):
        if existe_socio_db(nuevo_email):
            return None, f"El email '{nuevo_email}' ya se encuentra registrado.", 409

    actualizar_socio_db(socio_id, datos_actualizacion)
    return True, None, 204