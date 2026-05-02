#!/bin/bash

# Railway Deployment Script for ITMS Backend

echo "=========================================="
echo "ITMS Backend - Railway Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}✗ Railway CLI not found${NC}"
    echo ""
    echo "Install Railway CLI:"
    echo "  npm install -g @railway/cli"
    echo ""
    echo "Or deploy via Railway Dashboard:"
    echo "  https://railway.app/dashboard"
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI found${NC}"
echo ""

# Check if logged in
echo "Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠ Not logged in to Railway${NC}"
    echo ""
    echo "Logging in to Railway..."
    railway login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Login failed${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Authenticated with Railway${NC}"
echo ""

# Check if project is linked
echo "Checking Railway project..."
if ! railway status &> /dev/null; then
    echo -e "${YELLOW}⚠ No Railway project linked${NC}"
    echo ""
    echo "Options:"
    echo "  1. Link to existing project: railway link"
    echo "  2. Create new project: railway init"
    echo ""
    read -p "Create new project? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        railway init
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ Project creation failed${NC}"
            exit 1
        fi
    else
        echo "Please link to a project first: railway link"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Railway project linked${NC}"
echo ""

# Check for PostgreSQL
echo "Checking for PostgreSQL database..."
if ! railway variables | grep -q "DATABASE_URL"; then
    echo -e "${YELLOW}⚠ No PostgreSQL database found${NC}"
    echo ""
    read -p "Add PostgreSQL database? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        railway add --database postgresql
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ Failed to add PostgreSQL${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✓ PostgreSQL database added${NC}"
    else
        echo -e "${RED}✗ PostgreSQL is required${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ PostgreSQL database found${NC}"
fi

echo ""

# Check environment variables
echo "Checking environment variables..."
REQUIRED_VARS=("SECRET_KEY" "DATABASE_URL")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if ! railway variables | grep -q "$var"; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Missing environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please set these variables in Railway dashboard:"
    echo "  https://railway.app/dashboard"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Required environment variables found${NC}"
fi

echo ""

# Deploy
echo "=========================================="
echo "Deploying to Railway..."
echo "=========================================="
echo ""

railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✅ Deployment Successful!${NC}"
    echo "=========================================="
    echo ""
    
    # Get deployment URL
    echo "Getting deployment URL..."
    RAILWAY_URL=$(railway domain)
    
    if [ -n "$RAILWAY_URL" ]; then
        echo ""
        echo -e "${BLUE}Your backend is deployed at:${NC}"
        echo -e "${GREEN}https://$RAILWAY_URL${NC}"
        echo ""
        echo "Test your deployment:"
        echo "  curl https://$RAILWAY_URL/health"
        echo ""
        echo "View logs:"
        echo "  railway logs"
        echo ""
        echo "Open dashboard:"
        echo "  railway open"
    fi
    
    echo ""
    echo "Next steps:"
    echo "  1. Run migrations: railway run alembic upgrade head"
    echo "  2. Create admin user (see RAILWAY_DEPLOYMENT_GUIDE.md)"
    echo "  3. Test endpoints"
    echo "  4. Configure custom domain (optional)"
    echo ""
else
    echo ""
    echo "=========================================="
    echo -e "${RED}✗ Deployment Failed${NC}"
    echo "=========================================="
    echo ""
    echo "Check the logs above for errors"
    echo ""
    echo "Common issues:"
    echo "  - Missing environment variables"
    echo "  - Database connection error"
    echo "  - Build errors"
    echo ""
    echo "View logs: railway logs"
    echo "Get help: https://docs.railway.app"
    exit 1
fi
