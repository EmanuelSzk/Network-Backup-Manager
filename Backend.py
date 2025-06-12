from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:44987813@localhost:5432/network_backup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo de ejemplo para tabla de usuarios (podés adaptarlo)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Dispositivo(db.Model):
    
    nombre = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    Tipo = db.Column(db.String(50), nullable=False)
    Usuario = db.Column(db.String(50), nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    puerto_ssh = db.Column(db..Integer, nulleable=False)


@app.route('/login', methods=['POST'])
def login():        
    data = request.json
    username = data.get('username')
    password = data.get('password')

    usuario = Usuario.query.filter_by(username=username).first()

    if usuario and usuario.password == password:
        return jsonify({"success": True, "message": f"Bienvenido, {username}!"})
    else:
        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos."}), 401

@app.route('/dispositivo', methods=['POST'])
def agregar_dispositivo():
    data = request.json
    
    nombre = data.get('nombre')
    ip = data.get('ip')
    tipo = data.get('tipo')
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    ssh = data.get('ssh')
    

    
    nuevo_dispositivo = Dispositivo(
        nombre=nombre,
        ip=ip,
        tipo=tipo,
        usuario=usuario,
        contrasena=contrasena,
        ssh=ssh
        
    )
    db.session.add(nuevo_dispositivo)
    db.session.commit()

    return jsonify({"success": True, "message": "Dispositivo agregado correctamente"})

if __name__ == '__main__':
    # Crea las tablas si no existen (solo la primera vez)
    with app.app_context():
        db.create_all()
    app.run(port=5000)
