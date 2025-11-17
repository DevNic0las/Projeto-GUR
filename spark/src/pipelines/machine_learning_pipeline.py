#!/usr/bin/env python3
# pipeline_xgb_otimizado.py
#
# Um pipeline de machine learning OTIMIZADO para prever o hospital
# usando XGBoost e Scikit-learn.
#

import pandas as pd
import joblib
from datetime import datetime

# --- Modelagem ---
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    LabelEncoder,     # Para o alvo (y)
    OneHotEncoder,    # Para features categóricas
    OrdinalEncoder,   # Para features ordinais
    StandardScaler    # Para features numéricas
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

# --- Métricas ---
from sklearn.metrics import accuracy_score, classification_report

# --- Configuração ---
DATA_FILE = "../data/parquet/dataset_sintomas_4M_definitivo.parquet" # ⬅️ Ajuste o nome do arquivo, se necessário
MODEL_OUT = "hospital_xgb_pipeline_otimizado.pkl"
ENCODER_OUT = "hospital_label_encoder.pkl"
RANDOM_STATE = 42

# ===============================================
## 1. Carregar os Dados 📥
# ===============================================
print(f"📥 Carregando dados de {DATA_FILE}...")
try:
    # Ler o arquivo Parquet
    # Nota: Se você usar o arquivo CSV, mude para: pd.read_csv(DATA_FILE)
    df = pd.read_parquet(DATA_FILE, engine='pyarrow') 
except FileNotFoundError:
    print(f"❌ ERRO: Arquivo '{DATA_FILE}' não encontrado. Verifique o caminho.")
    print("Por favor, execute o script de geração de dados primeiro.")
    exit()

print(f"📊 Dados carregados: {len(df):,} linhas")

# ===============================================
## 2. Definir Features (X) e Alvo (y)
# ===============================================

# 🚫 Removendo colunas que não devem ser usadas no treino
DROP_COLS = ['ID', 'Diagnostico', 'Hospital_Recomendado']
TARGET_COL = 'Hospital_Recomendado'

X = df.drop(columns=DROP_COLS)
y_raw = df[TARGET_COL]

print("✅ Features (X) e Alvo (y) definidos.")

# ===============================================
## 3. Encode do Alvo (y) 🏷️
# ===============================================
# O alvo (y) deve ser numérico para o XGBoost.
le = LabelEncoder()
y = le.fit_transform(y_raw)

print(f"🏷️ Alvo '{TARGET_COL}' codificado.")
print(f"   Total de classes (hospitais): {len(le.classes_)}")

# ===============================================
## 4. Divisão de Treino e Teste ✂️
# ===============================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2, 
    random_state=RANDOM_STATE,
    stratify=y # CRÍTICO: Mantém a proporção das classes (hospitais)
)
print(f"✂️ Dados divididos: {len(X_train):,} para treino, {len(X_test):,} para teste.")

# ===============================================
## 5. Construir o Pipeline de Pré-processamento ⚙️
# ===============================================

# --- 5.1 Definir Colunas e Categorias ---

# Features Numéricas: Escaladas
numeric_features = ['Idade', 'Dificuldade_Decisao']

# Features Ordinais: Codificadas com ordem (Gravidade e Complexidade JUNTAS)
ordinal_features = ['Gravidade', 'Complexidade']
gravidade_cats = ['leve', 'moderado', 'grave', 'emergencia']
complexidade_cats = ['baixa', 'moderada', 'alta']
# A ordem aqui deve corresponder à ordem em ordinal_features
ordinal_cats = [gravidade_cats, complexidade_cats]

# Features Categóricas Nominais: One-Hot Encoding
categorical_features = ['Sintoma', 'Especialidade', 'Comorbidades', 'Horario']


# --- 5.2 Criar os Transformadores (Transformadores Únicos) ---

# 1. Numérico
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

# 2. Ordinal (Unificado)
ordinal_transformer = Pipeline(steps=[
    ('ordinal', OrdinalEncoder(categories=ordinal_cats))
])

# 3. Categórico
categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# --- 5.3 Juntar tudo com o ColumnTransformer ---
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('ord', ordinal_transformer, ordinal_features), # ⬅️ Transformador unificado
        ('cat', categorical_transformer, categorical_features)
    ],
    remainder='passthrough'
)

print("⚙️ Pipeline de pré-processamento (ColumnTransformer) criado.")

# ===============================================
## 6. Definir o Modelo (XGBoost) 🤖
# ===============================================

model = XGBClassifier(
    n_estimators=500,
    max_depth=11,
    learning_rate=0.02,
    tree_method='hist',
    objective='multi:softmax', 
    num_class=len(le.classes_), 
    random_state=RANDOM_STATE,
    n_jobs=-1,
    use_label_encoder=False,
    eval_metric='mlogloss' 
)

print("🤖 Modelo XGBClassifier configurado.")

# ===============================================
## 7. Criar e Treinar o Pipeline Final 🚀
# ===============================================

# O pipeline final: Pré-processador + Modelo
full_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', model)
])

print("\n🚀... Iniciando treinamento do pipeline completo ...")
start = datetime.now()

full_pipeline.fit(X_train, y_train)

end = datetime.now()
print(f"✅ Treinamento concluído em: {end - start}")

# ===============================================
## 8. Avaliar o Modelo 🎯
# ===============================================
print("\n" + "="*50)
print("🎯 AVALIAÇÃO DO MODELO (DADOS DE TESTE)")
print("="*50)

y_pred = full_pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"📊 Acurácia (Accuracy): {acc:.4f}")

print("\n📋 Relatório de Classificação:")
print(classification_report(
    y_test,
    y_pred,
    target_names=le.classes_,
    zero_division=0 # Evita avisos de divisão por zero para classes não previstas
))

# ===============================================
## 9. Salvar o Modelo e o Encoder 💾
# ===============================================
joblib.dump(full_pipeline, MODEL_OUT)
joblib.dump(le, ENCODER_OUT)

print(f"\n💾 Pipeline salvo em: {MODEL_OUT}")
print(f"💾 LabelEncoder salvo em: {ENCODER_OUT}")

# ===============================================
## 10. Exemplo de Previsão 🧪
# ===============================================
print("\n" + "="*50)
print("🧪 EXEMPLO DE PREVISÃO (INFERÊNCIA)")
print("="*50)

loaded_pipeline = joblib.load(MODEL_OUT)
loaded_le = joblib.load(ENCODER_OUT)

# Caso de teste (exemplo de emergência cardíaca)
caso_teste = {
    "Sintoma": "Dor no peito + tontura",
    "Especialidade": "Cardiologia",
    "Complexidade": "alta",
    "Dificuldade_Decisao": 0.9, # Aumentei a dificuldade para forçar a precisão
    "Idade": 70,
    "Comorbidades": "cardiopatia",
    "Gravidade": "emergencia",
    "Horario": "madrugada"
}

X_novo = pd.DataFrame([caso_teste])

print("Caso de teste:")
print(X_novo)

# Prever
pred_num = loaded_pipeline.predict(X_novo)
pred_proba = loaded_pipeline.predict_proba(X_novo)

# Decodificar o resultado
hospital_recomendado = loaded_le.inverse_transform(pred_num)[0]
confianca = pred_proba.max()

print("\n--- Resultado ---")
print(f"🏥 Hospital Recomendado: **{hospital_recomendado}**")
print(f"💯 Confiança: **{confianca:.2%}**")