COVERAGE_CMD ?= .venv/bin/pytest tests/ --cov=. --cov-report=html

.PHONY: help install run test clean rm_db coverage setup check

help:
	@echo "Available commands:"
	@echo " make install - Install requirements "
	@echo " make run - Run application "
	@echo " make test - Run tests "
	@echo " make clean - Clean temporary files "
	@echo " make rm_db - Remove database "
	@echo " make coverage - Find test coverage "
	@echo " make setup - Prepare project for running "
	@echo " make check - Check everything in project "
install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
run:
	.venv/bin/python3 main.py
test:
	.venv/bin/pytest tests/ -v
clean:
	rm -rf __pycache__ *.pyc .pytest_cache
rm_db:
	rm -f hotel.db
coverage:
	$(COVERAGE_CMD)
setup: install
check: test coverage
