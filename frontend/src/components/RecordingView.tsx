import React, { useState } from 'react';
import { Empty, Card, Typography, Divider, Input, Button, message } from 'antml:parameter>
import { AudioOutlined } from '@ant-design/icons';
import AudioRecorder from './AudioRecorder';
import { apiService } from '../services/api';
import './RecordingView.css';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

interface Recording {
  id: string;
  status: string;
  created_at: string;
  transcription_text?: string;
  notes?: string;
}

interface RecordingViewProps {
  recording: Recording | null;
  onRecordingCreated: () => void;
  onRecordingUpdated: () => void;
}

const RecordingView: React.FC<RecordingViewProps> = ({
  recording,
  onRecordingCreated,
  onRecordingUpdated
}) => {
  const [notes, setNotes] = useState('');
  const [savingNotes, setSavingNotes] = useState(false);

  const handleSaveNotes = async () => {
    if (!recording) return;

    try {
      setSavingNotes(true);
      await apiService.updateRecordingNotes(recording.id, notes);
      message.success('Notes saved successfully');
      onRecordingUpdated();
    } catch (error) {
      message.error('Failed to save notes');
    } finally {
      setSavingNotes(false);
    }
  };

  if (!recording) {
    return (
      <div className="recording-view-empty">
        <AudioRecorder onRecordingCreated={onRecordingCreated} />
      </div>
    );
  }

  return (
    <div className="recording-view">
      <Card className="recording-card">
        <Title level={4}>
          <AudioOutlined /> Recording from {new Date(recording.created_at).toLocaleString()}
        </Title>

        <Divider />

        {recording.transcription_text ? (
          <div className="transcription-section">
            <Title level={5}>Transcription</Title>
            <Card className="transcription-card">
              <Paragraph className="transcription-text">
                {recording.transcription_text}
              </Paragraph>
            </Card>
          </div>
        ) : (
          <Empty description="Transcription not yet available" />
        )}

        <Divider />

        <div className="notes-section">
          <Title level={5}>Notes</Title>
          <TextArea
            rows={4}
            placeholder="Add notes about this recording session..."
            value={notes || recording.notes || ''}
            onChange={(e) => setNotes(e.target.value)}
            className="notes-textarea"
          />
          <Button
            type="primary"
            onClick={handleSaveNotes}
            loading={savingNotes}
            style={{ marginTop: 16 }}
          >
            Save Notes
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default RecordingView;
