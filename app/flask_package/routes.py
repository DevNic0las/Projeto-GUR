from flask import Blueprint,render_template
def create_blueprint(db):
    web = Blueprint('web', __name__)
    
    @web.route("/hospital/<name>")
    def index(name):
        
        hospital = db.hospitals.find_one({"name": name})

        return render_template("index.html", hospital_find=hospital)
    
    return web