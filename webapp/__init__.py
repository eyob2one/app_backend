from flask import Flask
from models import db

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize the database
db.init_app(app)

from routes import app as routes_app
app.register_blueprint(routes_app)
