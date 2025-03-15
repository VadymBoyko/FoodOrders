FROM python:3.13

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app

COPY . /app

RUN pip install poetry==2.1.1

RUN poetry install --no-interaction --no-ansi --no-root

RUN poetry run pip install uvicorn

RUN poetry run uvicorn --version

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
