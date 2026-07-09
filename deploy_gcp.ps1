# ========================================================
#            STADIUMOS GCP CLOUD RUN DEPLOYER
# ========================================================
# This script builds and deploys both backend and frontend 
# containers to Google Cloud Run.
# ========================================================

Write-Host "========================================================" -ForegroundColor Green
Write-Host "         StadiumOS GCP Cloud Run Deployer" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

# 1. Retrieve current GCP Project
$currentProject = gcloud config get-value project 2>$null
if ([string]::IsNullOrEmpty($currentProject)) {
    Write-Host "[Warning] No default GCP project configuration detected." -ForegroundColor Yellow
    $projectId = Read-Host "Enter your Google Cloud Project ID"
    if ([string]::IsNullOrEmpty($projectId)) {
        Write-Error "Project ID is required. Exiting."
        Exit
    }
    Write-Host "[System] Configuring gcloud to project: $projectId..." -ForegroundColor Cyan
    gcloud config set project $projectId
} else {
    Write-Host "Active GCP Project detected: $currentProject" -ForegroundColor Green
    $choice = Read-Host "Do you want to deploy to this project? (Y/n)"
    if ($choice.ToLower() -eq 'n') {
        $projectId = Read-Host "Enter your Google Cloud Project ID"
        gcloud config set project $projectId
    } else {
        $projectId = $currentProject
    }
}

# 2. Enable Required APIs
Write-Host ""
Write-Host "[1/4] Enabling required GCP service APIs (Cloud Run, Artifact Registry)..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to enable service APIs. Check billing status and project permissions."
    Exit
}
Write-Host "APIs enabled successfully." -ForegroundColor Green

# Optional: Configure GEMINI_API_KEY for Backend container
Write-Host ""
$envKey = $env:GEMINI_API_KEY
$geminiApiKey = ""
if (![string]::IsNullOrEmpty($envKey)) {
    Write-Host "GEMINI_API_KEY detected in local environment." -ForegroundColor Green
    $keyChoice = Read-Host "Do you want to use this API key for backend? (Y/n)"
    if ($keyChoice.ToLower() -ne 'n') {
        $geminiApiKey = $envKey
    }
}

if ([string]::IsNullOrEmpty($geminiApiKey)) {
    $geminiApiKey = Read-Host "Enter your GEMINI_API_KEY (optional, press Enter to use Google Cloud IAM / default Service Account authentication)"
}

# 3. Build & Deploy Backend
Write-Host ""
Write-Host "[2/4] Deploying FastAPI Backend to Cloud Run..." -ForegroundColor Cyan

$backendArgs = @(
    "run", "deploy", "stadium-os-backend",
    "--source", "./backend",
    "--region", "us-central1",
    "--allow-unauthenticated",
    "--format=value(status.address.url)"
)
if (![string]::IsNullOrEmpty($geminiApiKey)) {
    $backendArgs += "--set-env-vars"
    $backendArgs += "GEMINI_API_KEY=$geminiApiKey"
}

gcloud @backendArgs > backend_url.txt

if ($LASTEXITCODE -ne 0) {
    Write-Error "Backend deployment failed. Exiting."
    Exit
}

$backendUrl = (Get-Content backend_url.txt).Trim()
Remove-Item backend_url.txt -Force
Write-Host "Backend deployed successfully! URL: $backendUrl" -ForegroundColor Green

# 4. Build & Deploy Frontend (Injecting the backend URL during compile stage)
Write-Host ""
Write-Host "[3/4] Deploying Vite React Frontend to Cloud Run..." -ForegroundColor Cyan
Write-Host "Injecting API Endpoint: VITE_API_URL=$backendUrl" -ForegroundColor Gray

gcloud run deploy stadium-os-frontend `
    --source ./frontend `
    --region us-central1 `
    --allow-unauthenticated `
    --set-build-env-vars VITE_API_URL=$backendUrl `
    --format="value(status.address.url)" > frontend_url.txt

if ($LASTEXITCODE -ne 0) {
    Write-Error "Frontend deployment failed. Exiting."
    Exit
}

$frontendUrl = (Get-Content frontend_url.txt).Trim()
Remove-Item frontend_url.txt -Force

# 5. Summary
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Frontend Dashboard UI: $frontendUrl" -ForegroundColor Cyan
Write-Host "Backend REST API Docs: $backendUrl/docs" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to complete..."
Read-Host
