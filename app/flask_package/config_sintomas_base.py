SINTOMAS_BASE = {
    "Dor de cabeça": {"categorias": ["Neurologia", "Clínica Médica", "Psiquiatria"], "prob": [0.5, 0.4, 0.1], "complexidade": "moderada", "gravidade": "leve"},
    "Dor intensa após queda ou pancada": {"categorias": ["Traumatologia", "Ortopedia"], "prob": [0.8, 0.2], "complexidade": "alta", "gravidade": "grave"},
    "Não consegue mover o membro": {"categorias": ["Traumatologia", "Ortopedia", "Neurologia"], "prob": [0.6, 0.3, 0.1], "complexidade": "alta", "gravidade": "grave"},
    "Coração acelerado": {"categorias": ["Cardiologia", "Psiquiatria", "Endocrinologia"], "prob": [0.5, 0.3, 0.2], "complexidade": "moderada", "gravidade": "moderado"},
    "Dor no peito": {"categorias": ["Cardiologia", "Pneumologia", "Gastroenterologia"], "prob": [0.6, 0.2, 0.2], "complexidade": "alta", "gravidade": "grave"},
    "Chiado no peito": {"categorias": ["Pneumologia", "Alergologia", "Cardiologia"], "prob": [0.7, 0.2, 0.1], "complexidade": "moderada", "gravidade": "moderado"},
    "Febre alta (acima de 38°C)": {"categorias": ["Infectologia", "Pediatria", "Clínica Médica"], "prob": [0.6, 0.2, 0.2], "complexidade": "moderada", "gravidade": "moderado"},
    "Tosse seca": {"categorias": ["Infectologia", "Alergologia", "Pneumologia"], "prob": [0.5, 0.3, 0.2], "complexidade": "baixa", "gravidade": "leve"},
    "Tosse com catarro": {"categorias": ["Infectologia", "Pneumologia"], "prob": [0.6, 0.4], "complexidade": "baixa", "gravidade": "leve"},
    "Dor de garganta": {"categorias": ["Infectologia", "Clínica Médica"], "prob": [0.7, 0.3], "complexidade": "baixa", "gravidade": "leve"},
    "Dor de barriga": {"categorias": ["Gastroenterologia", "Ginecologia", "Urologia"], "prob": [0.6, 0.2, 0.2], "complexidade": "moderada", "gravidade": "moderado"},
    "Vômito": {"categorias": ["Gastroenterologia", "Infectologia", "Neurologia"], "prob": [0.5, 0.3, 0.2], "complexidade": "moderada", "gravidade": "moderado"},
    "Diarreia": {"categorias": ["Gastroenterologia", "Infectologia"], "prob": [0.7, 0.3], "complexidade": "moderada", "gravidade": "moderado"},
    "Coriza": {"categorias": ["Alergologia", "Infectologia", "Pediatria"], "prob": [0.4, 0.4, 0.2], "complexidade": "baixa", "gravidade": "leve"},
    "Queimadura": {"categorias": ["Traumatologia", "Dermatologia"], "prob": [0.8, 0.2], "complexidade": "alta", "gravidade": "grave"},
    "Corte profundo": {"categorias": ["Traumatologia", "Cirurgia Geral"], "prob": [0.7, 0.3], "complexidade": "alta", "gravidade": "grave"},
    "Sangramento na urina": {"categorias": ["Urologia", "Ginecologia", "Nefrologia"], "prob": [0.5, 0.3, 0.2], "complexidade": "moderada", "gravidade": "moderado"},
    "Tontura": {"categorias": ["Neurologia", "Cardiologia", "Clínica Médica"], "prob": [0.4, 0.3, 0.3], "complexidade": "moderada", "gravidade": "moderado"},
    "Falta de ar": {"categorias": ["Pneumologia", "Cardiologia", "Psiquiatria"], "prob": [0.5, 0.3, 0.2], "complexidade": "alta", "gravidade": "grave"},
    "Convulsão": {"categorias": ["Neurologia", "Emergência"], "prob": [0.7, 0.3], "complexidade": "alta", "gravidade": "alta"}
}
SINTOMAS_PROCAPE = ["Dor no peito", "Coração acelerado", "Falta de ar"]