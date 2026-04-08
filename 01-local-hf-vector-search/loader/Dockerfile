FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY loader/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY loader/ingest_hf.py ingest_hf.py

CMD ["python", "ingest_hf.py"]
