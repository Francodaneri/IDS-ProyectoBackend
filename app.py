from flask import Flask
from src.routes.deportes import deportes_bp
from src.routes.canchas import canchas_bp
from src.routes.socios import socios_bp
from src.routes.reservas import reservas_bp

app = Flask(__name__)

app.register_blueprint(deportes_bp)
app.register_blueprint(canchas_bp)
app.register_blueprint(socios_bp)
app.register_blueprint(reservas_bp)

# Configuración para que Flask no escape acentos ni caracteres especiales
app.json.ensure_ascii = False  # Para Flask 2.3+ o 3.x
# app.config['JSON_AS_ASCII'] = False  # Para versiones de Flask anteriores a 2.3

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)