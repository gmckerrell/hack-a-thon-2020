FROM python:2
WORKDIR /app
COPY fs/app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apt install -y whois

COPY fs /

ENTRYPOINT ["/app/get_dns.sh"]
