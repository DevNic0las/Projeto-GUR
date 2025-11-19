import joblib
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
def predict_model():
    df = pd.DataFrame({
        'Idade': [45],
        'Dificuldade_Decisao': [3],
        'Gravidade': ['grave'],
        'Complexidade': ['alta'],
        'Especialidade': ['cardiologia'],
        'Hospital_ID': [2],
        'Sintoma': ['dor no peito'],       
        'Comorbidades': ['hipertensao'],   
        'Horario': ['manhã']  
    })
    
    model = joblib.load('./hospital_xgb_pipeline_otimizado_v4_tentativa4.pkl')
    pred = model.predict(df)
    le = joblib.load('./hospital_label_encoder_v4_tentativa4.pkl')
    pred_nome = le.inverse_transform(pred)
    
    # Gráfico simples da predição
    plt.figure(figsize=(8, 6))
    plt.bar(['Predição'], [1], color='lightblue', edgecolor='black')
    plt.text(0, 0.5, f'Resultado: {pred_nome[0]}', 
             ha='center', va='center', fontsize=12, fontweight='bold')
    plt.title('Resultado da Predição do Modelo')
    plt.ylim(0, 1.2)
    plt.axis('off')  # Remove os eixos
    plt.show()
    
    print(f"Predição: {pred_nome[0]}")
    return pred_nome[0]

predict_model()