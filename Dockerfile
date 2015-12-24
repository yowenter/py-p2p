FROM python:2.7.9

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8001
EXPOSE 8002
EXPOSE 8003

CMD ["python","udp_broker.py" ]
