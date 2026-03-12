#!/bin/bash
# Superset initialization script to be run inside the superset container (example)
set -e
superset fab create-admin --username admin --firstname Admin --lastname User --email admin@example.com --password admin
superset db upgrade
superset init
