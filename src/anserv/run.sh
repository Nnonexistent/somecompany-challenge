#!/bin/bash
alembic upgrade head
exec uvicorn app:app --host 0.0.0.0
