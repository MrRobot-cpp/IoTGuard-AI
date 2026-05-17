# Kill any existing process on port 8000
$existing = netstat -ano | Select-String ":8000 " | ForEach-Object {
    ($_ -split '\s+')[-1]
} | Sort-Object -Unique
foreach ($pid in $existing) {
    if ($pid -match '^\d+$') {
        try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
    }
}
Start-Sleep -Seconds 1

# Start backend
Set-Location "$PSScriptRoot\backend"
python -m uvicorn main:app --reload --port 8000
