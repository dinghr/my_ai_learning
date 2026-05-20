import { View, Text, Image } from '@tarojs/components';
import PoemCard, { PoemData } from '../PoemCard';
import './index.scss';

export interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  intentConfidence?: number;
  imageUrl?: string;
  meta?: Record<string, any>;
  onRefreshPoem?: () => void;
  onCompletePoem?: () => void;
}

const INTENT_LABELS: Record<string, { label: string; icon: string; color: string }> = {
  wrong_question: { label: '错题解析', icon: '✏️', color: '#FF8A65' },
  poem: { label: '古诗学习', icon: '📜', color: '#CE93D8' },
  math: { label: '数学辅导', icon: '🔢', color: '#90CAF9' },
  reading: { label: '阅读推荐', icon: '📖', color: '#4A7C59' },
  writing: { label: '写作指导', icon: '✍️', color: '#A1887F' },
  english: { label: '英语学习', icon: '🔤', color: '#FFD700' },
  general: { label: '知识百科', icon: '🔍', color: '#45B7D1' },
  chat: { label: '闲聊', icon: '💬', color: '#B0A080' },
};

export default function ChatMessageBubble({
  role,
  content,
  intent,
  intentConfidence,
  imageUrl,
  meta,
  onRefreshPoem,
  onCompletePoem,
}: ChatMessageProps) {
  const isUser = role === 'user';
  const intentInfo = intent ? INTENT_LABELS[intent] || INTENT_LABELS.chat : null;

  // 解析古诗数据
  const poemData: PoemData | undefined = meta?.poem;
  const isPoem = intent === 'poem' && poemData;

  // 简单的Markdown-like解析：分段 + 加粗
  const paragraphs = content.split('\n').filter(p => p.trim());

  return (
    <View className="chat-message-wrapper">
      <View className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
        <View className="message-avatar">
          <Text className="avatar-icon">{isUser ? '👦' : '🦕'}</Text>
        </View>
        <View className="message-content-wrapper">
          {/* 意图标签 */}
          {!isUser && intentInfo && (
            <View className="intent-tag" style={{ backgroundColor: `${intentInfo.color}20`, borderColor: `${intentInfo.color}40` }}>
              <Text style={{ color: intentInfo.color }}>{intentInfo.icon} {intentInfo.label}</Text>
              {intentConfidence && intentConfidence > 0 && (
                <Text className="intent-confidence" style={{ color: intentInfo.color }}>{intentConfidence}%</Text>
              )}
            </View>
          )}

          {/* 图片 */}
          {imageUrl && (
            <Image className="message-image" src={imageUrl} mode="widthFix" />
          )}

          {/* 文本内容 */}
          <View className={`message-bubble ${isUser ? 'user-bubble' : 'ai-bubble'}`}>
            {paragraphs.map((para, idx) => {
              const parts = para.split(/(\*\*.*?\*\*)/g);
              return (
                <Text key={idx} className="message-paragraph">
                  {parts.map((part, pidx) => {
                    if (part.startsWith('**') && part.endsWith('**')) {
                      return <Text key={pidx} className="message-bold">{part.slice(2, -2)}</Text>;
                    }
                    return <Text key={pidx}>{part}</Text>;
                  })}
                </Text>
              );
            })}
          </View>
        </View>
      </View>

      {/* 古诗卡片 — 在消息下方展示 */}
      {isPoem && poemData && (
        <PoemCard
          poem={poemData}
          onRefresh={onRefreshPoem}
          onComplete={onCompletePoem}
        />
      )}
    </View>
  );
}
