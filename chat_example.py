# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, request, session, redirect, jsonify, abort
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, send
import bcrypt
from datetime import timedelta
from config import CHAT_SETTINGS
from help_functions import *

app = Flask(__name__)

CHAT_SETTINGS = CHAT_SETTINGS

app.config['SECRET_KEY'] = CHAT_SETTINGS.SECRET_KEY
app.config["MONGO_DBNAME"] = CHAT_SETTINGS.MONGO_DBNAME
app.config['MONGO_HOST'] = CHAT_SETTINGS.MONGO_HOST
app.config['MONGO_PORT'] = CHAT_SETTINGS.MONGO_PORT
app.config['MONGO_USERNAME'] = CHAT_SETTINGS.MONGO_USERNAME
app.config['MONGO_PASSWORD'] = CHAT_SETTINGS.MONGO_PASSWORD
app.config['MONGO_AUTO_START_REQUEST'] = CHAT_SETTINGS.MONGO_AUTO_START_REQUEST
app.config['DEBUG'] = CHAT_SETTINGS.DEBUG
app.config['TRAP_HTTP_EXCEPTIONS'] = CHAT_SETTINGS.TRAP_HTTP_EXCEPTIONS

mongo = PyMongo(app)

socketio = SocketIO(app)

app.permanent_session_lifetime = timedelta(minutes=CHAT_SETTINGS.PERMANENT_SESSION_LIFETIME)

@app.route('/RECV/', methods=['GET'])
def recv():
    """Если пользователь успешно авторизовался,
    открывается страница с сообщениями
    и форма для ввода и отправки новых сообщений"""
    if 'username' in session:
        # Время жизни сеанса
        session.permanent = True
        search_word = request.args.get('nick', '')
        context = recv_helper(mongo, search_word)
        return render_template('recv.html', context=context)
    # если пользователь не авторизован - перенаправляем на авторизицию
    return redirect(url_for('index'))

@app.route('/RECV/', methods=['GET'])
def recv_nick():
    if 'username' in session:
        """Возвращает json формата {nick:[msg0,msg1,...,msgn]}"""
        search_word = request.args.get('nick')
        messages = mongo.db.messages.find({'author': search_word})

        return jsonify({search_word: [message['text'] for message in messages]})

@socketio.on('message')
def handleMessage(msg):
    """отправляем сообщение и автора и сохраняем в бд"""
    if 'username' in session:
        msg = handle_helper_message(msg, session['username'], mongo)
    send(msg, broadcast=True)

@app.route('/')
def index():
    """пользователь выполнил вход, перенаправляем на страницу с сообщениями."""
    if 'username' in session:
        return redirect(url_for('recv'))
    """В противном случае остаемся на странице входа"""
    return render_template('auth.html')

@app.route('/logout/')
def logout():
    """Завершить сеанс пользователя"""
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/AUTH/', methods=['POST','GET'])
def auth():
    """Авторизация пользователя"""
    if request.method == 'GET':
        nick = request.args.get('nick')
        pwd = request.args.get('pwd')
    else:
        nick = request.form['username']
        pwd = request.form['pass']
    users = mongo.db.users
    login_user = users.find_one({'name': nick})
    # Если пользователь существует в базе.
    if login_user:
        # проверка введенного пользователем пароля.
        if bcrypt.hashpw(pwd.encode('utf-8'),
                    login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = nick
            return redirect(url_for('recv'))
    # в случае неверно введенных данных сообщить.
    return abort(401, 'there is no visitor with such a nickname and password.')

@app.route('/REGISTER/', methods=['POST','GET'])
def register():
    """Регистрация пользователя"""
    if request.method == 'POST':
        nick = request.form['username']
        pwd = request.form['pass']
    if request.method == 'GET':
        nick = request.args.get('nick', '')
        pwd = request.args.get('pwd', '')
    if len(nick) >= 4 and len(pwd) >= 8:
        users = mongo.db.users
        existing_user = users.find_one({'name': nick})
        # Если новый пользователь
        if existing_user is None:
            # хеш пароля
            hashpass = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
            # сохраняем пользователя в базе
            users.insert({'name': nick, 'password': hashpass})
            session['username'] = nick
            return redirect(url_for('index'))
        # Если пользователь существует выводим сообщение
        return abort(403, 'That username already exists!')
    return render_template('register.html')

@app.route('/SEND/', methods=['GET'])
def sender():
    """Отправка сообщения"""
    if 'username' in session:
        nick = request.args.get('nick', '')
        msg = request.args.get('msg', '')
        message_send_helper(mongo, nick, msg)
        # в любом случае перенаправляем на страницу с сообщениями
        return redirect(url_for('recv'))
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """Обработка исключения 404"""
    message = '404 Not Found!'
    return render_template('error.html', message=message), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Обработка исключения 500"""
    message = '500 Internal Server Error!'
    return render_template('error.html', message=message), 500

@app.errorhandler(401)
def unauthorized(error):
    """Обработка исключения 401"""
    return render_template('error.html', message=error), 401

@app.errorhandler(403)
def forbidden(error):
    """Обработка исключения 403"""
    message = '403 Forbidden!'
    return render_template('error.html', message=message), 403

if __name__ == '__main__':
    socketio.run(app,
                 host=CHAT_SETTINGS.host,
                 port=CHAT_SETTINGS.port)
