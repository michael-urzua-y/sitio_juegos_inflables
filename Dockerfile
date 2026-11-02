FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    INSTANCE_DIR=/data \
    PORT=8000

WORKDIR /app

# Usuario sin privilegios
RUN useradd --create-home --uid 1000 appuser \
 && mkdir -p /data/uploads && chown -R appuser:appuser /data

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000
VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/healthz' % os.environ.get('PORT','8000'))" || exit 1

# --preload: crea tablas y datos iniciales una sola vez antes de levantar los workers
CMD gunicorn wsgi:app --preload --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-3} \
    --access-logfile - --forwarded-allow-ips="*"
