FROM python:3.13

WORKDIR /app

COPY . /app

RUN pip install poetry==$NIXPACKS_POETRY_VERSION

RUN poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
