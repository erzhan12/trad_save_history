.PHONY: help install test check-db check-tables check-stats check-recent check-symbol clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install        - Install project dependencies"
	@echo "  make test           - Run pytest tests"
	@echo "  make check-db       - Show recent ticker data (default 10 records)"
	@echo "  make check-tables   - List all database tables"
	@echo "  make check-stats    - Show ticker statistics"
	@echo "  make check-recent   - Show recent ticker data (20 records)"
	@echo "  make check-symbol   - Show recent data for BTCUSDT (20 records)"
	@echo "  make clean          - Remove Python cache files and database"

# Install dependencies
install:
	pip install -e .

# Run tests
test:
	pytest

# Run the application
run:
	python main.py

lint:
	ruff check .

# Database check commands
check-db:
	python check_db_runner.py --recent 10

check-tables:
	python check_db_runner.py --tables

check-stats:
	python check_db_runner.py --stats

check-recent:
	python check_db_runner.py --recent 20

check-symbol:
	python check_db_runner.py --recent 20 --symbol BTCUSDT

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} + 