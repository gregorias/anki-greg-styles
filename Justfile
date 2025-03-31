test: mypy unittest

mypy:
  mypy --python-executable=.venv/bin/python3 gregstyles test

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
