#! /bin/bash

status=0

echo "black:"
if ! black memecry --check; then
  status=1
fi
echo -e "---------\n"

echo "isort:"
if ! isort memecry --check-only --profile black; then
  status=1
fi
echo -e "---------\n"

echo "ruff:"
if ! ruff memecry; then
  status=1
fi
echo -e "---------\n"

echo "mypy:"
if ! mypy memecry; then
  status=1
fi

exit $status
