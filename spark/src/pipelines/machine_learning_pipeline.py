from catboost import CatBoostClassifier
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, top_k_accuracy_score, accuracy_score
import numpy as np


PATH_FILE = "/content/drive/MyDrive/dataset_triagem_corrigido_v6Final_1M.csv"
MODEL_FILENAME = "modelo_triagem_catboost_v7_final.cbm"

print("carregando dados...")
df = pd.read_csv(PATH_FILE)


df['Zona_Residencia'] = df['Zona_Residencia'].astype(str)
df['Sintoma'] = df['Sintoma'].astype(str)


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
      
        df_feat['Score_Proximidade'] = 0.5


    df_feat['Score_Lotacao'] = 1 - df_feat['Lotacao_No_Momento']

    return df_feat

df = criar_features_especificas_upas(df)


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


for col in cat_cols:
    df[col] = df[col].astype(str)

X = df[cols_features]
y = df["Hospital_Recomendado"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)



TEST_X_FILENAME = "X_test_features.csv"
TEST_Y_FILENAME = "y_test_target.csv"

try:

    X_test.to_csv(TEST_X_FILENAME, index=False)
    
    
    y_test.to_csv(TEST_Y_FILENAME, index=False, header=True)
    
    print(f"\n Conjunto de Teste de Features (X_test) salvo em: {TEST_X_FILENAME}")
    print(f"  Conjunto de Teste de Target (y_test) salvo em: {TEST_Y_FILENAME}")
except Exception as e:
    print(f"\n ERRO ao salvar os arquivos CSV. Verifique permissões de disco: {e}")


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



y_pred = model.predict(X_test)
print("\n RELATÓRIO DE CLASSIFICAÇÃO:")
print(classification_report(y_test, y_pred))


upas_mask = y_test.str.contains('UPA')
if upas_mask.any():
    y_test_upas = y_test[upas_mask]
    y_pred_upas = y_pred[upas_mask]
   
    print(classification_report(y_test_upas, y_pred_upas, zero_division=0))


print(f"\n Salvando o modelo treinado em {MODEL_FILENAME}...")
model.save_model(MODEL_FILENAME, format="cbm")
print("Modelo salvo com sucesso.")



def realizar_predicao_triagem(modelo, nova_amostra_dict, cols_features):
   
    df_amostra = pd.DataFrame([nova_amostra_dict])

   
    df_amostra_feat = criar_features_especificas_upas(df_amostra)

    
    X_predict = df_amostra_feat[cols_features]

  
    for col in cat_cols:
        if col in X_predict.columns:
            X_predict[col] = X_predict[col].astype(str)
            
 
    hospital_recomendado = modelo.predict(X_predict)[0]


    probabilidades = modelo.predict_proba(X_predict)[0]

 
    classes = modelo.classes_
    scores = pd.Series(probabilidades, index=classes).sort_values(ascending=False)

    return hospital_recomendado, scores

nova_amostra = {
    "Sintoma": "dor de cabeça",
    "Comorbidades": "nenhuma",
    "Idade": 25,
    "Complexidade": "moderada",
    "Gravidade": "leve",
    "Horario": "noite",
    "Zona_Residencia": "Centro",
    "Lotacao_No_Momento": 0.4
}

print("\n- Simulação de Triagem em Tempo Real ---")
print(f"**Paciente:** {nova_amostra['Sintoma']} | {nova_amostra['Zona_Residencia']} | {nova_amostra['Gravidade']}")

hospital, scores_prob = realizar_predicao_triagem(model, nova_amostra, cols_features)

print(f"\n RECOMENDAÇÃO FINAL: **{hospital}**")
print("\n Matriz de Probabilidades (Top 5):")
print(scores_prob.head())