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
RUN poetry install --no-interaction --no-ansi -vvv --only main

FROM python as runtime
RUN apt-get update && \
    apt-get install -y \
    --no-install-recommends \
    python3-opencv libleptonica-dev tesseract-ocr libtesseract-dev \
    python3-pil tesseract-ocr-eng tesseract-ocr-script-latn && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=poetry /app /app
CMD ["python", "-u", "memecry/main.py"]
