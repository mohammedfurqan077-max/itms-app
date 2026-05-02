# Quick Database Test Script (PowerShell)
# Tests if database is working with STRING fields (not ENUM)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "QUICK DATABASE TEST" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Database connection
$DB_NAME = "itms_db"
$DB_USER = "postgres"

Write-Host "1. Checking if commands table exists..."
$tableExists = psql -U $DB_USER -d $DB_NAME -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commands');"

if ($tableExists -eq "t") {
    Write-Host "✓ Commands table exists" -ForegroundColor Green
} else {
    Write-Host "✗ Commands table does not exist" -ForegroundColor Red
    Write-Host "Run: python -m alembic upgrade head"
    exit 1
}

Write-Host ""
Write-Host "2. Checking if ENUM types exist (should be 0)..."
$enumCount = psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM pg_type WHERE typname IN ('commandstatus', 'commandtype');"

if ($enumCount -eq "0") {
    Write-Host "✓ No ENUM types found (correct)" -ForegroundColor Green
} else {
    Write-Host "✗ Found $enumCount ENUM type(s) (should be 0)" -ForegroundColor Red
    Write-Host "Run: psql -U $DB_USER -d $DB_NAME -f cleanup_enum_types.sql"
    exit 1
}

Write-Host ""
Write-Host "3. Checking command_type field type..."
$cmdType = psql -U $DB_USER -d $DB_NAME -tAc "SELECT data_type FROM information_schema.columns WHERE table_name = 'commands' AND column_name = 'command_type';"

if ($cmdType -eq "character varying") {
    Write-Host "✓ command_type is VARCHAR (correct)" -ForegroundColor Green
} else {
    Write-Host "✗ command_type is $cmdType (should be VARCHAR)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "4. Checking status field type..."
$statusType = psql -U $DB_USER -d $DB_NAME -tAc "SELECT data_type FROM information_schema.columns WHERE table_name = 'commands' AND column_name = 'status';"

if ($statusType -eq "character varying") {
    Write-Host "✓ status is VARCHAR (correct)" -ForegroundColor Green
} else {
    Write-Host "✗ status is $statusType (should be VARCHAR)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "5. Checking table structure..."
Write-Host ""
psql -U $DB_USER -d $DB_NAME -c "\d commands"

Write-Host ""
Write-Host "6. Checking existing commands..."
$cmdCount = psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM commands;"
Write-Host "Total commands in database: $cmdCount"

if ([int]$cmdCount -gt 0) {
    Write-Host ""
    Write-Host "Sample commands:"
    psql -U $DB_USER -d $DB_NAME -c "SELECT id, command_type, status, created_at FROM commands ORDER BY created_at DESC LIMIT 5;"
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ DATABASE VALIDATION PASSED" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database is correctly configured with:"
Write-Host "  • Commands table exists"
Write-Host "  • No ENUM types (using STRING)"
Write-Host "  • command_type: VARCHAR(50)"
Write-Host "  • status: VARCHAR(50)"
Write-Host ""
Write-Host "Ready to run: python test_full_system_validation.py"
Write-Host ""
