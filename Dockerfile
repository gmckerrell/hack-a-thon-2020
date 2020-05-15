#FROM python:2
FROM ubuntu-latest
WORKDIR /app
COPY fs/app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apt install -y whois

COPY fs /

ENTRYPOINT ["bash"]
