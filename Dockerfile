FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./

COPY ./ ./

RUN apt update && apt install -y postgresql-client

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /sources

CMD ["python", "carbonera/manage.py", "runserver", "0.0.0.0:8000"]