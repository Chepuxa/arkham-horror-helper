FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10

COPY pip.txt ./
RUN pip install -r pip.txt

COPY . .

CMD uvicorn entrypoint:app --host 0.0.0.0 --port 80