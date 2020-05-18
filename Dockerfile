FROM python:2
WORKDIR /app
RUN apt-get update && apt-get install -y \
    whois \
  && rm -rf /var/lib/apt/lists¬

COPY fs/app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY fs /

CMD []
ENTRYPOINT ["/bin/bash","/entrypoint.sh"]
