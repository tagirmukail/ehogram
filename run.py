from app import app, socketio
from app.config import *

socketio.run(app,
             host=host,
             port=port,
             debug=DEBUG)
