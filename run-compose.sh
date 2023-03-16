#!/bin/bash

export COMPOSE_PROJECT_NAME=anserv

docker-compose build
docker-compose up
