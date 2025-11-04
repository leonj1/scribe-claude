import React, { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Typography, message } from 'antd';
import { UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import RecordingsList from '../components/RecordingsList';
import RecordingView from '../components/RecordingView';
import './Dashboard.css';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

interface Recording {
  id: string;
  status: string;
  created_at: string;
  transcription_text?: string;
  notes?: string;
}

const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [selectedRecording, setSelectedRecording] = useState<Recording | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleLogout = () => {
    logout();
    navigate('/');
    message.success('Logged out successfully');
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        Logout
      </Menu.Item>
    </Menu>
  );

  const handleRecordingSelect = (recording: Recording) => {
    setSelectedRecording(recording);
  };

  const handleRecordingCreated = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleRecordingUpdated = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <Layout className="dashboard-layout">
      <Header className="dashboard-header">
        <Title level={3} className="dashboard-title">
          Audio Transcription
        </Title>
        <Dropdown overlay={userMenu} placement="bottomRight">
          <Avatar
            size="large"
            icon={<UserOutlined />}
            className="user-avatar"
            style={{ cursor: 'pointer' }}
          />
        </Dropdown>
      </Header>

      <Layout>
        <Sider width={300} theme="light" className="recordings-sider">
          <RecordingsList
            onRecordingSelect={handleRecordingSelect}
            selectedRecordingId={selectedRecording?.id}
            refreshTrigger={refreshTrigger}
          />
        </Sider>

        <Content className="main-content">
          <RecordingView
            recording={selectedRecording}
            onRecordingCreated={handleRecordingCreated}
            onRecordingUpdated={handleRecordingUpdated}
          />
        </Content>

        <Sider width={250} theme="light" className="metadata-sider">
          <div className="metadata-panel">
            <Title level={5}>Metadata</Title>
            {selectedRecording && (
              <div className="metadata-content">
                <p><strong>Status:</strong> {selectedRecording.status}</p>
                <p><strong>Created:</strong> {new Date(selectedRecording.created_at).toLocaleString()}</p>
              </div>
            )}
          </div>
        </Sider>
      </Layout>
    </Layout>
  );
};

export default Dashboard;
