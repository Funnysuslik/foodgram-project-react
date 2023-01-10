FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt update && apt install -y libpq-dev gcc

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["bash", "./enterypoint.sh"]