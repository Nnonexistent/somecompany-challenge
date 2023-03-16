#!/bin/bash

export COMPOSE_FILE=docker-compose.yml:docker-compose.tests.yml
export COMPOSE_PROJECT_NAME=anserv_tests

docker-compose down
docker volume rm anserv_tests_db_data || false

docker-compose build
docker-compose up backend
