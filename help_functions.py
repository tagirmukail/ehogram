# -*- coding: utf-8 -*-
def message_socket_helper(msg, author):
    """Задаем формат отправленного сообщения в чат"""
    message = '<li class="media">' \
                '<div class="media-body">' \
                    '<div class="media">' \
                        '<div class="media-body">%s<br/>' \
                            '<small class="text-muted">%s</small>' \
                        '</div>' \
                    '</div>' \
                '</div>' \
              '</li>' % (msg, author)
    return message


def recv_helper(mongo, searchword):
    """Фильтр колличества отображенных сообщений в окне чата."""
    messages = mongo.db.messages
    if searchword:
        # в запросе присутствует ключевое слово(имя пользователя), выводим список сообщений от данного пользователя
        messages = messages.find({'author': searchword})
    else:
        # отобразить последние сообщения
        len_msgs = messages.count()
        if len_msgs > 40:
            len_msgs -= 20
        else:
            len_msgs = 0
        messages = messages.find({'message_id': {'$gt': len_msgs}})
    context = {
        'messages': messages
    }
    return context

def handle_helper_message(msg, author, mongo):
    """Сохраняем сообщение в бд, и отпраляем в чат, или отправляем в чат уведомление о подключении пользователя"""
    if msg != 'User has connected!':
        messages = mongo.db.messages
        messages.insert({'message_id': messages.count() + 1,
                         'author': author,
                         'text': msg})
    # Форматированный вывод сообшения в чат
    msg = message_socket_helper(msg, author)
    return msg

def message_send_helper(mongo, nick, msg):
    """сохраняем сообщение для вызова /SEND/?nick=NICKNAME&pwd=PASSWORD"""
    messages = mongo.db.messages
    # сохраняем сообщение в базе
    messages.insert({'message_id': messages.count() + 1,
                     'author': nick,
                     'text': msg})
