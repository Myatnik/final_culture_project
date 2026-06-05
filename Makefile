.PHONY: help setup run clean rm_db

help:
	@echo "Available commands:"
	@echo " make setup - Setup requiremets "
	@echo " make run - Run application "
	@echo " make clean - Clean temporary files "
	@echo " make rm_db - Remove database "
setup:
	pip3 install -r requirements-dev.txt
run:
	python3 main.py
clean:
	rm -rf __pycache__ *.pyc .pytest_cache
rm_db:
	rm -f hotel.db

