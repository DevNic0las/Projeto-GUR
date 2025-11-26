from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from flask_package.config_sintomas_base import SINTOMAS_BASE
from flask_package.config_sintomas_base import SINTOMAS_PROCAPE
from datetime import datetime 
import pandas as pd


def criar_features_especificas_upas(df ,hospital_alvo=None):
   
    proximidade_map = {
        'Zona Oeste': {
            'UPA Caxangá': 1.0, 'UPA Torrões': 0.9, 'HGV': 0.8, 'HC/UFPE': 0.7, 'HBL': 0.7,
            'UPA Imbiribeira': 0.4, 'UPA Boa Viagem': 0.2, 'UPA Nova Descoberta': 0.1
        },
        'Zona Sul': {
            'UPA Ibura': 0.9, 'UPA Imbiribeira': 0.8, 'IMIP': 0.6, 'HR': 0.6,
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
    df_feat = df.copy()
    
    if 'Hospital_Recomendado' in df_feat.columns:
        df_feat['Score_Proximidade'] = df_feat.apply(
            lambda x: proximidade_map.get(x['Zona_Residencia'], {}).get(x['Hospital_Recomendado'], 0.1),
            axis=1
        )
    elif hospital_alvo: 
         df_feat['Score_Proximidade'] = proximidade_map.get(df_feat['Zona_Residencia'].iloc[0], {}).get(hospital_alvo, 0.9)
    else:
        def calcular_score_zona(zona):
            if zona in proximidade_map:
                scores = list(proximidade_map[zona].values())
                return max(scores)  
            return 0.7  
        
        df_feat['Score_Proximidade'] = df_feat['Zona_Residencia'].apply(calcular_score_zona)

    df_feat['Score_Lotacao'] = 1 - df_feat['Lotacao_No_Momento']
    
    return df_feat
    
def ajustar_gravidade_por_idade(gravidade: str, idade: int) -> str:
    
    try:
        idade = int(idade)
    except (ValueError, TypeError):
        return gravidade 
    
   
    if idade < 60:
        return gravidade
    
    if gravidade == "leve":
        return "moderada"
    elif gravidade == "moderada":
        return "grave"
    
    return gravidade

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
        return render_template("hospital.html", hospital_list=hospital_data)
        
 
    @web.route("/predict", methods=['POST'])
    def predict():
        if model_catboost is None:
            return jsonify({"error": "Modelo não carregado"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON de dados não enviado"}), 400

      
        horario_agora = datetime.now().hour
        if horario_agora >= 0 and horario_agora < 6:
            horario = "Madrugada"               
        elif horario_agora >= 6 and horario_agora < 18:               
            horario = "Diurno" 
        else: 
            horario = "Noturno"
            
      
        sintoma = data.get("sintoma")
        zona = data.get("zona")
        idade = data.get("idade")
        comorbidade = data.get("comorbidade")
        # Usa lotação do input ou default 0.7
        lotacao = data.get("lotacao", 0.7) 
        
      
        if not all([sintoma, zona, idade, comorbidade]):
            return jsonify({"error": "Campos obrigatórios (sintoma, zona, idade, comorbidade) faltando."}), 400

      
        if sintoma not in SINTOMAS_BASE:
            return jsonify({"error": f"Sintoma '{sintoma}' não reconhecido"}), 400
        
        
        info_sintoma = SINTOMAS_BASE[sintoma]
        complexidade = info_sintoma['complexidade']
        gravidade_base = info_sintoma['gravidade']
        
        
        gravidade_ajustada = ajustar_gravidade_por_idade(gravidade_base, idade)
    
        target_hospital = None
        if sintoma in SINTOMAS_PROCAPE: 
            gravidade_ajustada = "grave"
            complexidade = "alta"
            target_hospital = "PROCAPE"
     
        dados_paciente = {
            "Sintoma": sintoma,
            "Comorbidades": comorbidade,
            "Idade": idade,
            "Complexidade": complexidade,        
            "Gravidade": gravidade_ajustada, 
            "Horario": horario, 
            "Zona_Residencia": zona,
            "Lotacao_No_Momento": lotacao    
        }    
            
        try:
          
            df_amostra = pd.DataFrame([dados_paciente])
            df_com_features = criar_features_especificas_upas(df_amostra, hospital_alvo=target_hospital) 
           
            features_esperadas = list(model_catboost.feature_names_)
                
           
            for col in ['Sintoma', 'Comorbidades', 'Complexidade', 'Gravidade', 'Horario', 'Zona_Residencia']:
                if col in df_com_features.columns:
                    df_com_features[col] = df_com_features[col].astype(str)

            X_pred = df_com_features[features_esperadas]
                
            predicao = model_catboost.predict(X_pred).flatten()[0]
                
          
            hospital_name = str(predicao)
        
                
          
            if hospital_name == "HC/UFPE":
                hospital_name = "Hospital das Clínicas"
                hospital_url = "hospital-das-clinicas-hc-ufpe"

          
            return jsonify({
                "hospital_name": hospital_name, 
                "redirect_url": f"/hospital/{hospital_name}"
            }), 200   
            
        except Exception as e:
           
            print(f"Erro inesperado durante a predição: {e}")
            return jsonify({"error": f"Erro interno na predição: {str(e)}"}), 500
    
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
        
       
        if model_catboost is None:
            return jsonify({"success": False, "error": "Modelo de predição não carregado"}), 500
    
        try:
            df_amostra = pd.DataFrame([dados_paciente_teste])
            df_com_features = criar_features_especificas_upas(df_amostra)
            features_esperadas = model_catboost.feature_names_
            X_pred = df_com_features[features_esperadas]
        
           
            predicao = model_catboost.predict(X_pred).flatten()[0]
            
            resultado_json = {
                "success": True,
                "hospital_sugerido": str(predicao) 
            }

           
            return redirect(url_for("web.details_hospitals", name_hospital=resultado_json['hospital_sugerido']))

        except Exception as e:
            print(f"Erro  no teste de predição: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    @web.route("/dashboard")
    def dashboard():
       return render_template("dashboard.html")
    return web