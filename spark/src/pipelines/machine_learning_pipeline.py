import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import pandas as pd



if __name__ == "__main__":
    # 1) TREINAR XGBOOST APENAS COM SINTOMAS
    df = pd.read_csv("../data/csv/pacientes_com_hospital.csv")

    # Usar APENAS sintomas
    X = df[['sintomas']].copy()
    y = df['hospital_recomendado']

    # Converter
    le_sintomas = LabelEncoder()
    le_hospital = LabelEncoder()

    X_encoded = le_sintomas.fit_transform(X['sintomas'].astype(str))
    y_encoded = le_hospital.fit_transform(y)

    # XGBoost com UMA feature
    model_xgb = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        random_state=42
    )

    # Treinar - reshape para 2D mesmo com uma feature
    model_xgb.fit(X_encoded.reshape(-1, 1), y_encoded)

    # 2) FUNÇÃO PREDITIVA
    def recomendar_hospital_xgb(sintomas):
        sintomas_formatados = f"['{sintomas}']"
        
        try:
            sintomas_encoded = le_sintomas.transform([sintomas_formatados])
        except ValueError:
            sintomas_encoded = [0]  # Valor padrão
        
        predicao = model_xgb.predict([sintomas_encoded])
        hospital = le_hospital.inverse_transform(predicao)
        
        return hospital[0]

    # 3) TESTAR
    print(recomendar_hospital_xgb("diarreia"))
    print(recomendar_hospital_xgb("dor no braço após queda"))
    print(recomendar_hospital_xgb("Dor de cabeça"))