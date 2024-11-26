FROM python:3.10-slim-bullseye
ARG VERSION
RUN pip install --no-cache mlflow==$VERSION
RUN pip install --no-cache boto3 psycopg2-binary