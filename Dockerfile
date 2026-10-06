FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY workout_api workout_api
COPY alembic alembic
COPY alembic.ini .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn workout_api.main:app --host 0.0.0.0 --port 8000"]
