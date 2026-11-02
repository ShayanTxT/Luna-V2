# shayan.txt
.PHONY: install run dev test backup clean

install:
	pip install -r requirements.txt

run:
	python bot.py

dev:
	LOG_LEVEL=DEBUG python bot.py

test:
	pytest -q

backup:
	python -c "import asyncio; from core.database import db_manager; asyncio.run(db_manager.backup())"

docker-build:
	docker build -t luna-bot .

docker-run:
	docker-compose up -d

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
