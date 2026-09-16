#!/bin/bash

# Detener la ejecución si ocurre algún error no controlado en la parte de Python
set -e

echo "=== Configurando el entorno para Club Deportivo Backend ==="

# 1. Verificar instalación de Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado en el sistema."
    exit 1
fi

echo "Python 3 detectado: $(python3 --version)"

# 2. Verificar e instalar MySQL / MariaDB Server si es necesario
echo "----------------------------------------------------------"
echo "Verificando servicio y cliente MySQL..."

if ! command -v mysql &> /dev/null; then
    echo "MySQL no se encuentra instalado. Intentando instalar automáticamente..."
    
    if command -v apt-get &> /dev/null; then
        echo "Detectado gestor de paquetes apt (Debian/Ubuntu). Instalando mysql-server..."
        sudo apt-get update && sudo apt-get install -y mysql-server mysql-client
    elif command -v brew &> /dev/null; then
        echo "Detectado Homebrew (macOS). Instalando mysql..."
        brew install mysql
    elif command -v dnf &> /dev/null; then
        echo "Detectado gestor dnf (Fedora/RHEL). Instalando mysql-server..."
        sudo dnf install -y mysql-server
    else
        echo "No se detectó un gestor de paquetes soportado (apt, brew, dnf)."
        echo "Por favor instala MySQL Server manualmente para tu sistema operativo."
    fi
else
    echo "MySQL ya está instalado: $(mysql --version)"
fi

# Intentar iniciar el servicio MySQL si no está respondiendo
if command -v mysqladmin &> /dev/null; then
    if ! mysqladmin ping -u root --silent &> /dev/null; then
        echo "El servicio MySQL no está corriendo. Intentando iniciar el servicio..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start mysql || sudo systemctl start mariadb || true
        elif command -v service &> /dev/null; then
            sudo service mysql start || true
        elif command -v brew &> /dev/null; then
            brew services start mysql || true
        fi
    fi
    
    # Comprobar nuevamente tras el intento de inicio
    if mysqladmin ping -u root --silent &> /dev/null; then
        echo "Servicio MySQL: En ejecución y listo para recibir conexiones."
    else
        echo "Advertencia: No se pudo verificar la conexión con MySQL sin contraseña."
        echo "Asegúrate de que el servicio esté corriendo y de contar con los permisos/credenciales adecuados."
    fi
fi
echo "----------------------------------------------------------"

# 3. Crear el entorno virtual (venv) si no existe
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando entorno virtual '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
else
    echo "El entorno virtual '$VENV_DIR' ya existe."
fi

# 4. Activar el entorno virtual
echo "Activando entorno virtual..."
source $VENV_DIR/bin/activate

# 5. Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# 6. Generar requirements.txt base si no existe
if [ ! -f "requirements.txt" ]; then
    echo "Generando requirements.txt..."
    cat <<EOF > requirements.txt
Flask>=3.0.0
PyMySQL>=1.1.0
python-dotenv>=1.0.0
EOF
fi

# 7. Instalar dependencias requeridas
echo "Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

echo ""
echo "=========================================================="
echo "¡Configuración e instalación completada!"
echo "Para activar el entorno virtual ejecuta:"
echo "    source venv/bin/activate"
echo ""
echo "Para inicializar la base de datos de la API:"
echo "    mysql -u root -p < init_db.sql"
echo ""
echo "Para iniciar el servidor Flask:"
echo "    python app.py"
echo "=========================================================="
