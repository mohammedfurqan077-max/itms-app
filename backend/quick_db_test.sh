#!/bin/bash

# Quick Database Test Script
# Tests if database is working with STRING fields (not ENUM)

echo "=========================================="
echo "QUICK DATABASE TEST"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database connection
DB_NAME="itms_db"
DB_USER="postgres"

echo "1. Checking if commands table exists..."
TABLE_EXISTS=$(psql -U $DB_USER -d $DB_NAME -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commands');")

if [ "$TABLE_EXISTS" = "t" ]; then
    echo -e "${GREEN}✓ Commands table exists${NC}"
else
    echo -e "${RED}✗ Commands table does not exist${NC}"
    echo "Run: python -m alembic upgrade head"
    exit 1
fi

echo ""
echo "2. Checking if ENUM types exist (should be 0)..."
ENUM_COUNT=$(psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM pg_type WHERE typname IN ('commandstatus', 'commandtype');")

if [ "$ENUM_COUNT" = "0" ]; then
    echo -e "${GREEN}✓ No ENUM types found (correct)${NC}"
else
    echo -e "${RED}✗ Found $ENUM_COUNT ENUM type(s) (should be 0)${NC}"
    echo "Run: psql -U $DB_USER -d $DB_NAME -f cleanup_enum_types.sql"
    exit 1
fi

echo ""
echo "3. Checking command_type field type..."
CMD_TYPE=$(psql -U $DB_USER -d $DB_NAME -tAc "SELECT data_type FROM information_schema.columns WHERE table_name = 'commands' AND column_name = 'command_type';")

if [ "$CMD_TYPE" = "character varying" ]; then
    echo -e "${GREEN}✓ command_type is VARCHAR (correct)${NC}"
else
    echo -e "${RED}✗ command_type is $CMD_TYPE (should be VARCHAR)${NC}"
    exit 1
fi

echo ""
echo "4. Checking status field type..."
STATUS_TYPE=$(psql -U $DB_USER -d $DB_NAME -tAc "SELECT data_type FROM information_schema.columns WHERE table_name = 'commands' AND column_name = 'status';")

if [ "$STATUS_TYPE" = "character varying" ]; then
    echo -e "${GREEN}✓ status is VARCHAR (correct)${NC}"
else
    echo -e "${RED}✗ status is $STATUS_TYPE (should be VARCHAR)${NC}"
    exit 1
fi

echo ""
echo "5. Checking table structure..."
echo ""
psql -U $DB_USER -d $DB_NAME -c "\d commands"

echo ""
echo "6. Checking existing commands..."
CMD_COUNT=$(psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM commands;")
echo "Total commands in database: $CMD_COUNT"

if [ "$CMD_COUNT" -gt "0" ]; then
    echo ""
    echo "Sample commands:"
    psql -U $DB_USER -d $DB_NAME -c "SELECT id, command_type, status, created_at FROM commands ORDER BY created_at DESC LIMIT 5;"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ DATABASE VALIDATION PASSED${NC}"
echo "=========================================="
echo ""
echo "Database is correctly configured with:"
echo "  • Commands table exists"
echo "  • No ENUM types (using STRING)"
echo "  • command_type: VARCHAR(50)"
echo "  • status: VARCHAR(50)"
echo ""
echo "Ready to run: python test_full_system_validation.py"
echo ""
