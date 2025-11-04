import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../contexts/AuthContext';

const AuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setToken } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    const error = searchParams.get('error');

    if (token) {
      setToken(token);
      navigate('/dashboard');
    } else if (error) {
      console.error('Authentication error:', error);
      navigate('/?error=' + encodeURIComponent(error));
    } else {
      navigate('/');
    }
  }, [searchParams, navigate, setToken]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh'
    }}>
      <Spin size="large" tip="Authenticating..." />
    </div>
  );
};

export default AuthCallback;
