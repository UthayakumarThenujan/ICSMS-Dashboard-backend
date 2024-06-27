FROM python:3.10-slim

WORKDIR code

EXPOSE 8002

COPY ./requirements.txt /code/requirements.txt

RUN pip --timeout=1000 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
