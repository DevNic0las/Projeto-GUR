import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# =========================
# 1) Carrega o dataset
# =========================
df = pd.read_csv("../data/csv/pacientes_com_hospital.csv")
df["sintomas"] = df["sintomas"].apply(eval)

# =========================
# 2) Normalização de sintomas
# =========================

sintomas_normalizados = {
    "dor no peito": "Dor no peito",
    "coração acelerado": "Coração acelerado",
    "peito doendo": "Dor no peito",
    "taquicardia": "Coração acelerado",
    "febre": "Febre alta (acima de 38°C)",
    "febre alta": "Febre alta (acima de 38°C)",
    "febre baixa": "Febre baixa (até 38°C)",
    "tosse": "Tosse seca",
    "tosse seca": "Tosse seca",
    "tosse com catarro": "Tosse com catarro"
}

def normalizar_sintoma(s):
    s = s.lower().strip()
    return sintomas_normalizados.get(s, None)

# =========================
# 3) Vetorização multi-hot
# =========================
mlb = MultiLabelBinarizer()
X = mlb.fit_transform(df["sintomas"])

# =========================
# 4) Codificação do y
# =========================
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(df["hospital_recomendado"])

# =========================
# 5) Train/Test Split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.25, random_state=42
)

# =========================
# 6) Modelo XGBoost
# =========================
model = XGBClassifier(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.08,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="multi:softmax",
    eval_metric="mlogloss"
)

model.fit(X_train, y_train)

# =========================
# 7) Avaliação (somente terminal)
# =========================
y_pred = model.predict(X_test)

print("\n📌 ACCURACY:", round(accuracy_score(y_test, y_pred), 3))

print("\n📌 RELATÓRIO DE CLASSIFICAÇÃO:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# =========================
# 8) Função final de recomendação
# =========================
def recomendar_hospital(sintomas_usuario):
    # normaliza sintomas
    sintomas_norm = [normalizar_sintoma(s) for s in sintomas_usuario]
    sintomas_norm = [s for s in sintomas_norm if s is not None]

    if not sintomas_norm:
        return "Sintomas desconhecidos — não foi possível classificar."

    X_user = mlb.transform([sintomas_norm])
    pred_num = model.predict(X_user)[0]
    hospital_pred = label_encoder.inverse_transform([pred_num])[0]

    # print explicação simples
    print("\n🔍 Sintomas normalizados usados no modelo:", sintomas_norm)
    print("🔍 Vetor multi-hot do paciente:", X_user.tolist())

    return hospital_pred

# =========================
# 9) Exemplo
# =========================
entrada = ["dor no peito", "coração acelerado"]
print("\nHospital recomendado:", recomendar_hospital(entrada))
