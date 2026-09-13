FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY services/recording-worker/requirements.txt \
     /app/requirements.txt

RUN pip install \
    --no-cache-dir \
    -r /app/requirements.txt

COPY services/recording-worker/app \
     /app/app

CMD ["python", "-m", "app.main"]