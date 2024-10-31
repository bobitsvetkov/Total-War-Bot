FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install virtualenv

RUN virtualenv venv

RUN ./venv/bin/pip install -r requirements.txt

COPY . .

CMD ["./venv/bin/python", "main.py"]