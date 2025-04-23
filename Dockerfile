FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y wkhtmltopdf gsfonts && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY Pipfile .
COPY Pipfile.lock .

RUN pip install pipenv

RUN pipenv install

COPY . .

CMD ["pipenv", "run", "python", "manage.py", "runserver"]