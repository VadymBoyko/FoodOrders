FROM python:3.13

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app

COPY . /app

RUN pip install poetry==3.13

RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
