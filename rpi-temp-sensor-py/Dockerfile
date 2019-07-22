# BUILD IMAGE
FROM arm32v6/python:2.7-alpine3.9 as builder

RUN apk --no-cache add git build-base && \
    pip install paho-mqtt

WORKDIR /home
RUN git clone https://github.com/adafruit/Adafruit_Python_DHT.git && \
	cd Adafruit_Python_DHT && \
	python setup.py install --force-pi

# RUNTIME IMAGE
FROM arm32v6/python:2.7-alpine3.9

RUN apk --no-cache add ca-certificates

COPY --from=builder /usr/local/lib/python2.7 /usr/local/lib/python2.7
COPY *.py /home/

WORKDIR /home

ENV SENSOR="DS18B20"
ENV PIN=0
ENV PROJECT_ID=""
ENV MQTT_USER=""
ENV MQTT_PASS=""

ENTRYPOINT [ "python", "main.py" ]
