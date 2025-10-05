FROM python:3.12-alpine

ARG ENVIRONMENT

ENV ENVIRONMENT=$ENVIRONMENT \
    PROJECT_DIR="/code" \
    PORT=8000 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR $PROJECT_DIR

RUN --mount=type=cache,target=/root/.apk apk update && apk add --no-cache \
    build-base \
    postgresql-dev \
    postgresql-client \
    musl-dev \
    linux-headers


COPY requirements.txt $PROJECT_DIR/

RUN --mount=type=cache,target=/root/.pip pip install -r $PROJECT_DIR/requirements.txt

COPY . $PROJECT_DIR/

RUN chmod +x ${PROJECT_DIR}/scripts/start_api.sh \
  && mkdir -p /${PROJECT_DIR}/media /${PROJECT_DIR}/static \
  && chmod +x /${PROJECT_DIR}/media/ /${PROJECT_DIR}/static/


EXPOSE $PORT

CMD ["./scripts/start_api.sh"]
