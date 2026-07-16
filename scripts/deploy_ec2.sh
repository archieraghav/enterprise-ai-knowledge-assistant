#!/bin/bash
set -e

echo "=== Enterprise AI Knowledge Assistant — EC2 Deployment Script ==="

echo "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker "$USER"
    rm get-docker.sh
else
    echo "Docker already installed, skipping."
fi

echo "Installing Docker Compose plugin..."
sudo apt-get install -y docker-compose-plugin

echo "Installing Git..."
sudo apt-get install -y git

echo "Cloning repository (if not already present)..."
if [ ! -d "enterprise-ai-knowledge-assistant" ]; then
    git clone https://github.com/archieraghav/enterprise-ai-knowledge-assistant.git
fi
cd enterprise-ai-knowledge-assistant

echo ""
echo "=== IMPORTANT: create .env.production before continuing ==="
echo "Copy .env.production.example to .env.production and fill in real values:"
echo "  cp .env.production.example .env.production"
echo "  nano .env.production"
echo ""
read -p "Press Enter once .env.production is ready to continue..."

echo "Building and starting containers..."
sudo docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "=== Deployment complete ==="
echo "Check status with: sudo docker compose -f docker-compose.prod.yml ps"
echo "View logs with: sudo docker compose -f docker-compose.prod.yml logs -f backend"