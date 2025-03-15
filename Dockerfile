FROM python:3.13

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app

COPY . /app

RUN pip install poetry==$NIXPACKS_POETRY_VERSION || curl -sSL https://install.python-poetry.org | python3 -


RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
