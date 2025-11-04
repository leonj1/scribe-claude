# Railway Frontend Build Error Fix

## Error
```
Nixpacks was unable to generate a build plan for this app.
```

## Root Cause
Railway is attempting to build from the repository root directory, which contains multiple directories (`frontend/`, `backend/`, etc.). Nixpacks cannot automatically detect which application to build from this multi-service monorepo structure.

## Solution

### Method 1: Railway Dashboard (Recommended)

1. Navigate to [Railway Dashboard](https://railway.app/dashboard)
2. Open your project
3. Click on the **frontend** service
4. Navigate to the **Settings** tab
5. Locate the **Root Directory** configuration
6. Set the value to: `frontend`
7. Save the changes (deployment will trigger automatically)

### Method 2: Railway CLI

```bash
# Select the frontend service
railway service --name frontend

# Set the root directory
railway service settings --root-directory frontend
```

### Method 3: Service Configuration File

If using Railway's service configuration, ensure your `railway.toml` or service settings specify:

```toml
[build]
builder = "NIXPACKS"

[deploy]
rootDirectory = "frontend"
```

## Verification

After applying the fix:

1. Railway will redeploy the frontend service
2. Nixpacks will now detect the React application from `frontend/package.json`
3. The build process will follow the configuration in `frontend/nixpacks.toml`:
   - Setup: Install Node.js 20.x
   - Install: Run `npm install`
   - Build: Run `npm run build`
   - Start: Run `npx serve -s build -l $PORT`

## Similarly for Backend

If your backend service has the same issue, apply the same fix:
- Set Root Directory to: `backend`

## Files Already Configured

Both services have proper configuration files in their respective directories:

- ✅ `frontend/nixpacks.toml` - Nixpacks build configuration
- ✅ `frontend/railway.json` - Railway service configuration
- ✅ `frontend/package.json` - Node.js dependencies and scripts
- ✅ `backend/nixpacks.toml` - Backend Nixpacks configuration
- ✅ `backend/railway.json` - Backend Railway configuration

The code is ready; only the Railway service settings need adjustment.

## Expected Deployment Flow

After fixing the root directory:

```
Railway → Clone Repo → CD to frontend/ → Nixpacks Detect → Build → Deploy
```

Instead of:

```
Railway → Clone Repo → Stay in root → Nixpacks Fail ❌
```
