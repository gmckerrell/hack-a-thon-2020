FROM python:2
WORKDIR /app
RUN apt update
RUN apt install -y whois
COPY fs/app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY fs /

ENTRYPOINT ["/bin/bash","-c"]
