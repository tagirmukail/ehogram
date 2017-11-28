from datetime import timedelta
DEBUG = True

MONGO_HOST = '127.0.0.1'
MONGO_PORT = '27017'
MONGO_DBNAME = 'yourname'
MONGO_USERNAME = 'user'
MONGO_PASSWORD = 'password'
MONGO_AUTO_START_REQUEST = 'True'

SECRET_KEY = 'mysecret!'
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
TRAP_HTTP_EXCEPTIONS = True
host = '127.0.0.1'
port = 5000

MAIL_SERVER = 'smtp.gmail.com'
MAIL_USERNAME = 'youremail'
MAIL_PASSWORD = 'yourpassword'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False