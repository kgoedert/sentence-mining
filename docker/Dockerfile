FROM continuumio/anaconda3:5.1.0

RUN apt-get update
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:mc3man/trusty-media  
RUN apt-get install ffmpeg -y
RUN apt-get install frei0r-plugins -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/output
RUN chmod -R 777 /app/output
WORKDIR /app

VOLUME [ "/app" ]