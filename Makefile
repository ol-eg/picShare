.PHONY: up test testd up-build migrate migrate-auto

DC = docker compose
EXEC = $(DC) exec -e PICSHARE_TEST_DB_HOST=db-test \
	-e PICSHARE_SECRET_KEY=test-secret-key \
	-e PICSHARE_INVITE_CODE=test-invite-42 \
	-e PICSHARE_UPLOAD_DIR=/tmp/picshare-test/uploads \
	-e PICSHARE_THUMB_DIR=/tmp/picshare-test/thumbnails app

up:
	$(DC) up --build -d

up-build:
	$(DC) up --build

test: up
	$(DC) exec app mkdir -p /tmp/picshare-test/uploads /tmp/picshare-test/thumbnails
	$(EXEC) pytest -v --cov=app --cov-report=term --cov-report=html

test-ci: up
	$(DC) exec app mkdir -p /tmp/picshare-test/uploads /tmp/picshare-test/thumbnails
	$(EXEC) pytest -v --cov=app --cov-report=term

migrate:
	$(DC) exec app alembic upgrade head

migrate-auto:
	$(DC) exec app alembic revision --autogenerate -m "$(m)"
	$(DC) exec app alembic upgrade head