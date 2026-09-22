"""
   actualizar_socio_db
"""
import pymysql
from db.config import DB_CONFIG

def obtener_socios_db(nombre=None, email=None, activo=None, limit=10, offset=0):
    """
    Obtiene el listado paginado de socios ordenado por id ASC, aplicando filtros opcionales.
    Retorna (listar_socios, total_registros).
    """
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Construcción dinámica de la cláusula WHERE
            where_clauses = []
            params = []

            if nombre:
                # Búsqueda parcial e insensible a mayúsculas/minúsculas
                where_clauses.append("LOWER(nombre) LIKE LOWER(%s)")
                params.append(f"%{nombre}%")

            if email:
                # Búsqueda parcial e insensible a mayúsculas/minúsculas
                where_clauses.append("LOWER(email) LIKE LOWER(%s)")
                params.append(f"%{email}%")

            if activo is not None:
                where_clauses.append("activo = %s")
                params.append(activo)

            where_str = ""
            if where_clauses:
                where_str = "WHERE " + " AND ".join(where_clauses)

            # 1. Obtener el total de registros que coinciden con el filtro
            count_sql = f"SELECT COUNT(*) AS total FROM socios {where_str};"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 2. Obtener los registros paginados y ordenados por id ASC
            data_sql = f"""
                SELECT id, nombre, email, activo
                FROM socios
                {where_str}
                ORDER BY id ASC 
                LIMIT %s OFFSET %s;
            """
            cursor.execute(data_sql, params + [limit, offset])
            socios = cursor.fetchall()

            # Convertir valores numéricos de MySQL (0/1) a booleanos nativos de Python
            for c in socios:
                c['activo'] = bool(c['activo'])

            return socios, total
    finally:
        connection.close()

def existe_socio_db(email):
    """Verifica si un email existe en la base de datos."""
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM socios WHERE email = %s;", (email,))
            return cursor.fetchone() is not None
    finally:
        connection.close()
        
def crear_socio_db(nombre: str, email: str, activo: bool = True) -> int:
    """Inserta un nuevo socio en la base de datos y retorna el id asignado."""
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO socios (nombre, email, activo)
                VALUES (%s, %s, %s);
            """
            cursor.execute(sql, (nombre, email, activo))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def obtener_socio_por_id_db(socio_id: int) -> dict | None:
    conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, nombre, email, activo FROM socios WHERE id = %s;"
            cursor.execute(sql, (socio_id,))
            socio = cursor.fetchone()
            if socio:
                socio['activo'] = bool(socio['activo'])
            return socio
    finally:
        conn.close()

def actualizar_socio_db(socio_id: int, datos: dict) -> None:
    if not datos:
        return
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            campos = [f"{clave} = %s" for clave in datos.keys()]
            valores = list(datos.values())
            valores.append(socio_id)
            sql = f"UPDATE socios SET {', '.join(campos)} WHERE id = %s;"
            cursor.execute(sql, valores)

        conn.commit()
    finally:
        conn.close()