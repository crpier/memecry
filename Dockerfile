FROM python:3.11-slim as python
ENV PYTHONUNBUFFERED=true
WORKDIR /app


FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VERSION=1.4.2
ENV PATH="$POETRY_HOME/bin:$PATH"
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY . ./
RUN poetry install --no-interaction --no-ansi -vvv --only main --no-root

FROM python as runtime
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
COPY --from=poetry /app /app
CMD ["python", "-u", "memecry/main.py"]
