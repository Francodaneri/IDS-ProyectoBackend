import pymysql
from db.config import DB_CONFIG  # Archivo de configuración con parámetros de conexión

def obtener_deportes_desde_db():
    """
    Consulta en la base de datos la lista de deportes precargados.
    Retorna una lista de diccionarios con 'id' y 'nombre'.
    """
    connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, nombre FROM deportes ORDER BY id ASC;"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()