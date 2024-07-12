FROM python:3.12-slim
EXPOSE 8000
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENV DJANGO_DB_HOST="database"
RUN python manage.py downloadhumanimages 1
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]