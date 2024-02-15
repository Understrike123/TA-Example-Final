FROM python:3.7

WORKDIR /app

COPY requirements.txt /app

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

ADD *.py /app/

CMD python -m panel serve *.py --port 5006