FROM python:3.9.4

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

RUN poetry install --no-dev --no-root
RUN pip install uvicorn


COPY . ./
ENV HOST 0.0.0.0
ENV PORT 8000
ENV PRODUCTION true

RUN python -m kanon_api.app

ENTRYPOINT ["./docker/entrypoint.sh"]
