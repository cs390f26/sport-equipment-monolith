#!/bin/bash
# EC2 user-data script. Cloud-init runs it once as root on first boot.
# Output is saved to /var/log/cloud-init-output.log.
#
# Paste this file into the User data field when you launch the instance.

set -euo pipefail

REPO_URL="https://github.com/cs390f26/sport-equipment-monolith.git"
APP_DIR=/home/ec2-user/sport-equipment-monolith

yum install -y python3.12 git

git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

python3.12 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
cp config/example.env .env

# This script runs as root, but the app runs as ec2-user.
chown -R ec2-user:ec2-user "$APP_DIR"

# .env must contain the Aurora endpoint before this runs.
# Edit config/example.env (AURORA_HOST and the password) and push first.
.venv/bin/python scripts/wait_for_aurorasql.py
.venv/bin/python scripts/create_table.py

cp deploy/equipment.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now equipment.service
