#!/bin/bash
set -e

# Install system dependencies
sudo yum update -y
sudo yum install -y docker java-11-openjdk-devel git python3 python3-pip firewalld

# Configure firewall
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-port=8080/tcp  # Bot API
sudo firewall-cmd --permanent --add-port=8081/tcp  # Java Dashboard
sudo firewall-cmd --reload

# Setup Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Clone repository
git clone https://github.com/topreach/meme-sniper-bot.git
cd meme-sniper-bot

# Create .env file
cp .env.example .env
nano .env  # Edit with your actual values

# Build and run bot container
docker build -t sniper-bot .
docker run -d --name sniper-bot --env-file .env sniper-bot

# Build Java dashboard
cd dashboard-java
./mvnw clean package
java -jar target/dashboard-0.0.1-SNAPSHOT.jar &

# Add to deployment script
echo "Configuring for L2: $L2_NETWORK"

# L2-specific dependencies
if [ "$L2_NETWORK" = "arbitrum" ]; then
    sudo yum install -y arbitrum-toolkit
elif [ "$L2_NETWORK" = "polygon" ]; then
    sudo yum install -y polygon-edge
fi

# Update .env with L2 settings
echo "IS_L2=True" >> .env
echo "L2_NETWORK=$L2_NETWORK" >> .env
echo "RPC_URL=$(curl -s https://l2-rpcs.example.com/$L2_NETWORK)" >> .env
