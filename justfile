serve:
  dotenv run python memecry/main.py

fix-formatting:
  ruff format .

fix-linting:
  ruff check --fix --unsafe-fixes .

fix: fix-formatting fix-linting

check-linting:
  ruff check .
