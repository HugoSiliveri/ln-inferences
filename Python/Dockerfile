FROM python:3.9-slim

RUN pip install redis requests

COPY ./Python/app /app

# Copie le code dans le conteneur
WORKDIR /app

CMD ["tail", "-f", "/dev/null"]