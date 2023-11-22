#! /bin/bash

status=0

echo "ruff format:"
if ! ruff format --check memecry; then
  status=1
fi
echo -e "---------\n"

echo "ruff lint:"
if ! ruff memecry; then
  status=1
fi
echo -e "---------\n"

echo "mypy:"
if ! mypy memecry; then
  status=1
fi

exit $status
