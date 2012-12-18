# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, flash, g, session, request, url_for
from datetime import datetime
import pymongo

app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.before_request
def before_request():
    g.conn = pymongo.MongoClient()
    g.db = g.conn[app.config['DATABASE']]

@app.teardown_request
def after_request(exception):
    g.conn.disconnect()

def set_pass(txt_pass):
    # TODO encriptar pass
    #algo = 'sha1'
    #salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    #hsh = get_hexdigest(algo, salt, txt_pass)
    #return '%s$%s$%s' % (algo, salt, hsh)
    return txt_pass

def check_pass(txt_pass, enc_pass):
    # TODO encriptar pass
    #algo, salt, hsh = enc_pass.split('$')
    #return hsh == get_hexdigest(algo, salt, txt_pass)
    return txt_pass == enc_pass

def valid_login(username, password):
    # TODO sanear username
    print('Alive: %s' %g.conn.alive())
    for u in g.db.users.find():
        print "%r" % u
    cur = g.db.users.find({'user':request.form['username'].encode("utf-8")}).limit(1)
    if cur!=1:
        print "ups, ninguno"
        return False
    user = cur[0]
    return check_pass(password, user['pass'])

@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['logged_in'] = True
            flash('Bienvenido %s' % request.form['username'])
        else:
            flash("Usuario y password incorrectos")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Sesion terminada. Hasta pronto!")
    return redirect(url_for('index'))


def get_last_num():
    cur = g.db.facturas.find().sort(('_id',pymongo.ASCENDING)).limit(1)
    if len(cur) == 0:
        return 1
    return cur[0]['_id']

@app.route("/")
def index():
    fnum = 0
    if getattr(session, "logged_in", False)==True:
        fnum = get_last_num()
    return render_template('index.html', fnum=fnum)

@app.route("/f/crear", methods=["POST"])
def crear_factura():
    if not session.get('logged_in'):
        abort(401)
    numero = int(request.form['num']) or get_last_num()
    fecha = datetime(request.form['fecha'])
    importe = float(request.form['importe'])
    factura = {
        '_id': numero,
        'fecha': fecha,
        'importe': importe,
               }
    flash('Ingresada factura #' % numero)
    g.db.facturas.insert(factura)
    return redirect(url_for('index'))

@app.route("/f")
def listar_facturas():
    cur = g.db.facturas.find()
    return render_template('lista_facturas.html', facturas=cur)

@app.route("/p/buscar")
def buscar_paciente():
    return "buscando"

@app.route("/p/<dni>", methods=["GET","POST"])
def editar_paciente(dni):
    return "editando"

if __name__ == "__main__":
    app.debug=True
    app.run(host='0.0.0.0')
