import React, { useEffect, useState } from 'react';
import { List, Typography, Tag, Spin, Empty } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';
import './RecordingsList.css';

const { Text } = Typography;

interface Recording {
  id: string;
  status: string;
  created_at: string;
  transcription_text?: string;
}

interface RecordingsListProps {
  onRecordingSelect: (recording: Recording) => void;
  selectedRecordingId?: string;
  refreshTrigger?: number;
}

const RecordingsList: React.FC<RecordingsListProps> = ({
  onRecordingSelect,
  selectedRecordingId,
  refreshTrigger
}) => {
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecordings();
  }, [refreshTrigger]);

  const fetchRecordings = async () => {
    try {
      setLoading(true);
      const data = await apiService.getRecordings();
      setRecordings(data);
    } catch (error) {
      console.error('Failed to fetch recordings:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'processing';
      case 'paused':
        return 'warning';
      case 'ended':
        return 'success';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <div className="recordings-loading">
        <Spin tip="Loading recordings..." />
      </div>
    );
  }

  if (recordings.length === 0) {
    return (
      <div className="recordings-empty">
        <Empty description="No recordings yet" />
      </div>
    );
  }

  return (
    <div className="recordings-list-container">
      <div className="recordings-list-header">
        <Text strong>Your Recordings</Text>
      </div>
      <List
        dataSource={recordings}
        renderItem={(recording) => (
          <List.Item
            className={`recording-item ${selectedRecordingId === recording.id ? 'selected' : ''}`}
            onClick={() => onRecordingSelect(recording)}
          >
            <div className="recording-item-content">
              <div className="recording-item-header">
                <ClockCircleOutlined />
                <Text className="recording-date">
                  {new Date(recording.created_at).toLocaleDateString()}
                </Text>
              </div>
              <Text className="recording-time" type="secondary">
                {new Date(recording.created_at).toLocaleTimeString()}
              </Text>
              <Tag color={getStatusColor(recording.status)} className="recording-status">
                {recording.status}
              </Tag>
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};

export default RecordingsList;
