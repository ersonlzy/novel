#!/bin/bash

# Novel Copilot - macOS/Linux One-Click Deployment Script
# =======================================================

echo ""
echo "========================================"
echo "  Novel Copilot - Docker Deployment"
echo "========================================"
echo ""

# 1. Update from GitHub
echo "[1/7] Checking for updates..."
if command -v git &> /dev/null; then
    if [ -d ".git" ]; then
        echo "Pulling latest changes from GitHub..."
        git pull
        echo "[√] Code updated"
    else
        echo "[!] Not a git repository, skipping update."
    fi
else
    echo "[!] Git not found, skipping update."
fi

# 2. Check Docker environment
echo ""
echo "[2/7] Checking Docker environment..."
if ! command -v docker &> /dev/null; then
    echo "[Error] Docker not found. Please install Docker Desktop."
    echo "Download: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "[√] Docker is installed"

# Check Docker Compose (docker compose or docker-compose)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "[Error] Docker Compose not found. Please ensure Docker Desktop is running."
    exit 1
fi
echo "[√] Docker Compose is ready"

# 3. Create necessary data directories
echo ""
echo "[3/7] Creating data directories..."
mkdir -p data/db
mkdir -p data/vectordb
mkdir -p data/files
echo "[√] Data directories created"

# 4. Check .env configuration
echo ""
echo "[4/7] Checking environment configuration..."
if [ -d ".env" ]; then
    echo "[!] Detected .env is a directory (possibly a Docker error)"
    echo "[!] Removing folder and recreating from .env.example..."
    rm -rf ".env"
    cp ".env.example" ".env"
fi

if [ ! -f ".env" ]; then
    echo "[!] .env file not found, copying from .env.example..."
    cp ".env.example" ".env"
    echo "[!] Please edit .env file to configure your API Keys."
    echo ""
    read -p "Continue deployment? (y/n): " CONTINUE
    if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
else
    echo "[√] .env file exists"
fi

# 5. Clean up old containers
echo ""
echo "[5/7] Cleaning up old containers and images..."
$DOCKER_COMPOSE_CMD down --rmi local > /dev/null 2>&1
echo "[√] Cleanup complete"

# 6. Build and start services
echo ""
echo "[6/7] Building Docker image..."
$DOCKER_COMPOSE_CMD build
if [ $? -ne 0 ]; then
    echo "[Error] Docker image build failed"
    exit 1
fi
echo "[√] Docker image build complete"

echo ""
echo "[7/7] Starting services..."
$DOCKER_COMPOSE_CMD up -d
if [ $? -ne 0 ]; then
    echo "[Error] Failed to start services"
    exit 1
fi

# Wait for service to start
echo ""
echo "Waiting for service to start..."
sleep 5

# Check service status and finish
echo ""
echo "========================================"
echo "  Deployment Complete!"
echo "========================================"
echo ""
$DOCKER_COMPOSE_CMD ps
echo ""
echo "Access URL: http://localhost:8501"
echo ""
echo "Common Commands:"
echo "  Logs:    $DOCKER_COMPOSE_CMD logs -f"
echo "  Stop:    $DOCKER_COMPOSE_CMD stop"
echo "  Start:   $DOCKER_COMPOSE_CMD start"
echo "  Restart: $DOCKER_COMPOSE_CMD restart"
echo "  Remove:  $DOCKER_COMPOSE_CMD down"
echo ""

# Open browser
if command -v open &> /dev/null; then
    echo "Opening browser..."
    open http://localhost:8501
elif command -v xdg-open &> /dev/null; then
    echo "Opening browser..."
    xdg-open http://localhost:8501
fi
