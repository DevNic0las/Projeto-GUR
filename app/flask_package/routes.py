from flask import Blueprint,render_template
from pymongo import MongoClient
def create_blueprint(hospital_col: MongoClient):
    web = Blueprint('web', __name__)
    
    @web.route("/")
    def index():
        return render_template("index.html")
    
    return web