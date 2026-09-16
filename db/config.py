import os

# Configuración de conexión a la base de datos SQL (MySQL)
# Se leen variables de entorno con valores por defecto para desarrollo local.
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'club_deportivo')

# Diccionario listo para pasar a PyMySQL mediante pymysql.connect(**DB_CONFIG)
DB_CONFIG = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'charset': 'utf8mb4',
    'autocommit': True
}