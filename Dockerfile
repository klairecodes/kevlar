FROM python:3.11.7-alpine3.19

WORKDIR /app
COPY . /app

EXPOSE 3000

RUN ["pip", "install", "-r", "requirements.txt"]
CMD ["python3", "app.py"]
