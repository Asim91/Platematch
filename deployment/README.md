# Service Configuration Guide for RegName Matcher

## Overview
This directory contains YAML configuration files for Google Cloud Run services.

## Project Information
- **Project ID**: platematch
- **Region**: europe-west1
- **Services**:
  - Frontend (Port: 3000)
  - Backend (Port: 8080)

## Service Files
- `backend-service.yaml`: Backend service configuration
- `frontend-service.yaml`: Frontend service configuration
- `policy.yaml`: IAM policy configuration for public access

## Applying Configuration Changes

### After Frontend Deployment
1. Get the frontend URL from GitHub Actions output
2. Update CORS_ORIGINS in backend-service.yaml:
```powershell
# Navigate to the deployment directory
\deployment

# Apply backend service configuration
gcloud run services replace .\backend-service.yaml --region=europe-west1
```

### After Backend Deployment
1. Get the backend URL from GitHub Actions output
2. Update NEXT_PUBLIC_BACKEND_URL in frontend-service.yaml:
```powershell
# Navigate to the deployment directory
\deployment

# Apply frontend service configuration
gcloud run services replace .\frontend-service.yaml --region=europe-west1
```

## Useful Commands

### Get Service URLs
```powershell
# Navigate to the deployment directory
cd c:\Development\RegName Matcher\deployment

# List all services and their URLs
gcloud run services list --platform managed --region=europe-west1
```

### View Current Configuration
```powershell
# Navigate to the deployment directory
cd c:\Development\RegName Matcher\deployment

# View backend configuration
gcloud run services describe platematch-backend --region=europe-west1

# View frontend configuration
gcloud run services describe platematch-frontend --region=europe-west1
```

## Setting Up Public Access
```powershell
# Navigate to deployment directory
cd c:\Development\RegName Matcher\deployment

# Apply IAM policy to both services
gcloud run services set-iam-policy platematch-backend policy.yaml --region=europe-west1
gcloud run services set-iam-policy platematch-frontend policy.yaml --region=europe-west1
```