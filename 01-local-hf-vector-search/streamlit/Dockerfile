FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-streamlit.txt requirements-streamlit.txt
RUN pip install --no-cache-dir -r requirements-streamlit.txt

COPY app.py app.py

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
