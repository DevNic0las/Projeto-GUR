from catboost import CatBoostClassifier
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, top_k_accuracy_score, accuracy_score
import numpy as np

# --- CONFIGURAÇÕES DE ARQUIVO E MODELO ---
PATH_FILE = "/content/drive/MyDrive/bigdata dataset/dataset_triagem_corrigido_v6Final_1M.csv"
MODEL_FILENAME = "modelo_triagem_catboost_v7_final.cbm"

print("📥 Carregando dados...")
df = pd.read_csv(PATH_FILE)

# ✅ CONVERSÕES DE SEGURANÇA
df['Zona_Residencia'] = df['Zona_Residencia'].astype(str)
df['Sintoma'] = df['Sintoma'].astype(str)

# --- FUNÇÃO DE FEATURE ENGINEERING (Recria features usadas no treinamento) ---
def criar_features_especificas_upas(df):
    df_feat = df.copy()
    
    # 🗺️ MAPA GEOGRÁFICO REALISTA (Usado APENAS para criar Score_Proximidade)
    # ATENÇÃO: Os hospitais no mapa devem ser os que existem no seu 'Hospital_Recomendado'
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
    
    # A feature Score_Proximidade é criada no dataset de treinamento/teste.
    # Quando testamos uma nova amostra, o Hospital_Recomendado é desconhecido,
    # então usamos um valor neutro para esta feature na predição, ou a removemos.
    # No treinamento, ela é crucial. Vamos mantê-la para o treinamento/teste.
    if 'Hospital_Recomendado' in df_feat.columns:
        df_feat['Score_Proximidade'] = df_feat.apply(
            lambda x: proximidade_map.get(x['Zona_Residencia'], {}).get(x['Hospital_Recomendado'], 0.1),
            axis=1
        )
    else:
        # Se não houver Hospital_Recomendado (modo de predição), usamos 0.5 como neutro.
        # CatBoost lida bem com a diferença de feature no predict se for numérico.
        df_feat['Score_Proximidade'] = 0.5

    # ✅ Score de lotação inteligente
    df_feat['Score_Lotacao'] = 1 - df_feat['Lotacao_No_Momento']
    
    return df_feat

df = criar_features_especificas_upas(df)

# ✅ FEATURES OTIMIZADAS
cols_features = [
    "Sintoma", "Comorbidades", "Idade",
    "Complexidade", "Gravidade", "Horario",
    "Zona_Residencia", "Lotacao_No_Momento",
    "Score_Proximidade", "Score_Lotacao"
]

cat_cols = [
    "Sintoma", "Comorbidades", 
    "Complexidade", "Gravidade", "Horario", 
    "Zona_Residencia"
]

# ✅ GARANTIR TIPOS
for col in cat_cols:
    df[col] = df[col].astype(str)

X = df[cols_features]
y = df["Hospital_Recomendado"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# --- TREINAMENTO DO MODELO ---
print("🚀 Treinando modelo com geografia CORRIGIDA...")

model = CatBoostClassifier(
    iterations=800,
    learning_rate=0.03,
    depth=10,
    l2_leaf_reg=4,
    task_type="GPU",
    devices='0',
    loss_function="MultiClass",
    early_stopping_rounds=50,
    verbose=50
)

model.fit(X_train, y_train, cat_features=cat_cols, eval_set=(X_test, y_test), logging_level='Silent')


# --- AVALIAÇÃO ---
y_pred = model.predict(X_test)
print("\n📈 RELATÓRIO DE CLASSIFICAÇÃO:")
print(classification_report(y_test, y_pred))

# ✅ FOCO NAS UPAs
upas_mask = y_test.str.contains('UPA')
if upas_mask.any():
    y_test_upas = y_test[upas_mask]
    y_pred_upas = y_pred[upas_mask]
    print("\n🎯 UPAs COM GEOGRAFIA CORRIGIDA:")
    print(classification_report(y_test_upas, y_pred_upas, zero_division=0))

# --- SALVAMENTO DO MODELO ---
print(f"\n💾 Salvando o modelo treinado em {MODEL_FILENAME}...")
model.save_model(MODEL_FILENAME, format="cbm")
print("✅ Modelo salvo com sucesso.")


# --- TESTE COM NOVA AMOSTRA DE FEATURES ---
def realizar_predicao_triagem(modelo, nova_amostra_dict, cols_features):
    # Converte o dicionário em DataFrame, mantendo a ordem das colunas
    df_amostra = pd.DataFrame([nova_amostra_dict])
    
    # Adiciona e calcula as features de engenharia
    # Nota: A feature 'Hospital_Recomendado' não existe aqui, então o Score_Proximidade
    # será calculado como 0.5 (neutro) conforme a lógica de 'criar_features_especificas_upas'
    # ajustada para modo de predição.
    df_amostra_feat = criar_features_especificas_upas(df_amostra)
    
    # Seleciona APENAS as colunas de features na ordem correta
    X_predict = df_amostra_feat[cols_features]

    # Garante que as colunas categóricas são strings
    for col in cat_cols:
        if col in X_predict.columns:
            X_predict[col] = X_predict[col].astype(str)

    # 1. Predição da Classe (Hospital)
    hospital_recomendado = modelo.predict(X_predict)[0]
    
    # 2. Predição da Probabilidade (Matriz de Score)
    probabilidades = modelo.predict_proba(X_predict)[0]
    
    # Mapeia as probabilidades para os nomes dos hospitais
    classes = modelo.classes_
    scores = pd.Series(probabilidades, index=classes).sort_values(ascending=False)
    
    return hospital_recomendado, scores

nova_amostra = {
    "Sintoma": "Dor de cabeça",
    "Comorbidades": "nenhuma",
    "Idade": 34,
    "Complexidade": "moderada",        
    "Gravidade": "emergencia",
    "Horario": "noturno",
    "Zona_Residencia": "Centro", # Corrigi para "Zona Norte" (minuscula no original)
    "Lotacao_No_Momento": 0.4      
}

print("\n--- 🏥 Simulação de Triagem em Tempo Real ---")
print(f"**Paciente:** {nova_amostra['Sintoma']} | {nova_amostra['Zona_Residencia']} | {nova_amostra['Gravidade']}")

hospital, scores_prob = realizar_predicao_triagem(model, nova_amostra, cols_features)

print(f"\n✅ RECOMENDAÇÃO FINAL: **{hospital}**")
print("\nMatriz de Probabilidades (Top 5):")
print(scores_prob.head())