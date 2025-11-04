import React, { useState, useRef, useEffect } from 'react';
import { Button, Card, message, Space, Typography } from 'antd';
import {
  AudioOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  StopOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import { apiService } from '../services/api';
import WaveformVisualizer from './WaveformVisualizer';
import './AudioRecorder.css';

const { Title, Text } = Typography;

interface AudioRecorderProps {
  onRecordingCreated: () => void;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ onRecordingCreated }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingId, setRecordingId] = useState<string | null>(null);
  const [chunkIndex, setChunkIndex] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const chunkTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) clearInterval(timerRef.current);
      if (chunkTimerRef.current) clearInterval(chunkTimerRef.current);
    };
  }, []);

  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const uploadChunk = async (blob: Blob, index: number, recId: string) => {
    try {
      await apiService.uploadChunk(recId, index, blob);
      console.log(`Chunk ${index} uploaded successfully`);
    } catch (error) {
      console.error(`Failed to upload chunk ${index}:`, error);
      message.error(`Failed to upload audio chunk ${index}`);
    }
  };

  const startChunkedUpload = (recId: string) => {
    // Upload chunks every 20 seconds
    chunkTimerRef.current = setInterval(() => {
      if (audioChunksRef.current.length > 0 && mediaRecorderRef.current?.state === 'recording') {
        const currentChunks = [...audioChunksRef.current];
        audioChunksRef.current = [];

        const blob = new Blob(currentChunks, { type: 'audio/webm' });
        const currentIndex = chunkIndex;
        setChunkIndex(prev => prev + 1);

        uploadChunk(blob, currentIndex, recId);
      }
    }, 20000); // 20 seconds
  };

  const stopChunkedUpload = () => {
    if (chunkTimerRef.current) {
      clearInterval(chunkTimerRef.current);
      chunkTimerRef.current = null;
    }
  };

  const handleStartRecording = async () => {
    try {
      // Create new recording session
      const recording = await apiService.createRecording();
      setRecordingId(recording.id);

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(1000); // Collect data every second

      setIsRecording(true);
      setIsPaused(false);
      setElapsedTime(0);
      setChunkIndex(0);
      startTimer();
      startChunkedUpload(recording.id);

      message.success('Recording started');
    } catch (error) {
      console.error('Failed to start recording:', error);
      message.error('Failed to start recording. Please check microphone permissions.');
    }
  };

  const handlePauseRecording = async () => {
    if (mediaRecorderRef.current && recordingId) {
      if (isPaused) {
        // Resume
        mediaRecorderRef.current.resume();
        setIsPaused(false);
        startTimer();
        message.info('Recording resumed');
      } else {
        // Pause
        mediaRecorderRef.current.pause();
        setIsPaused(true);
        stopTimer();
        await apiService.pauseRecording(recordingId);
        message.info('Recording paused');
      }
    }
  };

  const handleStopRecording = async () => {
    if (mediaRecorderRef.current && recordingId) {
      setIsProcessing(true);
      stopTimer();
      stopChunkedUpload();

      // Upload final chunk if any
      if (audioChunksRef.current.length > 0) {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await uploadChunk(blob, chunkIndex, recordingId);
      }

      mediaRecorderRef.current.stop();

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      try {
        // Finish recording and trigger transcription
        await apiService.finishRecording(recordingId);
        message.success('Recording saved and transcription started!');

        // Reset state
        setIsRecording(false);
        setIsPaused(false);
        setRecordingId(null);
        setChunkIndex(0);
        setElapsedTime(0);
        audioChunksRef.current = [];

        onRecordingCreated();
      } catch (error) {
        console.error('Failed to finish recording:', error);
        message.error('Failed to finish recording');
      } finally {
        setIsProcessing(false);
      }
    }
  };

  if (!isRecording) {
    return (
      <Card className="recorder-card-empty">
        <div className="recorder-empty-state">
          <AudioOutlined className="recorder-icon-large" />
          <Title level={4}>Start a New Recording</Title>
          <Text type="secondary">Click the button below to begin recording</Text>
          <Button
            type="primary"
            size="large"
            icon={<AudioOutlined />}
            onClick={handleStartRecording}
            className="start-recording-button"
          >
            Start Recording
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="recorder-card-active">
      <div className="recorder-active-state">
        <Title level={4}>
          {isPaused ? 'Recording Paused' : 'Recording in Progress'}
        </Title>

        <div className="waveform-container">
          <WaveformVisualizer isActive={!isPaused} stream={streamRef.current} />
        </div>

        <div className="recording-timer">
          <Text strong style={{ fontSize: 24 }}>
            {formatTime(elapsedTime)}
          </Text>
        </div>

        <Space size="large" className="recorder-controls">
          <Button
            size="large"
            icon={isPaused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
            onClick={handlePauseRecording}
            disabled={isProcessing}
          >
            {isPaused ? 'Resume' : 'Pause'}
          </Button>

          <Button
            type="primary"
            danger
            size="large"
            icon={isProcessing ? <LoadingOutlined /> : <StopOutlined />}
            onClick={handleStopRecording}
            loading={isProcessing}
          >
            End Recording
          </Button>
        </Space>
      </div>
    </Card>
  );
};

export default AudioRecorder;
