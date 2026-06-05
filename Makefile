.PHONY: help install run clean rm_db venv

help:
	@echo "Available commands:"
	@echo " make install - install requiremets "
	@echo " make run - Run application "
	@echo " make clean - Clean temporary files "
	@echo " make rm_db - Remove database "
venv:
	python3 -m venv $(VENV)
install: venv
	$(VENV)/bin/pip install -r requirements-dev.txt
run:
	$(VENV)/bin/python3 main.py
clean:
	rm -rf __pycache__ *.pyc .pytest_cache
rm_db:
	rm -f hotel.db

