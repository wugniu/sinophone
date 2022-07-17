refresh: clean build install lint

build:
	python setup.py build

install:
	python setup.py install

build_dist:
	make clean
	python setup.py sdist bdist_wheel
	python -m pip install dist/*.whl
	make test

release:
	python -m twine upload dist/*

lint:
	isort . --check-only --diff --combine-as --profile black
	black . --check
	flake8 sinophone/ tests/ --exclude "examples/*.py" --max-line-length 88 --extend-ignore E203 --statistics
	mypy --package sinophone --ignore-missing-imports
	mypy --package tests --ignore-missing-imports

test:
	python -m unittest

clean:
	python -m pip uninstall -y sinophone
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf **/__pycache__
