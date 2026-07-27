FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /app appuser \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "app:app"]
