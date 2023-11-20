FROM python:3.9.4-slim
WORKDIR /code
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . src/