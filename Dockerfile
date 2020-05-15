FROM python:3
WORKDIR /app
COPY fs/app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY fs /

CMD ["-x","/app/searchfor.sh","banana","results","historic"]
ENTRYPOINT ["bash"]
