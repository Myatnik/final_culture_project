.PHONY: help run clean rm_db

help:
	@echo "Available commands:"
	@echo " make run - Run application "
	@echo " make clean - Clean temporary files "
	@echo " make rm_db - Remove database "
run:
	python3 main.py
clean:
	rm -rf __pycache__ *.pyc .pytest_cache
rm_db:
	rm -f hotel.db

