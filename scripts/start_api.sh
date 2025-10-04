#!/usr/bin/env bash

set -o errexit
set -o nounset

: "${ENVIRONMENT:?ENVIRONMENT is not set}"
: "${SERVER_PORT:?SERVER_PORT is not set}"
: "${PROJECT_DIR:?PROJECT_DIR is not set}"

python3 manage.py migrate

load_required_data() {
    python3 manage.py collectstatic --no-input
    python3 manage.py initadmin
}

echo "ENVIRONMENT is ${ENVIRONMENT}"
echo "Port ${SERVER_PORT} exposed for E-commerce API"

# Установить рабочую директорию
if [[ ! -d "${PROJECT_DIR}" ]]; then
    echo "Error: Project directory ${PROJECT_DIR} does not exist."
    exit 1
fi

cd "${PROJECT_DIR}"
echo "Changed to working directory $(pwd)"

mkdir -p media/images

cd media/images

ln -sfn "${PROJECT_DIR}/static/common/images/defaults/countries/flags" "${PROJECT_DIR}/media/images/flags"

cd "${PROJECT_DIR}"

load_required_data

if [[ "${ENVIRONMENT}" == 'development' ]]; then
    python3 manage.py runserver 0.0.0.0:"${SERVER_PORT}"
else
    daphne -p 8000 -b 0.0.0.0 src.config.asgi:application
fi
main
