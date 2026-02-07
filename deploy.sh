#!/bin/bash
# Stratify AI Deployment Script
# Run this on your AWS EC2 instance after cloning the repository

set -e  # Exit on error

echo "========================================="
echo "Stratify AI - AWS Deployment Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${GREEN}Step 2: Installing dependencies...${NC}"
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx

echo -e "${GREEN}Step 3: Setting up PostgreSQL...${NC}"
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
echo -e "${YELLOW}Creating PostgreSQL database...${NC}"
sudo -u postgres psql -c "CREATE DATABASE stratify_db;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER stratify WITH PASSWORD 'change_this_password';" || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stratify_db TO stratify;"

echo -e "${GREEN}Step 4: Setting up Python backend...${NC}"
cd ~/stratify-ai/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}Step 5: Configuring environment variables...${NC}"
if [ ! -f .env ]; then
    cp ../.env.example .env
    echo -e "${YELLOW}Please edit .env file with your API keys${NC}"
    echo -e "${YELLOW}Run: nano ~/stratify-ai/backend/.env${NC}"
else
    echo ".env file already exists"
fi

echo -e "${GREEN}Step 6: Creating log directories...${NC}"
sudo mkdir -p /var/log/stratify
sudo chown $USER:$USER /var/log/stratify

echo -e "${GREEN}Step 7: Installing systemd service...${NC}"
sudo cp stratify.service /etc/systemd/system/
sudo systemctl daemon-reload

echo -e "${GREEN}Step 8: Configuring Nginx...${NC}"
sudo cp nginx.conf /etc/nginx/sites-available/stratify
sudo ln -sf /etc/nginx/sites-available/stratify /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

echo -e "${GREEN}Step 9: Starting services...${NC}"
sudo systemctl enable stratify
sudo systemctl start stratify
sudo systemctl enable nginx
sudo systemctl restart nginx

echo -e "${GREEN}Step 10: Installing SSL certificate (Let's Encrypt)...${NC}"
echo -e "${YELLOW}Make sure your domain points to this server first!${NC}"
read -p "Enter your domain name (or press Enter to skip): " DOMAIN

if [ ! -z "$DOMAIN" ]; then
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d $DOMAIN
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "Backend API: http://your-domain.com/api/"
echo -e "API Docs: http://your-domain.com/docs"
echo -e "Health Check: http://your-domain.com/health"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Edit .env file: nano ~/stratify-ai/backend/.env"
echo -e "2. Add your API keys (FRED, NewsAPI) and ensure Ollama is running"
echo -e "3. Update database URL if needed"
echo -e "4. Restart service: sudo systemctl restart stratify"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "Check status: sudo systemctl status stratify"
echo -e "View logs: sudo journalctl -u stratify -f"
echo -e "Restart: sudo systemctl restart stratify"
echo ""
