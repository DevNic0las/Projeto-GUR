import pandas as pd
from catboost import CatBoostClassifier
import numpy as np


print("Carregando modelo e dados...")
model = CatBoostClassifier()
model.load_model('./modelo_triagem_catboost_v7_final.cbm')


X_test = pd.read_csv('./X_test_features.csv') 
y_test = pd.read_csv('./y_test_target.csv')


print("Executando predições...")
predictions = model.predict(X_test).ravel()
probabilities = model.predict_proba(X_test)


df_performance = X_test.copy()


df_performance["Hospital_Predito"] = predictions
df_performance["Confianca_Predita"] = probabilities.max(axis=1)


df_performance["Hospital_Real"] = y_test.iloc[:, 0].values 


df_performance["Acerto"] = df_performance["Hospital_Predito"] == df_performance["Hospital_Real"]


print("\n--- Primeiras 5 linhas ---")
print(df_performance[['Hospital_Real', 'Hospital_Predito', 'Confianca_Predita', 'Acerto']].head())

OUTPUT_FILENAME = "analise_performance_catboost.csv"
df_performance.to_csv(OUTPUT_FILENAME, index=False)

print(f"\nTabela Fato de Desempenho criada: {OUTPUT_FILENAME}")