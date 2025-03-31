test: mypy unittest

mypy:
  mypy gregstyles test

ruff:
  ruff check gregstyles test

ruff-fix:
  ruff check --fix gregstyles test

unittest:
  python3 -m unittest discover -s test/ -t .

coverage:
  coverage run --source='gregstyles/' --branch -m unittest discover -s test/ -t . &&
  coverage html

vulture:
  vulture gregstyles/
