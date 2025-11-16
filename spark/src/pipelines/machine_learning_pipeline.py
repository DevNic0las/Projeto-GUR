#!/usr/bin/env python3
# machine_learning_pipeline_xgb.py
# Pipeline seguro e pronto para treinar XGBoost no seu dataset (parquet).

import os
import ast
import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from datetime import datetime
from collections import Counter

from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score,
    classification_report, confusion_matrix
)
from xgboost import XGBClassifier

# ---------------------
# Configurações
# ---------------------
PARQUET_DIR = "../data/parquet"   # ajuste se necessário
SAMPLE_FRAC = 0.05                # exemplo: 5% pra teste rápido; 1.0 pra rodar full
RANDOM_STATE = 42
TEST_SIZE = 0.20

MODEL_OUT = "pipeline_xgb_joblib.pkl"
ENCODERS_OUT = "mlb_labelencoder_joblib.pkl"

# ---------------------
# Regras (mapa sintomas -> "especialidade necessária")
# (Simples heurística baseada nos seus CATEGORIAS)
# ---------------------
SINTOMA_TO_ESP = {
    # Trauma / Ortopedia
    "Dor intensa após queda ou pancada": "Ortopedia/Trauma",
    "Não consegue mover o membro (Suspeita de Fratura)": "Ortopedia/Trauma",
    "Fratura": "Ortopedia/Trauma",
    "Corte": "Trauma",
    "Queimadura": "Queimadura/Trauma",

    # Cardio
    "Coração acelerado": "Cardiologia",
    "Dor no peito": "Cardiologia",
    "Chiado no peito": "Cardiologia",

    # Infecto / Respiratorio
    "Febre alta (acima de 38°C)": "Infectologia/Clínica",
    "Tosse seca": "Pneumologia/Infectologia",
    "Tosse com catarro": "Pneumologia/Infectologia",
    "Dor de garganta": "Infectologia",

    # Gastro
    "Dor de barriga": "Gastro",
    "Vômito": "Gastro",
    "Diarreia": "Gastro",

    # Pediatria (sintomas que com mais chance vão para pediatria se criança)
    "Coriza": "Pediatria",
    "Prisão de ventre": "Pediatria",

    # Gineco (coloquei placeholders; o gerador pode produzir mais)
    "Sangramento na urina": "Ginecologia/Urologia",

    # Geral fallback
    "Dor de cabeça": "Clínica Geral",
    "Cansaço extremo ou Fadiga": "Clínica Geral",
    "Mal-estar": "Clínica Geral",
    "Espirros": "Clínica Geral",
    "Gases": "Gastro",
    "Tontura": "Neurologia/Clínica",
    "Suor excessivo": "Clínica Geral",
    "Olho vermelho ou irritado": "Oftalmologia/Clínica",
}

# ---------------------
# Helpers seguros para parse
# ---------------------
def to_list_safe(x):
    """Garante que x vire sempre uma lista de strings sem explodir."""
    if isinstance(x, list):
        return x
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return []
    if isinstance(x, (int, float)):
        return [str(x)]
    if isinstance(x, str):
        s = x.strip()
        # strings simples "Diabetes" -> ["Diabetes"]
        if not s:
            return []
        # tenta literal_eval se parece lista
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
            try:
                val = ast.literal_eval(s)
                if isinstance(val, (list, tuple)):
                    return [str(i) for i in val]
            except Exception:
                # segue abaixo
                pass
        # se for CSV-like "a, b, c"
        if "," in s:
            parts = [p.strip() for p in s.split(",") if p.strip()]
            return parts if parts else [s]
        # fallback: string simples
        return [s]
    # qualquer outro tipo
    try:
        return list(x)
    except Exception:
        return [str(x)]


def infer_especialidade_necessaria(sintomas: list):
    """Heurística simples: conta mapping e retorna a especialidade mais frequente."""
    if not sintomas:
        return "Clínica Geral"
    votes = []
    for s in sintomas:
        if s in SINTOMA_TO_ESP:
            votes.append(SINTOMA_TO_ESP[s])
    if votes:
        return Counter(votes).most_common(1)[0][0]
    # fallback: escolher a especialidade por palavra-chave
    s_join = " ".join(sintomas).lower()
    if "card" in s_join or "coração" in s_join or "peito" in s_join:
        return "Cardiologia"
    if "trauma" in s_join or "queda" in s_join or "fratura" in s_join:
        return "Ortopedia/Trauma"
    return "Clínica Geral"

# ---------------------
# 1) Ler todos os parquet do diretório
# ---------------------
print("📥 Lendo arquivos parquet do diretório:", PARQUET_DIR)
files = [os.path.join(PARQUET_DIR, f) for f in os.listdir(PARQUET_DIR) if f.endswith(".parquet")]
if not files:
    raise SystemExit("Nenhum arquivo .parquet encontrado em " + PARQUET_DIR)

