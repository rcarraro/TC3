FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn python-jose

COPY ./app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
