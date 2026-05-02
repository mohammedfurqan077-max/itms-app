# Railway Deployment Script for ITMS Backend (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ITMS Backend - Railway Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
$railwayExists = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayExists) {
    Write-Host "✗ Railway CLI not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Railway CLI:"
    Write-Host "  npm install -g @railway/cli"
    Write-Host ""
    Write-Host "Or deploy via Railway Dashboard:"
    Write-Host "  https://railway.app/dashboard"
    exit 1
}

Write-Host "✓ Railway CLI found" -ForegroundColor Green
Write-Host ""

# Check if logged in
Write-Host "Checking Railway authentication..."
$whoami = railway whoami 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Not logged in to Railway" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Logging in to Railway..."
    railway login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Login failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ Authenticated with Railway" -ForegroundColor Green
Write-Host ""

# Check if project is linked
Write-Host "Checking Railway project..."
$status = railway status 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ No Railway project linked" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  1. Link to existing project: railway link"
    Write-Host "  2. Create new project: railway init"
    Write-Host ""
    $response = Read-Host "Create new project? (y/n)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        railway init
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Project creation failed" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Please link to a project first: railway link"
        exit 1
    }
}

Write-Host "✓ Railway project linked" -ForegroundColor Green
Write-Host ""

# Check for PostgreSQL
Write-Host "Checking for PostgreSQL database..."
$variables = railway variables 2>&1

if (-not ($variables -match "DATABASE_URL")) {
    Write-Host "⚠ No PostgreSQL database found" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Add PostgreSQL database? (y/n)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        railway add --database postgresql
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Failed to add PostgreSQL" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✓ PostgreSQL database added" -ForegroundColor Green
    } else {
        Write-Host "✗ PostgreSQL is required" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ PostgreSQL database found" -ForegroundColor Green
}

Write-Host ""

# Check environment variables
Write-Host "Checking environment variables..."
$requiredVars = @("SECRET_KEY", "DATABASE_URL")
$missingVars = @()

foreach ($var in $requiredVars) {
    if (-not ($variables -match $var)) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "⚠ Missing environment variables:" -ForegroundColor Yellow
    foreach ($var in $missingVars) {
        Write-Host "  - $var"
    }
    Write-Host ""
    Write-Host "Please set these variables in Railway dashboard:"
    Write-Host "  https://railway.app/dashboard"
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/n)"
    
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
} else {
    Write-Host "✓ Required environment variables found" -ForegroundColor Green
}

Write-Host ""

# Deploy
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deploying to Railway..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

railway up

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "✅ Deployment Successful!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Get deployment URL
    Write-Host "Getting deployment URL..."
    $railwayUrl = railway domain 2>&1
    
    if ($railwayUrl) {
        Write-Host ""
        Write-Host "Your backend is deployed at:" -ForegroundColor Blue
        Write-Host "https://$railwayUrl" -ForegroundColor Green
        Write-Host ""
        Write-Host "Test your deployment:"
        Write-Host "  curl https://$railwayUrl/health"
        Write-Host ""
        Write-Host "View logs:"
        Write-Host "  railway logs"
        Write-Host ""
        Write-Host "Open dashboard:"
        Write-Host "  railway open"
    }
    
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Run migrations: railway run alembic upgrade head"
    Write-Host "  2. Create admin user (see RAILWAY_DEPLOYMENT_GUIDE.md)"
    Write-Host "  3. Test endpoints"
    Write-Host "  4. Configure custom domain (optional)"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "✗ Deployment Failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Check the logs above for errors"
    Write-Host ""
    Write-Host "Common issues:"
    Write-Host "  - Missing environment variables"
    Write-Host "  - Database connection error"
    Write-Host "  - Build errors"
    Write-Host ""
    Write-Host "View logs: railway logs"
    Write-Host "Get help: https://docs.railway.app"
    exit 1
}
