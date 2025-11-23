from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from flask_package.config_sintomas_base import SINTOMAS_BASE
from datetime import datetime 
import pandas as pd


def criar_features_especificas_upas(df):
    df_feat = df.copy()
    
    proximidade_map = {
        'Zona Oeste': {
            'UPA Caxangá': 1.0, 'UPA Torrões': 0.9, 'HGV': 0.8, 'HC/UFPE': 0.7, 'HBL': 0.7,
            'UPA Imbiribeira': 0.4, 'UPA Boa Viagem': 0.2, 'UPA Nova Descoberta': 0.1
        },
        'Zona Sul': {
            'UPA Boa Viagem': 1.0, 'UPA Ibura': 0.9, 'UPA Imbiribeira': 0.8, 'IMIP': 0.6, 'HR': 0.6,
            'UPA Caxangá': 0.3, 'UPA Olinda': 0.2
        },
        'Zona Norte': {
            'UPA Nova Descoberta': 1.0, 'UPA Olinda': 0.9, 'HAM': 0.8, 'HUOC': 0.8, 
            'Hospital Pediátrico Helena Moura': 0.7, 'UPA Caxangá': 0.4, 'UPA Boa Viagem': 0.2
        },
        'Centro': {
            'IMIP': 1.0, 'HR': 0.9, 'PROCAPE': 0.9, 'HUOC': 0.8, 'UPA Imbiribeira': 0.6,
            'UPA Boa Viagem': 0.5, 'UPA Caxangá': 0.4, 'UPA Nova Descoberta': 0.3
        }
    }
    
    
    if 'Hospital_Recomendado' in df_feat.columns:
     
        df_feat['Score_Proximidade'] = df_feat.apply(
            lambda x: proximidade_map.get(x['Zona_Residencia'], {}).get(x['Hospital_Recomendado'], 0.1),
            axis=1
        )
    else:
        
        def calcular_score_zona(zona):
            if zona in proximidade_map:
               
                scores = list(proximidade_map[zona].values())
                return max(scores)  
            return 0.7  
        
        df_feat['Score_Proximidade'] = df_feat['Zona_Residencia'].apply(calcular_score_zona)

   
    df_feat['Score_Lotacao'] = 1 - df_feat['Lotacao_No_Momento']
    
    return df_feat

def create_blueprint(hospital_col: MongoClient, model_catboost):
    web = Blueprint('web', __name__)
    
    @web.route("/")
    def index():
        return render_template("index.html", hospital_list = list(hospital_col.find()))
    
    @web.route("/hospital/<name_hospital>")
    def details_hospitals(name_hospital):
        hospital_data = hospital_col.find_one({
        "name": {"$regex": f".*{name_hospital}.*"} 
        })
    
        return render_template("hospital.html",hospital_list=hospital_data)
    
        
 
    @web.route("/predict", methods=['POST'])
    def predict():
        if request.method == 'POST':
            horario_agora = datetime.now().hour
            if horario_agora >= 0 and horario_agora < 6:
                horario = "Madrugada"               
            elif horario_agora >= 6 and horario_agora < 18:               
                horario = "Diurno"
            else:
                horario = "Noturno"
                
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Json não enviado"}), 400  
                
            sintoma = data.get("sintoma")
            zona = data.get("zona")
            idade = data.get("idade")
            comorbidade = data.get("comorbidade")
            
            if sintoma in SINTOMAS_BASE:
                complexidade = SINTOMAS_BASE[sintoma]['complexidade']
                gravidade = SINTOMAS_BASE[sintoma]['gravidade']
            else:
                return jsonify({"error": "Sintoma não reconhecido"}), 400
        
            dados_paciente = {
                "Sintoma": sintoma,
                "Comorbidades": comorbidade,
                "Idade": idade,
                "Complexidade": complexidade,        
                "Gravidade": gravidade,
                "Horario": horario,
                "Zona_Residencia": zona,
                "Lotacao_No_Momento": 0.7    
            }    
            
            try:
                
                df_amostra = pd.DataFrame([dados_paciente])
                df_com_features = criar_features_especificas_upas(df_amostra)
                features_esperadas = model_catboost.feature_names_
                X_pred = df_com_features[features_esperadas]
                predicao = model_catboost.predict(X_pred).flatten()[0]
                if str(predicao) == "HC/UFPE":
                  hospital_name = "Hospital das Clínicas"
                  hospital_url = "Hospital das Clínicas"
                  return jsonify({"hospital_name": str(predicao), "redirect_url": f"/hospital/{hospital_url}"}), 200  
                else:
                  hospital_url = predicao
                  hospital_name = predicao
                return jsonify({"hospital":hospital_name, "redirect_url": f"/hospital/{hospital_url}"})
            except Exception as e:
                return jsonify({"error": f"Erro na predição: {str(e)}"}), 500
    
    @web.route("/test/predict")
    def test_predict():
     dados_paciente_teste = {
        "Sintoma": "Dor de cabeça",
        "Comorbidades": "nenhum",
        "Idade": 20,
        "Complexidade": "moderada",        
        "Gravidade": "leve",
        "Horario": "diurno",
        "Zona_Residencia": "Centro",
        "Lotacao_No_Momento": 0.4   
       }
    
     try:
        df_amostra = pd.DataFrame([dados_paciente_teste])
        df_com_features = criar_features_especificas_upas(df_amostra)
        features_esperadas = model_catboost.feature_names_
        X_pred = df_com_features[features_esperadas]
       
        # Faz a predição (geralmente retorna um numpy array)
        predicao = model_catboost.predict(X_pred).flatten()[0]
        
        # CORREÇÃO AQUI:
        # 1. Convertemos numpy.str_ ou numpy.object_ para string nativa do Python
        # 2. Criamos um dicionário para o jsonify
        
        resultado_json = {
            "success": True,
            "hospital_sugerido": str(predicao) 
        }

        return redirect(url_for("web.details_hospitals", name_hospital=resultado_json['hospital_sugerido']))

     except Exception as e:
        print(f"❌ Erro detalhado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
    return web