FROM python:2.7.18-slim-buster

COPY ./requirements.txt /tmp/requirements.txt

RUN apt update
RUN apt -y upgrade
RUN apt -y install gcc libssl-dev pkg-config libcairo2-dev build-essential libffi-dev python2-dev libgirepository1.0-dev libc6-i386 tcpdump
RUN python -m pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN rm -f /tmp/requirements.txt
RUN apt -y remove gcc libssl-dev pkg-config libcairo2-dev build-essential libffi-dev python2-dev libgirepository1.0-dev
RUN apt -y autoremove
RUN apt-get -y clean
RUN mkdir -p /var/parser/dump
RUN mkdir -p /var/parser/log

COPY ./pcap_to_squid.py /var/parser/pcap_to_squid.py
COPY ./trafr /var/parser/trafr

WORKDIR /var/parser

RUN chmod +x pcap_to_squid.py
RUN chmod +x trafr

CMD timeout 10 ./trafr -s | tcpdump -r - -n "(port 80 or 443)" -w dump/dump.pcap -s0 && ./pcap_to_squid.py >> $PROJ_PATH/log/access.log && rm -f $PROJ_PATH/dump/dump.pcap && exit 0
