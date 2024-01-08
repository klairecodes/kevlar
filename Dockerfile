FROM python:3.11.7-alpine3.19

WORKDIR /app
COPY . /app

EXPOSE 3000

ARG slack_app_token
ARG slack_bot_token
ENV SLACK_APP_TOKEN=$slack_app_token
ENV SLACK_BOT_TOKEN=$slack_bot_token

RUN ["pip", "install", "-r", "requirements.txt"]
CMD ["python3", "app.py"]
