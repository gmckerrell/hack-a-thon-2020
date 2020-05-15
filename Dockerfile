FROM python:3
ENV HTTPS_PROXY=http://webgateway.itm.mcafee.com:9090

WORKDIR /app
COPY fs/app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY fs /

CMD ["-x","/app/searchfor.sh","banana","results","historic"]
ENTRYPOINT ["bash"]
