#FROM python:2
FROM ubuntu:latest
WORKDIR /app
COPY fs/app/requirements.txt requirements.txt
RUN apt install -y whois python python-pip
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY fs /

ENTRYPOINT ["bash"]