# concatena em pandas (atenção a memória para full load)
tables = [pq.read_table(f) for f in files]
df = pd.concat([t.to_pandas() for t in tables], ignore_index=True)
print(f"📊 Dataset total carregado: {len(df):,} linhas")

# ---------------------
# 2) amostra para teste rápido (ou full se SAMPLE_FRAC == 1.0)
# ---------------------
if SAMPLE_FRAC < 1.0:
    df = df.sample(frac=SAMPLE_FRAC, random_state=RANDOM_STATE).reset_index(drop=True)
print(f"📉 Amostra usada: {len(df):,} linhas (frac={SAMPLE_FRAC})")

# ---------------------
# 3) Safe parsing de colunas que podem vir como string
# ---------------------
for col in ["sintomas", "doencas_preexistentes"]:
    if col not in df.columns:
        raise SystemExit(f"Coluna esperada não encontrada no parquet: {col}")
    df[col] = df[col].apply(to_list_safe)

# ---------------------
# 4) Feature engineering
# ---------------------
df["sintomas_str"] = df["sintomas"].apply(lambda lst: " ".join(lst))
df["num_sintomas"] = df["sintomas"].apply(len)
df["idade_crianca"] = (df["idade"] < 14).astype(int)
df["idade_idoso"] = (df["idade"] >= 60).astype(int)
df["gravidade_alta"] = (df["gravidade_estimado"] > 0.7).astype(int)

# inferir "especialidade necessária" a partir dos sintomas (feature explicativa, NÃO leakage)
df["especialidade_necessaria"] = df["sintomas"].apply(infer_especialidade_necessaria)

# ---------------------
# 5) Multilabel para doencas preexistentes
# ---------------------
mlb = MultiLabelBinarizer()
doencas_bin = mlb.fit_transform(df["doencas_preexistentes"])
doencas_cols = [f"doenca_{c}" for c in mlb.classes_]
doencas_df = pd.DataFrame(doencas_bin, columns=doencas_cols, index=df.index)
df = pd.concat([df, doencas_df], axis=1)

# ---------------------
# 6) Definir features X e target y
# NÃO incluir `diagnostico_final` nem `prioridade_clinica` para evitar leakage
# ---------------------
base_categoricas = ["especialidade_necessaria"]  # categorical derived from symptoms
base_numericas = [
    "idade", "gravidade_estimado", "num_sintomas",
    "idade_crianca", "idade_idoso", "gravidade_alta"
] + doencas_cols

# Verifica existencia de target
if "hospital_recomendado" not in df.columns:
    raise SystemExit("Coluna 'hospital_recomendado' não encontrada no dataset.")

X = df[["sintomas_str"] + base_categoricas + base_numericas]
y_raw = df["hospital_recomendado"].astype(str)

# label encode target
le = LabelEncoder()
y = le.fit_transform(y_raw)

print("🏷️ Targets (hospitais):", list(le.classes_))
print("🔢 Número de classes (hospitais):", len(le.classes_))

# ---------------------
# 7) Split estratificado
# ---------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)
print(f"✂️ Split: treino={len(X_train):,} teste={len(X_test):,}")

# ---------------------
# 8) Preprocessing + XGBoost
# - CountVectorizer para sintomas (sparse)
# - OneHot para especialidade_necessaria (sparse)
# - passthrough numericas
# ColumnTransformer normalmente retorna sparse (se qualquer componente for sparse).
# XGBoost aceita CSR sparse input; usamos tree_method='hist' para escala.
# ---------------------
count_vec = CountVectorizer(max_features=120, token_pattern=r"(?u)\b\w+\b")
ohe = OneHotEncoder(handle_unknown="ignore", sparse=True)

preprocessor = ColumnTransformer(
    transformers=[
        ("sintomas", count_vec, "sintomas_str"),
        ("esp", ohe, ["especialidade_necessaria"]),
        ("num", "passthrough", base_numericas),
    ],
    sparse_threshold=0.1  # manter sparse se possível
)

# XGBoost config
xgb = XGBClassifier(
    n_estimators=600,
    max_depth=8,
    learning_rate=0.06,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="hist",
    objective="multi:softprob",
    eval_metric="mlogloss",
    use_label_encoder=False,
    n_jobs=-1,
    random_state=RANDOM_STATE
)

pipeline = Pipeline([
    ("preproc", preprocessor),
    ("clf", xgb)
])

# ---------------------
# 9) sample_weight para mitigar desbalanceamento multiclass
# calculamos weight inverso à frequência da classe no treino
# ---------------------
counts = Counter(y_train)
total_train = len(y_train)
class_weights = {cls: total_train / (len(counts) * cnt) for cls, cnt in counts.items()}
sample_weight = np.array([class_weights[c] for c in y_train])

