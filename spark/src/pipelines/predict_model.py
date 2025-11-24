import pandas as pd
from catboost import CatBoostClassifier
import matplotlib.pyplot as plt
import seaborn as sns


model = CatBoostClassifier()
model.load_model('/content/modelo_triagem_catboost_v10_final_definitivo.cbm')


X_test = pd.read_csv('/content/X_test_features.csv')
y_test = pd.read_csv('/content/y_test_target.csv') 


predictions = model.predict(X_test).ravel()
probabilities = model.predict_proba(X_test)  


resultados_df = X_test.copy()
resultados_df["Predicao_CatBoost"] = predictions

resultados_df["Probabilidade"] = probabilities.max(axis=1)


print(resultados_df.head())



import pandas as pd
from catboost import CatBoostClassifier
import numpy as np

# 1. Carregar modelo e dados de teste
model = CatBoostClassifier()
model.load_model('/content/modelo_triagem_catboost_v10_final_definitivo.cbm')

X_test = pd.read_csv('/content/X_test_features.csv')
y_test = pd.read_csv('/content/y_test_target.csv')
y_test_target = y_test.iloc[:, 0] # Assume que o target é a primeira coluna

# 2. Gerar predições e probabilidades
y_pred = model.predict(X_test).ravel()
probabilities = model.predict_proba(X_test)

# 3. Criar a Tabela Fato de Desempenho
# Copia as features
df_performance = X_test.copy() 

# Adiciona o Valor Real (Target)
df_performance['Hospital_Real'] = y_test_target.values

# Adiciona a Predição e a Confiança
df_performance['Hospital_Predito'] = y_pred
df_performance['Confianca_Predita'] = probabilities.max(axis=1)

# Adiciona uma coluna de Acerto (True/False)
df_performance['Acerto'] = df_performance['Hospital_Predito'] == df_performance['Hospital_Real']

# 4. Salvar o arquivo final para o Power BI
OUTPUT_FILENAME = "analise_performance_catboost.csv"
df_performance.to_csv(OUTPUT_FILENAME, index=False)

print(f"\n✅ Tabela Fato de Desempenho criada e salva em: {OUTPUT_FILENAME}")