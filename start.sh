#!/bin/bash

python backend/init_db.py

uvicorn backend.app.main:app --host 0.0.0.0 --port 10000
