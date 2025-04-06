FROM python:3.8

ENV HOME /root
WORKDIR /root

COPY ./requirements.txt ./requirements.txt
COPY ./server.py ./server.py
COPY ./public ./public
COPY ./util ./util

RUN pip3 install -r requirements.txt && apt-get update && apt-get install -y ffmpeg
RUN pip install ffmpeg-python

EXPOSE 8000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 -u server.py
