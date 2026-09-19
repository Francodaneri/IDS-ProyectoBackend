import pymysql
from db.config import DB_CONFIG  # Archivo de configuración con parámetros de conexión

def obtener_canchas_db(id_deporte=None, nombre=None, techada=None, activa=None, limit=10, offset=0):
    """
    Obtiene el listado paginado de canchas ordenado por id ASC, aplicando filtros opcionales.
    Retorna (lista_de_canchas, total_registros).
    """
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Construcción dinámica de la cláusula WHERE
            where_clauses = []
            params = []

            if id_deporte is not None:
                where_clauses.append("id_deporte = %s")
                params.append(id_deporte)

            if nombre:
                # Búsqueda parcial e insensible a mayúsculas/minúsculas
                where_clauses.append("LOWER(nombre) LIKE LOWER(%s)")
                params.append(f"%{nombre}%")

            if techada is not None:
                where_clauses.append("techada = %s")
                params.append(techada)

            if activa is not None:
                where_clauses.append("activa = %s")
                params.append(activa)

            where_str = ""
            if where_clauses:
                where_str = "WHERE " + " AND ".join(where_clauses)

            # 1. Obtener el total de registros que coinciden con el filtro
            count_sql = f"SELECT COUNT(*) AS total FROM canchas {where_str};"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 2. Obtener los registros paginados y ordenados por id ASC
            data_sql = f"""
                SELECT id, nombre, id_deporte, precio_hora, techada, activa 
                FROM canchas 
                {where_str}
                ORDER BY id ASC 
                LIMIT %s OFFSET %s;
            """
            cursor.execute(data_sql, params + [limit, offset])
            canchas = cursor.fetchall()

            # Convertir valores numéricos de MySQL (0/1) a booleanos nativos de Python
            for c in canchas:
                c['techada'] = bool(c['techada'])
                c['activa'] = bool(c['activa'])

            return canchas, total
    finally:
        connection.close()


def existe_deporte_db(id_deporte):
    """Verifica si un deporte existe en la base de datos."""
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM deportes WHERE id = %s;", (id_deporte,))
            return cursor.fetchone() is not None
    finally:
        connection.close()


def crear_cancha_db(nombre, id_deporte, precio_hora, techada=False, activa=True):
    """Inserta una nueva cancha y retorna el id asignado."""
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(sql, (nombre, id_deporte, precio_hora, techada, activa))
            return cursor.lastrowid
    finally:
        connection.close()


def obtener_cancha_por_id_db(cancha_id: int) -> dict | None:
    conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE id = %s;"
            cursor.execute(sql, (cancha_id,))
            cancha = cursor.fetchone()
            if cancha:
                # Convertir enteros de MySQL a booleans
                cancha['techada'] = bool(cancha['techada'])
                cancha['activa'] = bool(cancha['activa'])
            return cancha
    finally:
        conn.close()


def actualizar_cancha_db(cancha_id: int, datos: dict) -> None:
    if not datos:
        return
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            campos = [f"{clave} = %s" for clave in datos.keys()]
            valores = list(datos.values())
            valores.append(cancha_id)
            sql = f"UPDATE canchas SET {', '.join(campos)} WHERE id = %s;"
            cursor.execute(sql, valores)
    finally:
        conn.close()


def cancha_tiene_reservas_db(cancha_id: int) -> bool:
    """Verifica si la cancha tiene al menos una reserva asociada en la DB [2]."""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            sql = "SELECT 1 FROM reservas WHERE id_cancha = %s LIMIT 1;"
            cursor.execute(sql, (cancha_id,))
            return cursor.fetchone() is not None
    finally:
        conn.close()


def eliminar_cancha_db(cancha_id: int) -> None:
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM canchas WHERE id = %s;"
            cursor.execute(sql, (cancha_id,))
    finally:
        conn.close()