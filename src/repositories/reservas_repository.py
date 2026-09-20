

import pymysql
from db.config import DB_CONFIG

def get_db_connection():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def obtener_socio_por_id_db(id_socio: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, nombre, email, activo FROM socios WHERE id = %s"
            cursor.execute(sql, (id_socio,))
            return cursor.fetchone()
    finally:
        connection.close()

def obtener_cancha_por_id_db(id_cancha: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, nombre, precio_hora, activa FROM canchas WHERE id = %s"
            cursor.execute(sql, (id_cancha,))
            return cursor.fetchone()
    finally:
        connection.close()

def verificar_superposicion_cancha_db(id_cancha: int, inicio, fin):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT id FROM reservas 
                WHERE id_cancha = %s 
                  AND estado = 'confirmada'
                  AND fecha_hora_inicio < %s 
                  AND fecha_hora_fin > %s
                LIMIT 1
            """
            cursor.execute(sql, (id_cancha, fin, inicio))
            return cursor.fetchone() is not None
    finally:
        connection.close()

def verificar_superposicion_socio_db(id_socio: int, inicio, fin):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT id FROM reservas 
                WHERE id_socio = %s 
                  AND estado = 'confirmada'
                  AND fecha_hora_inicio < %s 
                  AND fecha_hora_fin > %s
                LIMIT 1
            """
            cursor.execute(sql, (id_socio, fin, inicio))
            return cursor.fetchone() is not None
    finally:
        connection.close()

def crear_reserva_db(id_socio: int, id_cancha: int, inicio, fin, precio_hora: int, precio_total: int, estado: str = 'confirmada'):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (id_socio, id_cancha, inicio, fin, estado, precio_hora, precio_total))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def obtener_reserva_por_id_db(id_reserva: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total 
                FROM reservas 
                WHERE id = %s
            """
            cursor.execute(sql, (id_reserva,))
            return cursor.fetchone()
    finally:
        connection.close()

def listar_reservas_db(id_cancha=None, id_socio=None, estado=None, fecha_desde=None, fecha_hasta=None, limit=10, offset=0):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            where_clauses = []
            params = []

            if id_cancha is not None:
                where_clauses.append("id_cancha = %s")
                params.append(id_cancha)
            if id_socio is not None:
                where_clauses.append("id_socio = %s")
                params.append(id_socio)
            if estado is not None:
                where_clauses.append("estado = %s")
                params.append(estado)
            if fecha_desde is not None:
                where_clauses.append("LEFT(fecha_hora_inicio, 10) >= %s")
                params.append(fecha_desde[:10])
            if fecha_hasta is not None:
                where_clauses.append("LEFT(fecha_hora_inicio, 10) <= %s")
                params.append(fecha_hasta[:10])

            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            sql_count = f"SELECT COUNT(*) AS total FROM reservas{where_str}"
            cursor.execute(sql_count, params)
            total = cursor.fetchone()['total']

            sql_data = f"""
                SELECT id, id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total 
                FROM reservas
                {where_str}
                ORDER BY id ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql_data, params + [limit, offset])
            reservas = cursor.fetchall()

            return reservas, total
    finally:
        connection.close()

def actualizar_estado_reserva_db(id_reserva: int, nuevo_estado: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE reservas SET estado = %s WHERE id = %s"
            cursor.execute(sql, (nuevo_estado, id_reserva))
            connection.commit()
    finally:
        connection.close()