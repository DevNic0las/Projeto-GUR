FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências primeiro: qualquer mudança em .py não invalida esta camada.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # O catboost declara matplotlib/plotly/graphviz como obrigatórios,
    # mas a API só carrega scipy deles. Remove ~130 MB de libs não usadas.
    pip uninstall -y matplotlib plotly graphviz contourpy cycler fonttools \
        kiwisolver pyparsing pillow narwhals

# Código por último.
COPY . .

CMD ["python", "-m", "flask_package.run"]
