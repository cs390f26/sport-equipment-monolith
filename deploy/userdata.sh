#!/bin/bash
# EC2 user-data script. Cloud-init runs it once as root on first boot.
# Output is saved to /var/log/cloud-init-output.log.
#
# Paste this file into the User data field when you launch the instance.

set -euo pipefail

REPO_URL="https://github.com/cs390f26/sport-equipment-monolith.git"
APP_DIR=/home/ec2-user/sport-equipment-monolith

yum install -y python3.12 git
# Amazon Linux does not ship Oracle MySQL. This is MySQL 8.4 from MySQL's repo.
yum install -y https://dev.mysql.com/get/mysql84-community-release-el9-1.noarch.rpm
yum install -y mysql-community-server

git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

python3.12 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txst
.venv/bin/pip install -e .
cp config/example.env .env

# This script runs as root, but the app runs as ec2-user.
chown -R ec2-user:ec2-user "$APP_DIR"

cp deploy/mysql-local.service /etc/systemd/system/
cp deploy/equipment.service /etc/systemd/system/
systemctl daemon-reload
# The MySQL package ships mysqld.service. This deploy starts mysql-local.service.
systemctl disable mysqld.service
systemctl enable --now mysql-local.service

# First boot generates a temporary root password. Set it to MYSQL_PASSWORD
# and allow TCP connections to 127.0.0.1, which is what the app uses.
MYSQL_PASSWORD="$(awk -F= '/^MYSQL_PASSWORD=/ {print substr($0, index($0, "=")+1)}' .env)"
TEMP_PASSWORD="$(awk '/temporary password/ {print $NF}' /var/log/mysqld.log | tail -n 1)"
mysql --connect-expired-password -uroot -p"${TEMP_PASSWORD}" --execute "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';"
mysql -uroot -p"${MYSQL_PASSWORD}" --execute "CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASSWORD}'; ALTER USER 'root'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASSWORD}'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION; FLUSH PRIVILEGES;"

.venv/bin/python scripts/wait_for_mysql.py
.venv/bin/python scripts/create_table.py
.venv/bin/python scripts/seed.py

systemctl enable --now equipment.service

