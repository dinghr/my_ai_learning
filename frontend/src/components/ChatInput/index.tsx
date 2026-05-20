import { useState } from 'react';
import { View, Text, Input } from '@tarojs/components';
import './index.scss';

interface ChatInputProps {
  onSend: (message: string) => void;
  onImagePick?: () => void;
  onVoiceStart?: () => void;
  onVoiceEnd?: () => void;
  loading?: boolean;
}

export default function ChatInput({
  onSend,
  onImagePick,
  onVoiceStart,
  onVoiceEnd,
  loading = false,
}: ChatInputProps) {
  const [text, setText] = useState('');
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [recording, setRecording] = useState(false);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setText('');
  };

  const handleVoiceTouchStart = () => {
    setRecording(true);
    onVoiceStart?.();
  };

  const handleVoiceTouchEnd = () => {
    setRecording(false);
    onVoiceEnd?.();
  };

  return (
    <View className="chat-input-bar">
      {/* 语音/键盘切换 */}
      <View
        className="input-mode-btn"
        onClick={() => setIsVoiceMode(!isVoiceMode)}
      >
        <Text className="mode-icon">{isVoiceMode ? '⌨️' : '🎤'}</Text>
      </View>

      {/* 输入区域 */}
      {isVoiceMode ? (
        <View
          className={`voice-btn ${recording ? 'recording' : ''}`}
          onTouchStart={handleVoiceTouchStart}
          onTouchEnd={handleVoiceTouchEnd}
        >
          <Text className="voice-text">{recording ? '松开发送' : '按住说话'}</Text>
          {recording && <View className="voice-waves">
            <View className="wave" />
            <View className="wave" />
            <View className="wave" />
          </View>}
        </View>
      ) : (
        <View className="text-input-wrapper">
          <Input
            className="text-input"
            placeholder="问小棘的考古助手..."
            value={text}
            onInput={(e) => setText(e.detail.value)}
            confirmType="send"
            onConfirm={handleSend}
            disabled={loading}
          />
        </View>
      )}

      {/* 图片按钮 */}
      <View className="input-action-btn" onClick={onImagePick}>
        <Text className="action-icon">📷</Text>
      </View>

      {/* 发送按钮 */}
      {!isVoiceMode && (
        <View
          className={`send-btn ${text.trim() && !loading ? 'active' : ''}`}
          onClick={handleSend}
        >
          <Text className="send-icon">➤</Text>
        </View>
      )}
    </View>
  );
}
