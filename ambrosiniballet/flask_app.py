# Esto es el backend de python para mi aplicación web, hecha por Gabriel Ambrosini

from flask import Flask, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from functools import wraps
from helpers import login_required
import mysql.connector

""" A continuación vienen unas líneas de código que no entiendo muy bien
    pero que son un requisito para el programa"""
app = Flask(__name__)
app.config["DEBUG"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Conexión con la base de datos MySQL
mydb = mysql.connector.connect(
    host="gabriel1607.mysql.pythonanywhere-services.com",
    user="gabriel1607",
    password="caquitA2",
    database="gabriel1607$default"
)
db = mydb.cursor()

# Un decorador de rutas para reservar rutas para el administrador


def admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.execute("SELECT tipo FROM usuarios WHERE id = %s", [session["user_id"]])
        tipo = db.fetchall()
        # Verifica el tipo de usuario
        if tipo[0][0] != "administracion":
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


""" La ruta inicial, para poder ingresar al inicio de sesión y para
    solicitar un registro de nuevo usuario """


@app.route('/')
def index():
    # Ruta inicial con inicio de sesión
    if session:
        db.execute("SELECT tipo FROM usuarios WHERE id = %s", [session["user_id"]])
        tipo = db.fetchall()
        # Mostrar página inicial, especificando el tipo de usuario
        return render_template("index.html", tipo=tipo[0][0])

    # Ruta inicial sin inicio de sesión, mostrar página inicial sin tipo de usuario
    return render_template("index.html")


# Ruta para el incio de sesión
@app.route('/login', methods=["GET", "POST"])
def login():

    session.clear()

    # Cargar la información para inicio de sesión
    if request.method == "POST":
        nombre = [request.form.get("nombre")]
        db.execute("SELECT clave FROM usuarios WHERE nombre = %s", nombre)
        clave = db.fetchall()

        # Validación de la información
        if len(clave) > 0 and request.form.get("clave") and check_password_hash(clave[0][0], request.form.get("clave")):
            db.execute("SELECT id FROM usuarios WHERE nombre = %s", nombre)
            id = db.fetchall()
            # Asignar número de identificación para el usuario de la sesión en curso
            session["user_id"] = id[0][0]
            return redirect("/")

        # Si hay información inválida, mostrar mensaje de error en la página de inicio de sesión
        else:
            return render_template("login.html", aviso="clave")

    # Página de inicio de sesión
    return render_template("login.html")


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")


# Ruta para cambio de clave
@app.route('/cclave', methods=["POST"])
@login_required
@admin
def cclave():
    # Paso 2: cambiar la clave
    if request.method == "POST" and request.form.get("paso") == "2":

        # Verificar que la clave ha sido escrita bien dos veces
        if request.form.get("clave") != request.form.get("rclave"):
            # Si la clave está mal escrita, mostrar mensaje de error
            return render_template("cclave.html", id=request.form.get("id"), alerta="si")

        # Cambiar la clave en la base de datos
        db.execute("UPDATE usuarios SET clave = %s WHERE id = %s", [
                   generate_password_hash(request.form.get("clave")), request.form.get("id")])

    # Paso 1: mostrar formulario
    elif request.method == "POST" and request.form.get("paso") == "1":

        # Mostrar página con formulario de cambio de clave
        return render_template("cclave.html", id=request.form.get("id"))

    # Recargar la página de usuarios, si se ha cambiado la clave de uno
    return redirect("/usuarios")


# Ruta para solicitud de registro
@app.route('/solicitud', methods=["GET", "POST"])
def solicitud():
    # Enviar información de solicitud de registro a la base de datos
    if request.method == "POST":
        tipo = request.form.get("tipo")
        if tipo == "alumna":
            sql = "INSERT INTO solicitudes (nombre, tipo, nacimiento, telefono, correo, nombrer, direccion, colegio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = [request.form.get("nombre"), "alumna", request.form.get("nacimiento"), request.form.get("telefono"),
                   request.form.get("correo"), request.form.get("nombrer"), request.form.get("direccion"),  request.form.get("colegio")]
            db.execute(sql, val)
            mydb.commit()
        else:
            sql = "INSERT INTO solicitudes (nombre, nacimiento, telefono, correo, tipo) VALUES (%s, %s, %s, %s, %s)"
            val = [request.form.get("nombre"), request.form.get("nacimiento"),
                   request.form.get("telefono"), request.form.get("correo"), "profesora"]
            db.execute(sql, val)
            mydb.commit()

        # Regresar a la página principal
        return redirect("/")

    # Página de solicitud de registro, diferente dependiendo del tipo de solicitud
    tipo = request.args.get("tipo")
    if tipo == "profesora":
        tipo = ""
    return render_template("solicitud.html", tipo=tipo)


# Ruta para registrar un pago en la base de datos
@app.route('/pago', methods=["GET", "POST"])
@login_required
def pago():

    # Enviar información a la base de datos, si el método es POST
    if request.method == "POST":
        db.execute("SELECT id FROM usuarios WHERE nombre = %s", [request.form.get("usuario")])
        usuario = db.fetchall()

        # Validar existencia del usuario
        if not (len(usuario) > 0):
            return render_template("pago.html", aviso="nombre")
        # Validar el monto
        if not (request.form.get("monto").isnumeric()):
            return render_template("pago.html", aviso="monto")

        # Registrar información en la base de datos
        val = [usuario[0][0], request.form.get("enlace"), request.form.get("concepto"), request.form.get(
            "monto"), request.form.get("comentario"), request.form.get("fecha"), "0"]
        db.execute("INSERT INTO pagos (id_usuario, enlace, concepto, monto, comentario, fecha, confirmacion) VALUES (%s, %s, %s, %s, %s, %s, %s)", val)
        mydb.commit()

        # Mostrar la misma página de registro de pago, con mensaje de confirmación
        return render_template("pago.html", aviso="bien")

    # Página de pago, si el método es GET y no POST.
    return render_template("pago.html")


