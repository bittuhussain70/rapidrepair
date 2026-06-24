# RapidRepair Multi-Service Launcher (Windows PowerShell)
# Runs Flask app and Node.js worker in parallel

Write-Host "🚀 Starting RapidRepair Services..." -ForegroundColor Green
Write-Host ""

# Function to cleanup processes
function Cleanup {
    Write-Host ""
    Write-Host "Shutting down services..." -ForegroundColor Yellow
    try {
        Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
        Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    } catch {}
    exit 0
}

# Handle Ctrl+C
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {Cleanup}

# Check Python virtual environment
if (!(Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    & ".\.venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
} else {
    & ".\.venv\Scripts\Activate.ps1"
}

# Start Flask app
Write-Host "Starting Flask app on port 5000..." -ForegroundColor Cyan
$flaskProcess = Start-Process python -ArgumentList "app.py" -PassThru -NoNewWindow -RedirectStandardOutput "server.out.log" -RedirectStandardError "server.err.log"
Write-Host "Flask app PID: $($flaskProcess.Id)"

# Wait for Flask to start
Start-Sleep -Seconds 2

# Install worker dependencies if needed
if (!(Test-Path "worker\node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
    Push-Location worker
    npm install
    Pop-Location
}

# Start Node.js worker
Write-Host "Starting Node.js worker on port 3000..." -ForegroundColor Cyan
$workerProcess = Start-Process node -ArgumentList "src/index.js" -WorkingDirectory "worker" -PassThru -NoNewWindow -RedirectStandardOutput "worker.out.log" -RedirectStandardError "worker.err.log"
Write-Host "Worker PID: $($workerProcess.Id)"

Write-Host ""
Write-Host "✅ Services started successfully!" -ForegroundColor Green
Write-Host "📊 Flask app: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "⚙️  Worker API: http://127.0.0.1:3000/api/worker/health" -ForegroundColor Green
Write-Host "📈 Analytics: http://127.0.0.1:3000/api/worker/analytics" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Wait for processes
while ($flaskProcess.HasExited -eq $false -and $workerProcess.HasExited -eq $false) {
    Start-Sleep -Seconds 1
}

Cleanup
