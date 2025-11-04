# Railway Deployment Guide

This guide explains how to deploy the Audio Transcription Service to Railway.

## Architecture on Railway

The application will be deployed as three separate services:
1. **Backend Service** (FastAPI)
2. **Frontend Service** (React)
3. **MySQL Database**

## Prerequisites

- [Railway Account](https://railway.app/) (free tier available)
- [Railway CLI](https://docs.railway.app/develop/cli) (optional but recommended)
- GitHub account (for automatic deployments)

## Deployment Steps

### Option 1: Deploy via Railway Dashboard (Recommended)

#### 1. Create a New Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository

#### 2. Add MySQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "MySQL"
3. Railway will provision a MySQL database and provide connection details

#### 3. Deploy Backend Service

1. Click "+ New" → "GitHub Repo"
2. Select your repository
3. Configure the service:
   - **Service Name**: `backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Add environment variables:
   ```
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   LLM_API_KEY=your-llm-api-key
   MYSQL_URL=mysql+pymysql://root:${{MySQL.MYSQL_ROOT_PASSWORD}}@${{MySQL.MYSQL_HOST}}:${{MySQL.MYSQL_PORT}}/${{MySQL.MYSQL_DATABASE}}
   AUDIO_STORAGE_PATH=/app/audio_storage
   JWT_SECRET=your-secure-random-secret-key
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_MINUTES=10080
   ENCRYPTION_KEY=your-fernet-encryption-key
   REDIRECT_URI=${{RAILWAY_PUBLIC_DOMAIN}}/auth/google/callback
   FRONTEND_URL=${{frontend.RAILWAY_PUBLIC_DOMAIN}}
   ```

5. Enable public networking to get a URL

#### 4. Deploy Frontend Service

1. Click "+ New" → "GitHub Repo"
2. Select your repository again
3. Configure the service:
   - **Service Name**: `frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx serve -s build -l $PORT`

4. Add environment variables:
   ```
   REACT_APP_API_URL=${{backend.RAILWAY_PUBLIC_DOMAIN}}
   ```

5. Enable public networking to get a URL

#### 5. Update Google OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to your OAuth 2.0 credentials
3. Add the Railway backend URL to authorized redirect URIs:
   ```
   https://your-backend-url.railway.app/auth/google/callback
   ```
4. Add the Railway frontend URL to authorized origins:
   ```
   https://your-frontend-url.railway.app
   ```

### Option 2: Deploy via Railway CLI

#### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. Login to Railway

```bash
railway login
```

#### 3. Create New Project

```bash
railway init
```

#### 4. Add MySQL Database

```bash
railway add mysql
```

#### 5. Deploy Backend

```bash
cd backend
railway up
```

Set environment variables:
```bash
railway variables set GOOGLE_CLIENT_ID=your-value
railway variables set GOOGLE_CLIENT_SECRET=your-value
railway variables set LLM_API_KEY=your-value
# ... set other variables
```

#### 6. Deploy Frontend

```bash
cd ../frontend
railway up
```

Set environment variables:
```bash
railway variables set REACT_APP_API_URL=your-backend-url
```

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `123456789-abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | `GOCSPX-xxxxx` |
| `LLM_API_KEY` | API key for transcription service | `your-api-key` |
| `MYSQL_URL` | MySQL connection string | `mysql+pymysql://user:pass@host:port/db` |
| `AUDIO_STORAGE_PATH` | Path for audio file storage | `/app/audio_storage` |
| `JWT_SECRET` | Secret key for JWT tokens | Generate with `openssl rand -hex 32` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRATION_MINUTES` | JWT token expiration time | `10080` (7 days) |
| `ENCRYPTION_KEY` | Fernet encryption key | Generate with Python Fernet |
| `REDIRECT_URI` | OAuth callback URL | `https://backend.railway.app/auth/google/callback` |
| `FRONTEND_URL` | Frontend URL for CORS | `https://frontend.railway.app` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://backend.railway.app` |

## Generating Required Keys

### JWT Secret

```bash
openssl rand -hex 32
```

### Encryption Key (Fernet)

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Monitoring and Logs

### View Logs

In Railway Dashboard:
1. Select your service
2. Click "Deployments" tab
3. Click on the latest deployment
4. View real-time logs

Via CLI:
```bash
railway logs
```

### Health Checks

- Backend: `https://your-backend-url.railway.app/health`
- Frontend: `https://your-frontend-url.railway.app/`

## Troubleshooting

### Backend Won't Start

1. Check environment variables are set correctly
2. Verify MySQL connection string
3. Check logs for errors: `railway logs`

### Frontend Can't Connect to Backend

1. Verify `REACT_APP_API_URL` is set correctly
2. Check CORS settings in backend
3. Ensure both services have public networking enabled

### OAuth Errors

1. Verify redirect URIs in Google Console match Railway URLs
2. Check `REDIRECT_URI` and `FRONTEND_URL` environment variables
3. Ensure HTTPS is being used (Railway provides this automatically)

### Database Connection Issues

1. Verify MySQL service is running
2. Check `MYSQL_URL` environment variable
3. Ensure Railway MySQL service is in the same project

## Cost Considerations

Railway offers:
- **Free Tier**: $5 of usage per month
- **Hobby Plan**: $5/month + usage
- **Pro Plan**: $20/month + usage

This application typically uses:
- Backend: ~1GB RAM, minimal CPU
- Frontend: ~512MB RAM (during build), minimal after
- MySQL: ~512MB RAM

**Estimated monthly cost**: Free tier should cover development/testing. Production may require Hobby or Pro plan.

## Scaling

To scale your application:
1. Go to service settings in Railway Dashboard
2. Adjust "Replicas" setting (Pro plan required)
3. Consider using Railway's auto-scaling features

## Backups

### Database Backups

Railway doesn't provide automatic backups on free/hobby plans. Consider:
1. Upgrading to Pro plan for automated backups
2. Implementing manual backup scripts
3. Using external backup solutions

### Audio File Backups

Audio files are stored in ephemeral storage. For production:
1. Use Railway Volumes for persistent storage
2. Consider external storage (S3, Google Cloud Storage)
3. Implement regular backup procedures

## Security Best Practices

1. **Never commit sensitive keys** - Use Railway environment variables
2. **Rotate secrets regularly** - Update JWT_SECRET and ENCRYPTION_KEY periodically
3. **Use strong passwords** - For MySQL and all services
4. **Enable 2FA** - On your Railway account
5. **Monitor access logs** - Regularly check for suspicious activity
6. **Keep dependencies updated** - Run `npm audit` and `pip-audit` regularly

## Support

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Project Issues](https://github.com/yourusername/scribe-claude/issues)
