import pymysql
from db.config import DB_CONFIG

def get_db_connection():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def existe_bloqueo_superpuesto_db(id_cancha: int, fecha: str, hora_inicio: str, hora_fin: str) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 1 FROM bloqueos 
                WHERE id_cancha = %s AND fecha = %s 
                AND hora_inicio < %s AND hora_fin > %s 
                LIMIT 1;
            """
            cursor.execute(sql, (id_cancha, fecha, hora_fin, hora_inicio))
            return cursor.fetchone() is not None
    finally:
        conn.close()

def existe_reserva_superpuesta_bloqueo_db(id_cancha: int, fecha: str, hora_inicio: str, hora_fin: str) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            inicio_str = f"{fecha} {hora_inicio}"
            fin_str = f"{fecha} {hora_fin}"
            sql = """
                SELECT 1 FROM reservas 
                WHERE id_cancha = %s AND estado = 'confirmada' 
                AND fecha_hora_inicio < %s AND fecha_hora_fin > %s 
                LIMIT 1;
            """
            cursor.execute(sql, (id_cancha, fin_str, inicio_str))
            return cursor.fetchone() is not None
    finally:
        conn.close()

def crear_bloqueo_db(id_cancha: int, fecha: str, hora_inicio: str, hora_fin: str, motivo: str) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO bloqueos (id_cancha, fecha, hora_inicio, hora_fin, motivo)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(sql, (id_cancha, fecha, hora_inicio, hora_fin, motivo))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def obtener_bloqueo_por_id_db(bloqueo_id: int) -> dict | None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, id_cancha, 
                       DATE_FORMAT(fecha, '%%Y-%%m-%%d') AS fecha, 
                       TIME_FORMAT(hora_inicio, '%%H:%%i:%%s') AS hora_inicio, 
                       TIME_FORMAT(hora_fin, '%%H:%%i:%%s') AS hora_fin, 
                       motivo 
                FROM bloqueos 
                WHERE id = %s;
            """
            cursor.execute(sql, (bloqueo_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def listar_bloqueos_db(id_cancha=None, fecha=None, limit=10, offset=0):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            where_clauses = []
            params = []
            if id_cancha is not None:
                where_clauses.append("id_cancha = %s")
                params.append(id_cancha)
            if fecha:
                where_clauses.append("fecha = %s")
                params.append(fecha)

            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            sql_count = f"SELECT COUNT(*) AS total FROM bloqueos{where_str};"
            cursor.execute(sql_count, params)
            total = cursor.fetchone()['total']

            sql_data = f"""
                SELECT id, id_cancha, 
                       DATE_FORMAT(fecha, '%%Y-%%m-%%d') AS fecha, 
                       TIME_FORMAT(hora_inicio, '%%H:%%i:%%s') AS hora_inicio, 
                       TIME_FORMAT(hora_fin, '%%H:%%i:%%s') AS hora_fin, 
                       motivo 
                FROM bloqueos {where_str} 
                ORDER BY id ASC 
                LIMIT %s OFFSET %s;
            """
            cursor.execute(sql_data, params + [limit, offset])
            bloqueos = cursor.fetchall()
            return bloqueos, total
    finally:
        conn.close()

def eliminar_bloqueo_db(bloqueo_id: int) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM bloqueos WHERE id = %s;"
            cursor.execute(sql, (bloqueo_id,))
            conn.commit()
    finally:
        conn.close()