FROM python:3.7-slim

RUN mkdir /app

WORKDIR /app/backend

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app/backend

CMD ["gunicorn", "recipes.wsgi:application", "--bind", "0:8000" ]