# -*- coding: utf-8 -*-
import bcrypt
from flask import render_template, flash, url_for, request, session, redirect, jsonify, abort
from flask_mail import Message
from flask_socketio import send
from itsdangerous import URLSafeTimedSerializer
from app import app, mail, mongo, socketio, bootstrap
from app.config import *
from help_functions import *
from forms import *
# from werkzeug.security import generate_password_hash, check_password_hash

s = URLSafeTimedSerializer('Thisissecret!')

@app.route('/recv/', methods=['GET'])
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
    return redirect(url_for('auth'))

@app.route('/logout/')
def logout():
    """Завершить сеанс пользователя"""
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/auth/', methods=['POST','GET'])
def auth():
    """Авторизация пользователя"""
    form = LoginForm()
    users = mongo.db.users
    login_user = users.find_one({'name': form.nick.data})
    # Если пользователь существует в базе.
    if login_user and login_user['email'] != '':
        # проверка введенного пользователем пароля.
        if bcrypt.hashpw(form.password.data.encode('utf-8'),
                    login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = form.nick.data
            return redirect(url_for('recv'))
        flash('Invalid nickname or password')
    return render_template('auth.html', form=form)

@app.route('/AUTH/')
def auth_args():
    """API - авторизация пользователя."""
    if request.method == 'GET':
        nick = request.args.get('nick', '')
        pwd = request.args.get('pwd', '')
        users = mongo.db.users
        login_user = users.find_one({'name': nick})
        if login_user and login_user['email'] != '':
            if bcrypt.hashpw(pwd.encode('utf-8'),
                             login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
                session['username'] = nick
                return redirect(url_for('recv'))
            flash('Invalid nickname or password')
        return redirect(url_for('auth'))


@app.route('/register/', methods=['POST', 'GET'])
def register():
    """Регистрация пользователя."""
    form = RegistrationForm()
    users = mongo.db.users
    if form.validate_on_submit():
        # формируем токен
        token = s.dumps(form.email.data, salt='email-confirm')
        # формируем сообщение с ссылкой для подтверждения регистрации.
        msg = Message('Confirm Email', sender=MAIL_USERNAME, recipients=[form.email.data])
        link = url_for('confirm_email', nick=form.nick.data, token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)
        # отпавляем сообщение с ссылкой
        mail.send(msg)
        # хеш пароля
        hashpass = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        users.insert({'name': form.nick.data,
                      'email': '',
                      'password': hashpass})
        flash('Check your mailbox')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/REGISTER/')
def register_args():
    """API для регистрации пользователя."""
    if request.method == 'GET':
        nick = request.args.get('nick', '')
        email = request.args.get('email', '')
        pwd = request.args.get('pwd', '')
        pwd2 = request.args.get('pwd2', '')
        if pwd == pwd2:
            users = mongo.db.users
            token = s.dumps(email, salt='email-confirm')
            msg = Message('Confirm Email', sender=MAIL_USERNAME, recipients=[email])
            link = url_for('confirm_email', nick=nick, token=token, _external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)

            hashpass = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': nick,
                          'email': '',
                          'password': hashpass})
            flash('Check your mailbox')
            return redirect(url_for('auth'))
        flash('Invalid password')
        return redirect(url_for('register'))

@app.route('/confirm_email/<nick>/<token>')
def confirm_email(nick, token):
    """После перехода по ссылке из письма"""
    users = mongo.db.users
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
        # Обновить email пользователя после перехода по ссылке.
        users.update_one({'name': nick}, {'$set': {'email': email}})
    except:
        # в случае ошибки удалить пользователя из бд.
        users.delete_one({'name': nick})
        return abort(400, 'The token is bad!')
    return redirect(url_for('index'))

@app.route('/SEND/', methods=['GET'])
def sender():
    """API - отправка сообщения"""
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

@app.errorhandler(400)
def badrequest(error):
    """400 исключение"""
    message = 'Bad request!'
    return render_template('error.html', message=message), 400
