# Makefile

.PHONY: help build up down restart logs shell web worker beat alembic-init alembic-make alembic-upgrade alembic-downgrade clean

# Variables
PROJECT_NAME := k_one
DOCKER_COMPOSE := docker-compose
PYTHON := docker-compose exec web python
ALEMBIC := docker-compose exec web alembic

help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'

build:
	$(DOCKER_COMPOSE) up --build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(MAKE) down
	$(MAKE) up

logs:
	$(DOCKER_COMPOSE) logs -f

shell:
	$(DOCKER_COMPOSE) exec web bash

web:
	$(DOCKER_COMPOSE) up web

worker:
	$(DOCKER_COMPOSE) up worker

beat:
	$(DOCKER_COMPOSE) up celery-beat

celery-restart:
	$(DOCKER_COMPOSE) restart worker celery-beat

# Alembic
alembic-init:
	$(ALEMBIC) init app/db/alembic

alembic-make: ## new migration
	$(ALEMBIC) revision --autogenerate -m "$(name)"

alembic-upgrade:
	$(ALEMBIC) upgrade head

alembic-downgrade:
	$(ALEMBIC) downgrade -1

clean:
	docker volume rm $$(docker volume ls -q | grep $(PROJECT_NAME)) || true
	$(MAKE) down
