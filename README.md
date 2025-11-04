# Audio Transcription Service for Healthcare

A HIPAA-compliant audio transcription platform designed for healthcare professionals to record patient notes and automatically transcribe them using AI.

## Features

- **Google OAuth Authentication**: Secure login with Google accounts
- **Long-form Audio Recording**: Record hours of audio with pause/resume functionality
- **Chunked Streaming**: Audio is streamed in 20-second chunks to prevent data loss
- **AI-Powered Transcription**: Automatic transcription using RequestYai LLM provider
- **HIPAA Compliance**: End-to-end encryption for audio files and transcriptions
- **User-Friendly Dashboard**: 3-pane interface for managing recordings
- **Notes Feature**: Add contextual notes to recording sessions

## Architecture

### Backend (FastAPI)
- Google OAuth2 authentication with JWT tokens
- Repository pattern for database abstraction
- LLM provider abstraction for transcription services
- Encryption at rest for audio and transcription data
- RESTful API endpoints

### Frontend (React + TypeScript)
- Ant Design UI components
- MediaRecorder API for audio capture
- Real-time waveform visualization
- Chunked audio upload to backend
- JWT-based authentication

### Database (MySQL)
- User management
- Recording sessions
- Audio chunks metadata
- Encrypted transcriptions

## Prerequisites

- Docker and Docker Compose
- Google Cloud Console account (for OAuth credentials)
- RequestYai API key (or configure alternative LLM provider)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd claude
```

### 2. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure consent screen
6. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback`
   - (Add production URL when deploying)
7. Copy the Client ID and Client Secret

### 3. Generate Encryption Key

For HIPAA-compliant encryption, generate a Fernet encryption key:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-actual-client-id
GOOGLE_CLIENT_SECRET=your-actual-client-secret

# LLM Provider Configuration
LLM_API_KEY=your-requestyai-api-key

# JWT Configuration (generate a secure random string)
JWT_SECRET=your-secure-random-secret-key

# Encryption Configuration
ENCRYPTION_KEY=your-generated-fernet-key
```

### 5. Start the Application

```bash
docker-compose up --build
```

The services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **MySQL**: localhost:3306

### 6. Access the Application

1. Open http://localhost:3000 in your browser
2. Click "Login with Google"
3. Authorize the application
4. Start recording!

## Project Structure

```
.
├── backend/
│   ├── models/              # SQLAlchemy database models
│   ├── repositories/        # Repository pattern implementations
│   ├── routers/            # FastAPI route handlers
│   ├── middleware/         # Authentication middleware
│   ├── llm/                # LLM provider abstraction
│   ├── utils/              # Utilities (JWT, encryption, audio)
│   ├── main.py             # FastAPI application entry point
│   ├── database.py         # Database configuration
│   ├── config.py           # Settings management
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts (Auth)
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service
│   │   └── App.tsx         # Main application component
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
└── docker-compose.yml      # Docker orchestration
```

## API Endpoints

### Authentication
- `GET /auth/google/login` - Initiate Google OAuth flow
- `GET /auth/google/callback` - Handle OAuth callback

### Recordings
- `POST /recordings` - Create new recording session
- `POST /recordings/{id}/chunks` - Upload audio chunk
- `PATCH /recordings/{id}/pause` - Pause recording
- `POST /recordings/{id}/finish` - Finish recording and trigger transcription
- `GET /recordings` - List user's recordings
- `GET /recordings/{id}` - Get specific recording
- `PATCH /recordings/{id}/notes` - Update recording notes

## HIPAA Compliance

This application implements several measures to maintain HIPAA compliance:

### 1. Data Encryption
- **At Rest**: All audio files and transcriptions are encrypted using Fernet (AES-128)
- **In Transit**: HTTPS/TLS required for all network communication (configure in production)

### 2. Access Control
- JWT-based authentication for all API endpoints
- User-specific data isolation
- OAuth2 with Google for secure authentication

### 3. Audit Logging
- All database operations are timestamped
- User actions are traceable through JWT tokens
- Consider implementing comprehensive audit logs in production

### 4. Data Integrity
- Database constraints ensure data consistency
- Chunked upload prevents data loss during long recordings
- Automatic retry mechanisms for failed uploads

### 5. Production Recommendations

For production deployment, ensure:

1. **Use HTTPS**: Configure SSL/TLS certificates
2. **Secure Secrets**: Use secret management systems (AWS Secrets Manager, HashiCorp Vault)
3. **Database Security**: Enable MySQL encryption, use strong passwords
4. **Network Security**: Implement VPC, security groups, firewall rules
5. **Backup Strategy**: Regular encrypted backups of database and audio files
6. **Access Logs**: Implement comprehensive logging and monitoring
7. **Business Associate Agreement**: Ensure BAA with cloud providers
8. **Regular Updates**: Keep all dependencies updated for security patches

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Database Migrations

The application automatically creates database tables on startup. For production, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init migrations
# Configure alembic.ini and create migrations
```

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Customizing LLM Provider

To use a different transcription provider:

1. Create a new provider class in `backend/llm/`:

```python
# backend/llm/custom_provider.py
class CustomProvider:
    def transcribe_audio(self, audio_path: str) -> str:
        # Your implementation here
        pass
```

2. Update the import in `backend/routers/recordings.py`:

```python
from llm.custom_provider import CustomProvider
llm_provider = CustomProvider()
```

## Troubleshooting

### OAuth Redirect Issues
- Ensure redirect URI in Google Console matches exactly: `http://localhost:8000/auth/google/callback`
- Check that FRONTEND_URL is set correctly in backend environment

### Audio Recording Not Working
- Ensure browser has microphone permissions
- Check browser console for errors
- Verify MediaRecorder API is supported (Chrome, Firefox, Edge)

### Database Connection Errors
- Wait for MySQL container to be fully ready (healthcheck)
- Verify MySQL credentials in docker-compose.yml
- Check MySQL logs: `docker-compose logs mysql`

### Encryption Errors
- Ensure ENCRYPTION_KEY is a valid Fernet key (44 characters, base64)
- Regenerate key if corrupted

## License

[Your License Here]

## Support

For issues and questions, please open an issue on the GitHub repository.
