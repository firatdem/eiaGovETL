FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && \
    pip install fastapi uvicorn snowflake-connector-python python-dotenv

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
