import pandas as pd
import joblib
from datetime import datetime

# --- Modelagem ---
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

# --- Configuração ---
DATA_FILE = "../data/parquet/dataset_sintomas_4M_balanceado_v6_definitivo.parquet"
MODEL_OUT = "hospital_xgb_pipeline_otimizado_v6_treino.pkl"
ENCODER_OUT = "hospital_label_encoder_v6.pkl"
RANDOM_STATE = 42

# ===============================================
# 1. Carregar os Dados
# ===============================================
print(f"📥 Carregando dados de {DATA_FILE}...")
try:
    df = pd.read_parquet(DATA_FILE, engine='pyarrow')
except FileNotFoundError:
    print(f"❌ ERRO: Arquivo '{DATA_FILE}' não encontrado.")
    exit()
except Exception as e:
    print(f"⚠️ Tentando ler como CSV: {e}")
    df = pd.read_csv('dataset_sintomas_4M_balanceado_v5.csv')

print(f"📊 Dados carregados: {len(df):,} linhas")

# ===============================================
# 2. Definir X e y
# ===============================================
DROP_COLS = ['ID', 'Diagnostico', 'Hospital_Recomendado']
TARGET_COL = 'Hospital_Recomendado'

cols_to_drop_actual = [col for col in DROP_COLS if col in df.columns]
X = df.drop(columns=cols_to_drop_actual)
y_raw = df[TARGET_COL]

print("✅ Features (X) e Alvo (y) definidos.")

# ===============================================
# 3. Encode do Alvo
# ===============================================
le = LabelEncoder()
y = le.fit_transform(y_raw)
print(f"🏷 Alvo codificado. Classes: {len(le.classes_)}")

# ===============================================
# 4. Divisão Treino / Teste
# ===============================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

# (Opcional: Separar validação, mas não vamos usar no fit do pipeline direto para evitar erro)
print(f"✂ Treino: {len(X_train):,}")
print(f"🧪 Teste: {len(X_test):,}")

# ===============================================
# 5. Pipeline de Pré-processamento
# ===============================================
numeric_features = ['Idade', 'Dificuldade_Decisao']
categorical_features = ['Sintoma', 'Especialidade', 'Comorbidades', 'Horario', 'Complexidade', 'Gravidade']

# Filtra apenas colunas existentes
numeric_features = [c for c in numeric_features if c in X.columns]
categorical_features = [c for c in categorical_features if c in X.columns]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ],
    remainder='drop'
)

print("⚙ Pipeline de pré-processamento configurado.")

# ===============================================
# 6. Modelo XGBoost (CORRIGIDO)
# ===============================================
model = XGBClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    tree_method='hist',
    objective='multi:softmax',
    num_class=len(le.classes_),
    eval_metric='mlogloss',
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbosity=1
    # REMOVIDO: early_stopping_rounds=30 (Isso causava o erro sem eval_set)
)
print("🤖 Modelo XGBClassifier configurado (sem Early Stopping no Pipeline).")

# ===============================================
# 7. Pipeline Completo
# ===============================================
full_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', model)
])

print("\n🚀 Iniciando treinamento...")
start = datetime.now()

# Treinamento direto (sem eval_set para não quebrar o pipeline)
full_pipeline.fit(X_train, y_train)

end = datetime.now()
print(f"✅ Treinamento concluído em: {end - start}")

# ===============================================
# 8. Avaliação
# ===============================================
print("\n" + "="*50)
print("🎯 AVALIAÇÃO")
print("="*50)

y_pred = full_pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"📊 Acurácia: {acc:.4f}")

# ===============================================
# 9. Salvar Artefatos
# ===============================================
joblib.dump(full_pipeline, MODEL_OUT)
joblib.dump(le, ENCODER_OUT)

print(f"\n💾 Modelo salvo em: {MODEL_OUT}")
print(f"💾 LabelEncoder salvo em: {ENCODER_OUT}")

# ===============================================
# 10. Teste Rápido
# ===============================================
print("\n🧪 Testando 'Sangramento na urina'...")
caso_teste = pd.DataFrame([{
    "Sintoma": "Sangramento na urina",
    "Especialidade": "Urologia",
    "Complexidade": "moderada",
    "Dificuldade_Decisao": 0.5,
    "Idade": 45,
    "Comorbidades": "nenhuma",
    "Gravidade": "moderado",
    "Horario": "diurno"
}])

try:
    pred = full_pipeline.predict(caso_teste)
    print(f"✅ Resultado: {le.inverse_transform(pred)[0]}")
except Exception as e:
    print(f"❌ Erro: {e}")