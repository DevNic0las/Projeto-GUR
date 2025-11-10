from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient

def create_blueprint(hospital_col: MongoClient):
    web = Blueprint('web', __name__)
    
    @web.route("/")
    def index():
        return render_template("index.html")
    
    @web.route("/teste", methods=["GET", "POST"])
    def teste():
        if request.method == "POST":
           
            form_data = request.form

           
            date = form_data.to_dict()
            list(date)
            query = hospital_col.find_one({"illness": {"$in":date }})
            
          
           
            return jsonify(query)
        
        
        return render_template("teste.html")
    
    @web.route("/sucesso")
    def sucesso():
        return "<h3>Formulário enviado com sucesso!</h3><a href='/teste'>Voltar</a>"
    @web.route("/teste3")
    def teste3():
      return "<h1>TEMPALTE 3</h1>"
  
    @web.route("/hositals")
    def all_hospitals():
         list_hospitals = hospital_col.find()
         return jsonify(list_hospitals)
         
         
    return web
  
