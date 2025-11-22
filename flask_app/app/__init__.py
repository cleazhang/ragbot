from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from app.main import main_blueprint


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(base_dir, 'static')
    template_folder = os.path.join(base_dir, 'templates')

    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
    app.register_blueprint(main_blueprint)
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'b88f1c3b2b4d9f1c3b2b4d9f1c3b')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    SQLAlchemy(app)
    return app