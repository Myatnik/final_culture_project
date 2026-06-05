.PHONY: help install run test clean rm_db

help:
	@echo "Available commands:"
	@echo " make install - Install requiremets "
	@echo " make run - Run application "
	@echo " make test - Run tests "
	@echo " make clean - Clean temporary files "
	@echo " make rm_db - Remove database "
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

