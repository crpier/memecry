echo "black:"
black src
echo "---------"

echo "\nisort:"
isort src --check-only --profile black
echo "---------"

echo "\nruff:"
ruff src
echo "---------"

echo "\nmypy:"
mypy src
echo "---------"
