# backend/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_moment import Moment # for time management
from flask_login import LoginManager # Gestion de sesiones

from dotenv import load_dotenv # maneja credenciales en variables de entorno (mas seguro)

# form management
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

#cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

#coors
from flask_cors import CORS



# Cargar el archivo .env
load_dotenv()

# Inicialización de la aplicación y configuración
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')  # Cargar SECRET_KEY para WTF forms security

# Inicializar bootstrap
Bootstrap(app)
# Inicializar moments
moments = Moment(app)

# Inicialización de la base de datos y migraciones
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Inicializar LoginManager para la gestión de sesiones
login_manager = LoginManager()
login_manager.login_view = 'signin'  # Redirige a la página de signin si no está autenticado
login_manager.init_app(app)  # Vincula LoginManager con la app Flask

# Función de carga de usuarios para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from backend.models import User  # Importar el modelo User aquí para evitar referencias circulares
    return User.query.get(int(user_id))


# Registrar blueprints
from backend.routes import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Importar las rutas y otros módulos después de inicializar app y db
from backend import routes,app, db, models


#--------------------cloudinary


# Configuración de Cloudinary
#cloudinary.config(
#    cloud_name='your_cloud_name',  # Reemplaza con tu nombre de Cloudinary
#    api_key='your_api_key',        # Reemplaza con tu API key
#    api_secret='your_api_secret'   # Reemplaza con tu API secret
#)

# Configurar Cloudinary usando variables de entorno (con python-dotenv)
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Permitir CORS para todas las rutas y orígenes
CORS(app)



