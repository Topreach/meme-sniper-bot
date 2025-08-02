#!/bin/bash
set -e

# Create system user
sudo useradd -r -s /sbin/nologin -d /opt/meme-sniper-bot sniperbot

# Install dependencies
sudo yum update -y
sudo yum install -y docker java-11-openjdk-devel git python3 python3-pip firewalld postgresql-server

# Configure firewall
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-port=8080-8081/tcp
sudo firewall-cmd --reload

# Setup directories
sudo mkdir -p /opt/meme-sniper-bot/{bot,dashboard,scripts,data/{logs,db}}
sudo chown -R sniperbot:sniperbot /opt/meme-sniper-bot
sudo chmod 750 /opt/meme-sniper-bot

# Clone repo (as sniperbot user)
sudo -u sniperbot git clone https://github.com/topreach/meme-sniper-bot.git /opt/meme-sniper-bot/bot

# Move dashboard
sudo mv /opt/meme-sniper-bot/bot/dashboard-java /opt/meme-sniper-bot/dashboard

# Setup environment
sudo -u sniperbot cp /opt/meme-sniper-bot/bot/.env.example /opt/meme-sniper-bot/data/.env
sudo -u sniperbot nano /opt/meme-sniper-bot/data/.env  # Edit config

# Link configs
sudo -u sniperbot ln -s /opt/meme-sniper-bot/data/.env /opt/meme-sniper-bot/bot/.env
sudo -u sniperbot ln -s /opt/meme-sniper-bot/data/logs /opt/meme-sniper-bot/bot/logs

# Initialize PostgreSQL
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create DB user
sudo -u postgres psql -c "CREATE USER botuser WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE sniperbot OWNER botuser;"

# Install Python dependencies
sudo -u sniperbot python3 -m pip install -r /opt/meme-sniper-bot/bot/requirements.txt --user

# Build Java dashboard
cd /opt/meme-sniper-bot/dashboard
sudo -u sniperbot ./mvnw clean package

# Create systemd services
sudo tee /etc/systemd/system/sniper-bot.service <<EOL
[Unit]
Description=Meme Sniper Bot
After=network.target postgresql.service

[Service]
User=sniperbot
WorkingDirectory=/opt/meme-sniper-bot/bot
ExecStart=/usr/bin/python3 /opt/meme-sniper-bot/bot/scripts/run_sniper.py
EnvironmentFile=/opt/meme-sniper-bot/data/.env
Restart=always
RestartSec=10

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/meme-sniper-bot/data

[Install]
WantedBy=multi-user.target
EOL

sudo tee /etc/systemd/system/sniper-dashboard.service <<EOL
[Unit]
Description=Sniper Bot Dashboard
After=network.target postgresql.service

[Service]
User=sniperbot
WorkingDirectory=/opt/meme-sniper-bot/dashboard
ExecStart=/usr/bin/java -jar target/dashboard-0.0.1-SNAPSHOT.jar
EnvironmentFile=/opt/meme-sniper-bot/data/.env
Restart=always
RestartSec=10

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=full
ProtectHome=yes
ReadWritePaths=/opt/meme-sniper-bot/data

[Install]
WantedBy=multi-user.target
EOL

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable sniper-bot sniper-dashboard
sudo systemctl start sniper-bot sniper-dashboard

# Verify installation
echo "Deployment complete!"
echo "Check status with:"
echo "sudo systemctl status sniper-bot"
echo "sudo journalctl -u sniper-bot -f"
