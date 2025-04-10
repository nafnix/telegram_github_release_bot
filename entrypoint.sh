#!/bin/sh
set -ex

python set_webhook.py
gunicorn --print-config src.main:app

exec "$@"
