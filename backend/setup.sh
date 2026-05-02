#!/bin/bash

# ITMS Backend Setup Script
# This script helps set up the development environment

set -e

echo "🚀 ITMS Backend Setup"
echo "====================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate a random secret key
    secret_key=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env with generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-in-production/$secret_key/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-change-in-production/$secret_key/" .env
    fi
    
    echo "✅ .env file created with generated SECRET_KEY"
    echo "⚠️  Please update DATABASE_URL and other settings in .env"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Check PostgreSQL
echo "🐘 Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client found"
    echo "ℹ️  Make sure PostgreSQL server is running"
    echo "ℹ️  Create database: createdb itms_db"
else
    echo "⚠️  PostgreSQL client not found"
    echo "ℹ️  Install PostgreSQL: https://www.postgresql.org/download/"
fi
echo ""

# Initialize Alembic (if not already initialized)
if [ ! -d "alembic/versions" ]; then
    echo "🗄️  Initializing Alembic..."
    mkdir -p alembic/versions
    echo "✅ Alembic initialized"
else
    echo "ℹ️  Alembic already initialized"
fi
echo ""

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your database credentials"
echo "2. Create PostgreSQL database: createdb itms_db"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start development server: uvicorn app.main:app --reload"
echo ""
echo "📚 Documentation:"
echo "- README.md: General information"
echo "- ARCHITECTURE.md: Architecture details"
echo "- API docs: http://localhost:8000/api/docs (after starting server)"
echo ""
echo "🎉 Happy coding!"