# Ruta para borrar información de la base de datos
@app.route('/borrar', methods=["POST"])
@login_required
@admin
def borrar():
    # Eliminar un usuario
    if request.form.get("id-usuario"):
        sql = "DELETE FROM usuarios WHERE id = %s"
        val = [request.form.get("id-usuario")]
        db.execute(sql, val)
        mydb.commit()

        # Recargar la página de usuarios
        return redirect("/usuarios")

    # Eliminar una solicitud
    elif request.form.get("id"):
        sql = "DELETE FROM solicitudes WHERE id = %s"
        val = [request.form.get("id")]
        db.execute(sql, val)
        mydb.commit()

        # Recargar la página de solicitudes
        return redirect("/solicitudes")

    # Eliminar un pago
    elif request.form.get("id-pago"):
        sql = "DELETE FROM pagos WHERE id = %s"
        val = [request.form.get("id-pago")]
        db.execute(sql, val)
        mydb.commit()

        # Recargar la página de pagos
        return redirect("/pagos")

    # En caso de manipulación de la entrada del usuario, regresar a página principal
    return redirect("/")


# Ruta para aceptar y finalizar registro en base de datos
@app.route('/aceptar', methods=["POST"])
@login_required
@admin
def aceptar():

    # Confirmar un pago en la base de datos
    if request.form.get("id-pago"):
        db.execute("UPDATE pagos SET confirmacion = %s WHERE id = %s",
                   ["1", request.form.get("id-pago")])
        mydb.commit()

        # Recargar la página de pagos
        return redirect("/pagos")

    # Recoger información sobre la solicitud de registro de usuario para aceptar
    sql = "SELECT * FROM solicitudes WHERE id = %s"
    val = [request.form.get("id")]
    db.execute(sql, val)
    tipo = db.fetchall()
    tipo = tipo[0]

    # Ingresar información en la base de datos si es profesora o...
    if tipo[2] == "profesora":
        sql = "INSERT INTO usuarios (nombre, tipo, clave, nacimiento, telefono, correo) VALUES (%s, %s, %s, %s, %s, %s)"
        val = [tipo[1], tipo[2], generate_password_hash("clave"), tipo[3], tipo[4], tipo[5]]
    # ... si es alumna
    elif tipo[2] == "alumna":
        sql = "INSERT INTO usuarios (nombre, tipo, clave, nacimiento, telefono, correo, nombrer, direccion, colegio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = [tipo[1], tipo[2], generate_password_hash(
            "clave"), tipo[3], tipo[4], tipo[5], tipo[6], tipo[7], tipo[8]]
    # En caso de error, recargar la página de solicitudes
    else:
        return redirect("/solicitudes")

    # Una vez ingresada la información en la base de datos de usuarios, borrarla en la base de datos de solicitudes
    db.execute(sql, val)
    sql = "DELETE FROM solicitudes WHERE id = %s"
    val = [request.form.get("id")]
    db.execute(sql, val)
    mydb.commit()

    # Regresar a la página de solicitudes
    return redirect("/solicitudes")


# Ruta para cargar la página con la lista de solicitudes de usuario
@app.route('/solicitudes')
@login_required
@admin
def solicitudes():
    # Cargar las solicitudes
    db.execute("SELECT * FROM solicitudes ORDER BY hora")
    solicitudes = db.fetchall()

    # Mostrar página con las solicitudes
    return render_template("solicitudes.html", solicitudes=solicitudes)


# Ruta para cargar la página con la lista de usuarios
@app.route('/usuarios')
@login_required
@admin
def usuarios():
    # Cargar la información de los usuarios
    db.execute("SELECT * FROM usuarios WHERE NOT id = %s ORDER BY nombre", [session["user_id"]])
    usuarios = db.fetchall()

    # Mostrar página con los usuarios
    return render_template("usuarios.html", usuarios=usuarios)


# Ruta para cargar la página con la lista de todos los pagos
@app.route('/pagos')
@login_required
@admin
def pagos():
    # Cargar los pagos
    db.execute("SELECT * FROM pagos ORDER BY fecha")
    pagos = db.fetchall()
    # Cargar los nombres de los usuarios
    db.execute("SELECT nombre FROM usuarios WHERE id IN (SELECT id_usuario FROM pagos ORDER BY fecha)")
    usuarios = db.fetchall()

    # Mostrar página con los pagos
    return render_template("pagos.html", pagos=pagos, usuarios=usuarios)


# Ruta para cargar la página con la lista de pagos del usuario en inicio de sesión
@app.route('/mispagos')
@login_required
def mispagos():
    # Cargar los pagos del usuario
    db.execute("SELECT * FROM pagos WHERE id_usuario = %s ORDER BY fecha", [session["user_id"]])
    pagos = db.fetchall()
    # Cargar nombre del usuario
    db.execute("SELECT nombre FROM usuarios WHERE id = %s", [session["user_id"]])
    nombre = db.fetchall()

    # Mostrar página con sus pagos
    return render_template("pagos.html", pagos=pagos, nombre=nombre[0][0])


# Esto es el final de mi documento app.py
