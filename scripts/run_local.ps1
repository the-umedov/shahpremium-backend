<#
ShahPremium'ni lokal kompyuterda ishga tushirish (baza + backend + frontend).

Uchala papka BITTA ota-papka ichida yonma-yon turishi kerak (disk harfi muhim emas):
    <ota-papka>\shahpremiumuz-python      (backend)
    <ota-papka>\shahpremiumuz-frontend    (frontend)
    <ota-papka>\pgdata-shahpremium        (PostgreSQL dasturi + ma'lumotlar)

Ishlatish (shahpremiumuz-python papkasida turib):
    powershell -ExecutionPolicy Bypass -File .\scripts\run_local.ps1
Kutubxonalarni majburan qayta o'rnatish:
    powershell -ExecutionPolicy Bypass -File .\scripts\run_local.ps1 -Reinstall
#>
param([switch]$Reinstall)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$backend = Join-Path $root "shahpremiumuz-python"
$frontend = Join-Path $root "shahpremiumuz-frontend"
$pg = Join-Path $root "pgdata-shahpremium"

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Yellow }
function Ok($msg) { Write-Host "    $msg" -ForegroundColor Green }
function Listening($port) { [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) }

foreach ($dir in $backend, $frontend, $pg) {
    if (-not (Test-Path $dir)) { throw "Papka topilmadi: $dir  (uchala papka bitta joyda yonma-yon bo'lishi kerak)" }
}

# ---- 1. Python ----
Step "Python qidirilmoqda (3.11 yoki yangiroq kerak)"
$pyExe = $null
$probe = "import sys; print(sys.executable if sys.version_info >= (3, 11) else '')"
foreach ($cmd in @("py -3.13", "py -3", "python")) {
    $parts = $cmd.Split(" ")
    if (-not (Get-Command $parts[0] -ErrorAction SilentlyContinue)) { continue }
    try {
        $out = & $parts[0] @($parts | Select-Object -Skip 1) -c $probe 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) { $pyExe = "$out".Trim(); break }
    } catch { }
}
if (-not $pyExe) { throw "Python 3.11+ topilmadi. https://www.python.org/downloads/ dan o'rnating ('Add python.exe to PATH' belgisini qo'ying)." }
Ok $pyExe

# ---- 2. Virtual muhitlar ----
# .venv boshqa kompyuterdan ko'chirilganda ishlamaydi (ichida eski Python'ning
# to'liq yo'li yozilgan) — shuning uchun tekshirib, kerak bo'lsa qayta yaratamiz.
function Ensure-Venv($dir, $imports) {
    $venvPy = Join-Path $dir ".venv\Scripts\python.exe"
    $healthy = $false
    if ((Test-Path $venvPy) -and -not $Reinstall) {
        try { & $venvPy -c "import $imports" 2>$null; $healthy = ($LASTEXITCODE -eq 0) } catch { $healthy = $false }
    }
    if ($healthy) { Ok "$(Split-Path $dir -Leaf): tayyor"; return }
    Write-Host "    $(Split-Path $dir -Leaf): kutubxonalar o'rnatilmoqda (birinchi marta bir necha daqiqa)..."
    $venv = Join-Path $dir ".venv"
    if (Test-Path $venv) { Remove-Item $venv -Recurse -Force }
    & $pyExe -m venv $venv
    & $venvPy -m pip install --quiet --upgrade pip
    & $venvPy -m pip install --quiet -r (Join-Path $dir "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "pip install xato bilan tugadi: $dir" }
    Ok "$(Split-Path $dir -Leaf): o'rnatildi"
}
Step "Kutubxonalar tekshirilmoqda"
Ensure-Venv $backend "fastapi, sqlalchemy, asyncpg"
Ensure-Venv $frontend "nicegui, httpx"

# ---- 3. PostgreSQL (port 5433) ----
Step "PostgreSQL (port 5433)"
if (Listening 5433) {
    Ok "allaqachon ishlab turibdi"
} else {
    # Papka server ishlab turganda ko'chirilgan bo'lsa, eski postmaster.pid qolib ketadi
    # va serverni ishga tushirishga to'sqinlik qiladi.
    $pidFile = Join-Path $pg "data\postmaster.pid"
    if ((Test-Path $pidFile) -and -not (Get-Process postgres -ErrorAction SilentlyContinue)) { Remove-Item $pidFile -Force }
    $pgBin = Join-Path $pg "pgsql\bin"
    $pgData = Join-Path $pg "data"
    $pgLog = Join-Path $pg "server.log"
    try {
        & (Join-Path $pgBin "pg_ctl.exe") -D $pgData -o "-p 5433" -l $pgLog -w start | Out-Null
    } catch {
        # Windows "Smart App Control" imzosiz pg_ctl.exe'ni bloklaydi, lekin
        # postgres.exe'ga ruxsat beradi — shu holatda serverni to'g'ridan-to'g'ri ishga tushiramiz.
        Write-Host "    pg_ctl.exe bloklandi (Smart App Control) — postgres.exe to'g'ridan-to'g'ri ishga tushirilmoqda"
        Start-Process -FilePath (Join-Path $pgBin "postgres.exe") -ArgumentList "-D", "`"$pgData`"", "-p", "5433" `
            -WindowStyle Hidden -RedirectStandardError $pgLog
        foreach ($i in 1..30) { Start-Sleep -Seconds 1; if (Listening 5433) { break } }
    }
    if (-not (Listening 5433)) {
        if (Test-Path $pgLog) { Get-Content $pgLog -Tail 20 }
        throw ("PostgreSQL ishga tushmadi — yuqoridagi logni ko'ring. Agar 'Application Control policy' xatosi bo'lsa: " +
               "Windows Security -> App & browser control -> Smart App Control'ni tekshiring.")
    }
    Ok "ishga tushdi"
}

# ---- 4. Backend (port 4000) ----
Step "Backend (http://127.0.0.1:4000)"
if (Listening 4000) {
    Ok "allaqachon ishlab turibdi"
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command",
        "`$host.UI.RawUI.WindowTitle='ShahPremium backend'; Set-Location '$backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 4000"
    $up = $false
    foreach ($i in 1..60) {
        Start-Sleep -Seconds 1
        try { $r = Invoke-WebRequest "http://127.0.0.1:4000/api/v1/health" -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { $up = $true; break } } catch { }
    }
    if (-not $up) { throw "Backend 60 soniyada javob bermadi — 'ShahPremium backend' oynasidagi xatoni ko'ring." }
    Ok "ishga tushdi"
}

# ---- 5. Frontend (port 8080) ----
Step "Frontend (http://localhost:8080)"
if (Listening 8080) {
    Ok "allaqachon ishlab turibdi"
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command",
        "`$host.UI.RawUI.WindowTitle='ShahPremium frontend'; Set-Location '$frontend'; .\.venv\Scripts\python.exe main.py"
    foreach ($i in 1..40) { Start-Sleep -Seconds 1; if (Listening 8080) { break } }
    if (-not (Listening 8080)) { throw "Frontend ishga tushmadi — 'ShahPremium frontend' oynasidagi xatoni ko'ring." }
    Ok "ishga tushdi"
}

Start-Process "http://localhost:8080"
Write-Host "`nTayyor! Brauzerda http://localhost:8080 ochildi." -ForegroundColor Green
Write-Host "To'xtatish: 'ShahPremium backend' va 'ShahPremium frontend' oynalarini yoping."
Write-Host "Baza fonda ishlashda davom etadi (kompyuter o'chganda o'zi to'xtaydi) — keyingi safar skript uni qayta ishlatadi."
