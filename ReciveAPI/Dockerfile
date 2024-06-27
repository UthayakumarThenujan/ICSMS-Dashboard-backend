FROM python:3.10-slim

WORKDIR code

EXPOSE 8005

COPY ./requirements.txt /code/requirements.txt

RUN pip --timeout=1000 install --no-cache-dir --upgrade -r /code/requirements.txt

#Run pip uninstall bson && pip install pymongo

#RUN  pip install pymongo

COPY . /code/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
