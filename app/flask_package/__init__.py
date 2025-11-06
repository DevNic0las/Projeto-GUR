from flask import Flask
from database.initdatabase import initdatabase

def create_app():
    app = Flask(__name__, template_folder= "../templates")
    hospital_col = initdatabase()
    from .routes import create_blueprint
    web = create_blueprint(hospital_col)  
    app.register_blueprint(web)
    
    return app