print("⚖️ Amostras por classe (treino):")
for c, cnt in sorted(counts.items(), key=lambda x: x[0]):
    print(f"  {le.inverse_transform([c])[0]}: {cnt}")

# ---------------------
# 10) Treino com early stopping (usando parte do treino como validação)
# vamos criar X_val_small por split manual (10% do treino) e passar como eval_set
# Para passar eval_set a partir do pipeline, precisamos transformar manualmente.
# Estratégia: fit preprocessor, transformar, depois treinar XGBoost com arrays.
# ---------------------
print("\n⚙️ Preparando dados para XGBoost (transformando)...")
preproc = pipeline.named_steps["preproc"]
# fit transform preprocessor on training
X_train_trans = preproc.fit_transform(X_train)
X_test_trans = preproc.transform(X_test)

# split pequeno dentro do treino para early stopping
X_tr_sub, X_val_sub, y_tr_sub, y_val_sub, sw_tr_sub, sw_val_sub = train_test_split(
    X_train_trans, y_train, sample_weight, test_size=0.10, random_state=RANDOM_STATE, stratify=y_train
)

print("🔢 Shapes:", X_train_trans.shape, X_test_trans.shape)
print("⏱️ Iniciando treino XGBoost (com sample_weight e early stopping)...")
start = datetime.now()

# treinar o xgb do pipeline manualmente
xgb.fit(
    X_tr_sub, y_tr_sub,
    sample_weight=sw_tr_sub,
    eval_set=[(X_val_sub, y_val_sub)],
    sample_weight_eval_set=[sw_val_sub],
    early_stopping_rounds=50,
    verbose=20
)

end = datetime.now()
print("⏱️ Treino concluído em", (end - start))

# ---------------------
# 11) Avaliação
# ---------------------
y_pred = xgb.predict(X_test_trans)
acc = accuracy_score(y_test, y_pred)
bacc = balanced_accuracy_score(y_test, y_pred)

print("\n📌 MÉTRICAS (TESTE):")
print("Accuracy:", round(acc, 4))
print("Balanced Accuracy:", round(bacc, 4))
print("\n📌 Classification report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

print("\n📌 Confusion matrix (valores brutos):")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# ---------------------
# 12) Salvar artefatos: preprocessor + xgb + label encoder + mlb
# recomendo salvar pipeline com preproc + clf por compatibilidade na inferência.
# Como treinamos XGBoost separado, vamos compor um pipeline final e salvar.
# ---------------------
final_pipeline = Pipeline([("preproc", preproc), ("clf", xgb)])
joblib.dump(final_pipeline, MODEL_OUT)
joblib.dump({"label_encoder": le, "mlb": mlb}, ENCODERS_OUT)

print(f"\n✔ Modelo salvo em: {MODEL_OUT}")
print(f"✔ Encoders salvo em: {ENCODERS_OUT}")

# ---------------------
# 13) Função de inferência (exemplo)
# ---------------------
def recomendar_hospital_por_sintomas(sintomas_usuario: list, idade: int = 30, doencas_pre: list = None, gravidade: float = 0.3):
    doencas_pre = to_list_safe(doencas_pre)
    s_str = " ".join(sintomas_usuario)
    especial = infer_especialidade_necessaria(sintomas_usuario)
    num_sint = len(sintomas_usuario)
    idade_cr = 1 if idade < 14 else 0
    idade_id = 1 if idade >= 60 else 0
    grav_alta = 1 if gravidade > 0.7 else 0

    row = {
        "sintomas_str": s_str,
        "especialidade_necessaria": especial,
    }
    for ncol in base_numericas:
        # preencher numericas a partir do nome
        if ncol == "idade":
            row[ncol] = idade
        elif ncol == "gravidade_estimado":
            row[ncol] = gravidade
        elif ncol == "num_sintomas":
            row[ncol] = num_sint
        elif ncol == "idade_crianca":
            row[ncol] = idade_cr
        elif ncol == "idade_idoso":
            row[ncol] = idade_id
        elif ncol == "gravidade_alta":
            row[ncol] = grav_alta
        else:
            # doenca_* columns -> 0/1
            row[ncol] = 1 if ncol.replace("doenca_", "") in doencas_pre else 0

    X_row = pd.DataFrame([row])
    pred_num = final_pipeline.predict(X_row)[0]
    return le.inverse_transform([pred_num])[0]

# Exemplo de uso rápido
ex = ["Dor no peito", "Coração acelerado"]
print("\nExemplo de inferência:", ex, "=>", recomendar_hospital_por_sintomas(ex, idade=60, doencas_pre=["Hipertensão"], gravidade=0.8))

