FROM python:3.12-slim

WORKDIR /app
COPY app/ /app/app/
COPY templates/ /app/templates/

RUN python -m pip install --no-cache-dir --upgrade pip

ENTRYPOINT ["python", "-m", "app.generator"]