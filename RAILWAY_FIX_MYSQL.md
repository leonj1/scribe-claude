# Fix: Multiple MySQL Services on Railway

## Problem
Railway is provisioning 3 MySQL services instead of 1.

## Root Cause
Railway auto-detects `docker-compose.yml` which defines a MySQL service. When deploying a monorepo with multiple services (backend, frontend), Railway may provision MySQL multiple times.

## Solution

### Step 1: Remove Duplicate MySQL Services
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select your project
3. Identify the 3 MySQL services
4. Delete 2 of them, keeping only ONE MySQL service
5. Note the name/ID of the remaining MySQL service

### Step 2: Update Backend to Use Single MySQL
1. Go to the **backend** service settings
2. In the "Variables" tab, ensure `MYSQL_URL` references the single MySQL service:
   ```
   MYSQL_URL=mysql+pymysql://root:${{MySQL.MYSQL_ROOT_PASSWORD}}@${{MySQL.MYSQL_HOST}}:${{MySQL.MYSQL_PORT}}/${{MySQL.MYSQL_DATABASE}}
   ```
   Replace `MySQL` with the actual name of your MySQL service if different.

### Step 3: Verify Configuration Files
The following changes prevent Railway from auto-provisioning MySQL:

1. **`.railwayignore`** - Ignores `docker-compose.yml` to prevent auto-detection
2. **`backend/railway.json`** - Backend config (no database provisioning)
3. **`frontend/railway.json`** - Frontend config (no database provisioning)

### Step 4: Redeploy
1. Commit the `.railwayignore` file:
   ```bash
   git add .railwayignore RAILWAY_FIX_MYSQL.md
   git commit -m "Fix: Prevent multiple MySQL instances on Railway"
   git push
   ```

2. Railway will automatically redeploy both services

3. Verify in Railway Dashboard that only 1 MySQL service exists

## Prevention
- The `.railwayignore` file prevents Railway from detecting `docker-compose.yml`
- Each service (backend/frontend) has its own `railway.json` that doesn't request a database
- The backend service connects to the manually provisioned MySQL via environment variables

## Manual MySQL Provisioning (If Needed)
If you need to create a new MySQL service:
1. In Railway Dashboard, click "+ New"
2. Select "Database" → "MySQL"  
3. Railway provisions a single MySQL instance
4. Connect backend to it via environment variables

## Important Notes
- **Frontend does NOT need MySQL** - only the backend needs database access
- **Only provision 1 MySQL service** for the entire project
- The MySQL service is shared between all environments in the project
