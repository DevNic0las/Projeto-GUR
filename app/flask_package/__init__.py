from flask import Flask
from database.init_database import initdatabase
from catboost import CatBoostClassifier
def create_app():
    app = Flask(__name__, template_folder= "../templates")
    hospital_col = initdatabase()
    model_catboost = CatBoostClassifier()
    model_catboost.load_model('./flask_package/modelo_triagem_catboost_v7_final.cbm')
    from .routes import create_blueprint
    web = create_blueprint(hospital_col,model_catboost)  
    app.register_blueprint(web)
    
    return app