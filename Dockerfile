FROM python:3.12-slim

EXPOSE 8000

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT ["./docker-entrypoint.sh"]
