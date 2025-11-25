from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from flask_package.config_sintomas_base import SINTOMAS_BASE
from flask_package.config_sintomas_base import SINTOMAS_PROCAPE
from datetime import datetime 
import pandas as pd


def criar_features_especificas_upas(df):
    """
    Cria as features Score_Proximidade e Score_Lotacao. 
    Para predição (sem 'Hospital_Recomendado'), usa o score máximo de proximidade para a zona.
    """
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
    else:
        def calcular_score_zona(zona):
            if zona in proximidade_map:
                scores = list(proximidade_map[zona].values())
                return max(scores)  
            return 0.7  # Fallback
        
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

        # 1. TRATAMENTO DO HORÁRIO (3 categorias: Madrugada, Diurno, Noturno)
        horario_agora = datetime.now().hour
        if horario_agora >= 0 and horario_agora < 6:
            horario = "Madrugada"               
        elif horario_agora >= 6 and horario_agora < 18:               
            horario = "Diurno" 
        else: # 18h - 24h
            horario = "Noturno"
            
        # 2. COLETA E VALIDAÇÃO DE DADOS
        sintoma = data.get("sintoma")
        zona = data.get("zona")
        idade = data.get("idade")
        comorbidade = data.get("comorbidade")
        # Usa lotação do input ou default 0.7
        lotacao = data.get("lotacao", 0.7) 
        
        # Validação de campos obrigatórios
        if not all([sintoma, zona, idade, comorbidade]):
            return jsonify({"error": "Campos obrigatórios (sintoma, zona, idade, comorbidade) faltando."}), 400

        # Validação do sintoma: se não estiver na base, retorna erro.
        if sintoma not in SINTOMAS_BASE:
            return jsonify({"error": f"Sintoma '{sintoma}' não reconhecido"}), 400
        
        # 3. EXTRAÇÃO E AJUSTE DA GRAVIDADE 
        info_sintoma = SINTOMAS_BASE[sintoma]
        complexidade = info_sintoma['complexidade']
        gravidade_base = info_sintoma['gravidade']
        
        # APLICAÇÃO DA REGRA CLÍNICA 1: Fragilidade Geriátrica
        gravidade_ajustada = ajustar_gravidade_por_idade(gravidade_base, idade)
        
        
        if sintoma in SINTOMAS_PROCAPE and zona == "Centro":
            gravidade_ajustada = "emergencia"
            complexidade = "alta"
            
        # 4. MONTAGEM DO DICIONÁRIO DE DADOS
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
            # 5. PREDIÇÃO
            df_amostra = pd.DataFrame([dados_paciente])
            df_com_features = criar_features_especificas_upas(df_amostra) 
                
            features_esperadas = list(model_catboost.feature_names_)
                
            # Converte features categóricas para string (boa prática)
            for col in ['Sintoma', 'Comorbidades', 'Complexidade', 'Gravidade', 'Horario', 'Zona_Residencia']:
                if col in df_com_features.columns:
                    df_com_features[col] = df_com_features[col].astype(str)

            X_pred = df_com_features[features_esperadas]
                
            predicao = model_catboost.predict(X_pred).flatten()[0]
                
            # 6. RETORNO PADRONIZADO
            hospital_name = str(predicao)
        
                
            # Apenas para o caso específico do HC/UFPE
            if hospital_name == "HC/UFPE":
                hospital_name = "Hospital das Clínicas (HC/UFPE)"
                hospital_url = "hospital-das-clinicas-hc-ufpe"

            # Garante que o retorno é sempre consistente
            return jsonify({
                "hospital_name": hospital_name, 
                "redirect_url": f"/hospital/{hospital_name}"
            }), 200   
            
        except Exception as e:
            # Retorna o erro de forma segura
            print(f"Erro inesperado durante a predição: {e}")
            return jsonify({"error": f"Erro interno na predição: {str(e)}"}), 500
    
    @web.route("/test/predict")
    def test_predict():
        # Indentação corrigida em todo o bloco da função
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
        
        # Verifica se o modelo está carregado antes de prosseguir
        if model_catboost is None:
            return jsonify({"success": False, "error": "Modelo de predição não carregado"}), 500
    
        try:
            df_amostra = pd.DataFrame([dados_paciente_teste])
            df_com_features = criar_features_especificas_upas(df_amostra)
            features_esperadas = model_catboost.feature_names_
            X_pred = df_com_features[features_esperadas]
        
            # Faz a predição (geralmente retorna um numpy array)
            predicao = model_catboost.predict(X_pred).flatten()[0]
            
            resultado_json = {
                "success": True,
                "hospital_sugerido": str(predicao) 
            }

            # Redireciona para a página de detalhes do hospital sugerido
            return redirect(url_for("web.details_hospitals", name_hospital=resultado_json['hospital_sugerido']))

        except Exception as e:
            print(f"❌ Erro detalhado no teste de predição: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return web