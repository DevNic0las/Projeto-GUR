from flask import Blueprint,render_template
from pymongo import MongoClient
def create_blueprint(hospital_col: MongoClient):
    web = Blueprint('web', __name__)
    
    @web.route("/hospital/<name>")
    def index(name):
       
        hospital = hospital_col.find_one({"name": name})

        return render_template("index.html", hospital_find=hospital)
    
    return web