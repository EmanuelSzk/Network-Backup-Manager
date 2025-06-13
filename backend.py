from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import paramiko
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:110402BES44150784@localhost:5432/network_backup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo de ejemplo para tabla de usuarios (podés adaptarlo)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Dispositivos(db.Model):
    __tablename__ = 'dispositivos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    usuario = db.Column(db.String(50), nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    puerto_ssh = db.Column(db.Integer, nullable=False)

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

@app.route('/dispositivos', methods=['GET'])
def obtener_dispositivos():
    dispositivos = Dispositivos.query.all()
    lista = []
    for d in dispositivos:
        lista.append({
            "id": d.id,
            "nombre": d.nombre,
            "ip": d.ip,
            "tipo": d.tipo
        })
    return jsonify(lista)

@app.route('/dispositivos/<int:id>', methods=['GET'])
def obtener_dispositivo(id):
    dispositivo = Dispositivos.query.get_or_404(id)
    return jsonify({
        'id': dispositivo.id,
        'nombre': dispositivo.nombre,
        'ip': dispositivo.ip,
        'tipo': dispositivo.tipo,
        'usuario': dispositivo.usuario,
        'contrasena': dispositivo.contrasena,
        'puerto_ssh': dispositivo.puerto_ssh
    })

@app.route('/dispositivo', methods=['POST'])
def agregar_dispositivo():
    data = request.json
    
    nombre = data.get('nombre')
    ip = data.get('ip')
    tipo = data.get('tipo')
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    ssh = data.get('ssh')
    
    nuevo_dispositivo = Dispositivos(
        nombre=nombre,
        ip=ip,
        tipo=tipo,
        usuario=usuario,
        contrasena=contrasena,
        puerto_ssh=ssh
        
    )
    db.session.add(nuevo_dispositivo)
    db.session.commit()

    return jsonify({"success": True, "message": "Dispositivo agregado correctamente"})

@app.route('/dispositivos/<int:id>', methods=['DELETE'])
def eliminar_dispositivo(id):
    dispositivo = Dispositivos.query.get(id)
    if not dispositivo:
        return jsonify({"success": False, "message": "Dispositivo no encontrado"}), 404
    db.session.delete(dispositivo)
    db.session.commit()
    return jsonify({"success": True, "message": "Dispositivo eliminado correctamente"})

@app.route('/Editar', methods=['POST'])
def editar_dispositivo():
    data = request.json
    id = data.get('id')
    dispositivo = Dispositivos.query.get(id)
    if dispositivo:
        dispositivo.nombre = data.get('nombre')
        dispositivo.ip = data.get('ip')
        dispositivo.tipo = data.get('tipo')
        dispositivo.usuario = data.get('usuario')
        dispositivo.contrasena = data.get('contrasena')
        dispositivo.puerto_ssh = data.get('ssh')
        db.session.commit()
        return jsonify({"success": True, "message": "Dispositivo actualizado"})

@app.route('/backup/<int:id>', methods=['POST'])
def backup_dispositivo(id):
    dispositivo = Dispositivos.query.get(id)
    if not dispositivo:
        return jsonify({"success": False, "message": "Dispositivo no encontrado"}), 404

    ip = dispositivo.ip
    usuario = dispositivo.usuario
    contrasena = dispositivo.contrasena
    puerto = dispositivo.puerto_ssh

    # Comando típico para Cisco/IOS, adaptalo si usás otro sistema
    comando = "show running-config"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=puerto, username=usuario, password=contrasena, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(comando)
        salida = stdout.read().decode()
        ssh.close()
    except Exception as e:
        print(f"Error SSH: {e}")
        return jsonify({"success": False, "message": f"Error de conexión SSH: {e}"}), 500

    if not salida:
        return jsonify({"success": False, "message": "No se pudo obtener la configuración"}), 500

    # Carpeta y nombre de archivo
    carpeta = "C:/backups/"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{dispositivo.nombre}_{fecha}.txt"
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    try:
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(salida)
    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return jsonify({"success": False, "message": f"Error al guardar archivo: {e}"}), 500

    return jsonify({"success": True, "message": f"Backup guardado en {ruta_archivo}"})

if __name__ == '__main__':
    # Crea las tablas si no existen (solo la primera vez)
    # with app.app_context():
        # db.create_all()
    app.run(port=5000)