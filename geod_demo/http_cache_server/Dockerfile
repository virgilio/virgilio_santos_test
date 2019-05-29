FROM python:3.7-alpine

WORKDIR /usr/src/app
ENV FLASK_APP="server.py"
ENV FLASK_RUN_HOST 0.0.0.0

RUN apk add --no-cache gcc g++ musl-dev linux-headers git
COPY requirements.txt ./
RUN git clone https://github.com/virgilio/virgilio_santos_test.git --depth 1 /usr/src/geod_lrucache

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install /usr/src/geod_lrucache/geod_lrucache/

COPY . .
EXPOSE 5000
CMD [ "flask", "run" ]