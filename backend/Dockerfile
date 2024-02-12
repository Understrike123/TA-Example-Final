FROM python:3.7

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python3 main.py SEISMIC2D--test_LINE_EW_PERIHAKA_100