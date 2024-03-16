FROM python:3.9

RUN pip install --upgrade pip

WORKDIR /app
COPY . /app

RUN pip install -r ./requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
