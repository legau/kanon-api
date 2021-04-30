FROM python:3.9.4

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

RUN poetry install --no-dev --no-root -E uvicorn

COPY . ./
ENV HOST 0.0.0.0

ENTRYPOINT ["./docker/entrypoint.sh"]
