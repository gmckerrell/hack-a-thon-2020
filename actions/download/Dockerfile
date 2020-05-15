FROM python:2
WORKDIR /app
COPY ../../fs /
RUN apt update
RUN apt install -y whois
RUN pip install --no-cache-dir -r /app/requirements.txt


ENTRYPOINT ["/app/get_dns.sh"]
