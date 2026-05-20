import { useState } from 'react';
import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import './index.scss';

export interface PoemData {
  title: string;
  author: string;
  dynasty: string;
  content: string[];
  explanation: string;
  appreciation: string;
}

interface PoemCardProps {
  poem?: PoemData;
  onRefresh?: () => void;
  onComplete?: () => void;
  loading?: boolean;
}

export default function PoemCard({ poem, onRefresh, onComplete, loading }: PoemCardProps) {
  const [showExplanation, setShowExplanation] = useState(false);
  const [completed, setCompleted] = useState(false);

  const handleComplete = () => {
    setCompleted(true);
    onComplete?.();
    Taro.showToast({ title: '背诵完成！+15⭐', icon: 'success' });
  };

  if (loading) {
    return (
      <View className="poem-card loading">
        <View className="poem-loading">
          <Text className="loading-icon">📜</Text>
          <Text className="loading-text">正在翻阅古诗集...</Text>
        </View>
      </View>
    );
  }

  if (!poem) return null;

  return (
    <View className={`poem-card ${completed ? 'completed' : ''}`}>
      {/* 完成标记 */}
      {completed && (
        <View className="poem-complete-badge">
          <Text>✓ 已背诵</Text>
        </View>
      )}

      {/* 卡片头部：卷轴装饰 */}
      <View className="poem-header">
        <View className="scroll-decoration left" />
        <View className="poem-title-area">
          <Text className="poem-title">{poem.title}</Text>
          <Text className="poem-author">[{poem.dynasty}] {poem.author}</Text>
        </View>
        <View className="scroll-decoration right" />
      </View>

      {/* 诗句正文 */}
      <View className="poem-content">
        {poem.content.map((line, idx) => (
          <Text key={idx} className="poem-line">{line}</Text>
        ))}
      </View>

      {/* 注释/赏析（可展开） */}
      <View className="poem-explanation-toggle" onClick={() => setShowExplanation(!showExplanation)}>
        <Text className="toggle-text">
          {showExplanation ? '🔼 收起讲解' : '🔽 查看讲解'}
        </Text>
      </View>

      {showExplanation && (
        <View className="poem-explanation">
          <View className="explanation-section">
            <Text className="section-label">📖 大意</Text>
            <Text className="section-text">{poem.explanation}</Text>
          </View>
          <View className="explanation-section">
            <Text className="section-label">✨ 赏析</Text>
            <Text className="section-text">{poem.appreciation}</Text>
          </View>
        </View>
      )}

      {/* 背诵提示 */}
      <View className="poem-tip">
        <Text className="tip-icon">💡</Text>
        <Text className="tip-text">试着大声朗读三遍，然后闭上眼睛背一背～</Text>
      </View>

      {/* 操作按钮 */}
      <View className="poem-actions">
        <View className="poem-btn secondary" onClick={onRefresh}>
          <Text>🔄 换一首</Text>
        </View>
        {!completed ? (
          <View className="poem-btn primary" onClick={handleComplete}>
            <Text>✅ 我背完了</Text>
          </View>
        ) : (
          <View className="poem-btn done">
            <Text>🎉 已完成</Text>
          </View>
        )}
      </View>
    </View>
  );
}
