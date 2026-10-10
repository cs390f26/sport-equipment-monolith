#!/bin/bash

# EC2 user-data script for Amazon Linux 2023.
# Cloud-init runs this script as root during first boot.
# Output is logged to /var/log/cloud-init-output.log.

# Stop on errors, unset variables, or failed commands in a pipeline.
set -euo pipefail

REPO_URL="https://github.com/cs390f26/sport-equipment-monolith.git"
APP_DIR="/home/ec2-user/sport-equipment-monolith"

# Refresh package metadata and install Python, Git, and OpenSSL.
dnf install -y python3.12 git openssl

# Install the official MySQL 8.4 Community repository for EL9.
dnf install -y \
    https://dev.mysql.com/get/mysql84-community-release-el9-1.noarch.rpm

# Install the MySQL Community Server and its client dependencies.
dnf install -y mysql-community-server

git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

python3.12 -m venv .venv

.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .

cp config/example.env .env

# Give ec2-user ownership of the application and its virtual environment.
chown -R ec2-user:ec2-user "$APP_DIR"

# Start MySQL now and enable it to start automatically on reboot.
systemctl enable --now mysqld.service

# MySQL generates a temporary root password on a fresh installation.
TEMP_PASSWORD=""

for i in {1..30}; do
    TEMP_PASSWORD="$(
        sed -n \
            's/.*temporary password is generated for root@localhost: //p' \
            /var/log/mysqld.log | tail -n 1
    )"

    if [ -n "$TEMP_PASSWORD" ]; then
        break
    fi

    sleep 2
done

if [ -z "$TEMP_PASSWORD" ]; then
    echo "ERROR: MySQL temporary root password not found." >&2
    exit 1
fi

# Generate 48 hexadecimal characters.
MYSQL_PASSWORD="$(openssl rand -hex 32)"

# Restrict newly created files to the current user.
umask 077

# Create a temporary file for MySQL client credentials.
TEMP_CNF="$(mktemp)"

# Ensure the temporary credentials file is removed if the script exits.
trap 'rm -f "$TEMP_CNF"' EXIT

# Escape backslashes and double quotes for a MySQL option file.
ESCAPED_TEMP="${TEMP_PASSWORD//\\/\\\\}"
ESCAPED_TEMP="${ESCAPED_TEMP//\"/\\\"}"

# Write the temporary credentials to the file.
printf '[client]\nuser=root\npassword="%s"\n' \
    "$ESCAPED_TEMP" > "$TEMP_CNF"

# Change the MySQL root password using the temporary credentials.
mysql --defaults-extra-file="$TEMP_CNF" \
    --connect-expired-password \
    -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';"

# Save the new root credentials in a root-only MySQL client config.
printf '[client]\nuser=root\npassword="%s"\n' \
    "$MYSQL_PASSWORD" > /root/.my.cnf

# Restrict access to root because this file contains a database password.
chmod 600 /root/.my.cnf

# Delete the temporary credentials file and remove its exit trap.
rm -f "$TEMP_CNF"
trap - EXIT

# Update the MySQL username and password in the application's .env.
sed -i \
    -e 's/^MYSQL_USER=.*/MYSQL_USER=root/' \
    -e "/^MYSQL_PASSWORD=/c\\MYSQL_PASSWORD=$MYSQL_PASSWORD" \
    "$APP_DIR/.env"

# Restrict access to the application's environment file.
chmod 600 "$APP_DIR/.env"

# Copy the provided systemd service definition into the system directory.
cp "$APP_DIR/deploy/equipment.service" \
    /etc/systemd/system/equipment.service

# Tell systemd to reload its service definitions.
systemctl daemon-reload

.venv/bin/python scripts/wait_for_mysql.py
.venv/bin/python scripts/create_table.py
.venv/bin/python scripts/seed.py

# Enable the service on future boots and start it immediately.
systemctl enable --now equipment.service

# If execution reaches this point, provisioning completed successfully.
echo "User-data provisioning completed successfully."