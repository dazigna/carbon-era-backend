FROM python:3

WORKDIR /app

COPY requirements.txt ./

COPY carbonera ./

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /sources

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]