#! /bin/bash

echo "black:"
black src
echo -e "---------\n"

echo "isort:"
isort src --check-only --profile black
echo -e "---------\n"

echo "ruff:"
ruff src
echo -e "---------\n"

echo "mypy:"
mypy src
echo -e "---------\n"
