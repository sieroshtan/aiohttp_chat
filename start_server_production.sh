#!/usr/bin/env bash

source /home/ubuntu/projects/chichat/backend/venv/bin/activate
cd /home/ubuntu/projects/chichat/backend/app; gunicorn -b 0.0.0.0:8886 -k aiohttp.worker.GunicornWebWorker -w 1 -t 60 chat.server_g:app --reload

