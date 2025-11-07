from flask import Flask
from database.init_database import init_database

def create_app():
    app = Flask(__name__, template_folder= "../templates")
    hospital_col = init_database()
    from .routes import create_blueprint
    web = create_blueprint(hospital_col)  
    app.register_blueprint(web)
    
    return app