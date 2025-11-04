import React from 'react';
import { Button, Typography } from 'antd';
import { GoogleOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';
import './LandingPage.css';

const { Title, Paragraph } = Typography;

const LandingPage: React.FC = () => {
  const handleGoogleLogin = () => {
    window.location.href = apiService.getGoogleLoginUrl();
  };

  return (
    <div className="landing-page">
      <div className="hero-section">
        <div className="hero-content">
          <Title level={1} className="hero-title">
            Audio Transcription Service
          </Title>
          <Paragraph className="hero-subtitle">
            Secure, HIPAA-compliant audio transcription for healthcare professionals
          </Paragraph>
          <Paragraph className="hero-description">
            Record patient notes, automatically transcribe with AI, and manage your recordings
            all in one secure platform.
          </Paragraph>
          <Button
            type="primary"
            size="large"
            icon={<GoogleOutlined />}
            onClick={handleGoogleLogin}
            className="login-button"
          >
            Login with Google
          </Button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
