import { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import ChatMessageBubble from '../../components/ChatMessage';
import ChatInput from '../../components/ChatInput';
import QuickActions from '../../components/QuickActions';
import { sendChatMessage, getQuickReplies } from '../../api/ai';
import { ChatMessage, QuickReply } from '../../api/ai';
import './index.scss';

const WELCOME_MESSAGE: ChatMessage = {
  id: 'welcome',
  student_id: 'demo-student',
  role: 'assistant',
  content: '你好！我是小棘的考古助手 🦕\n\n你可以问我：\n• "教我背一首古诗" 📜\n• "这道数学题怎么做" 🔢\n• "为什么天是蓝色的" ❓\n• "讲一个恐龙的故事" 🦖',
  content_type: 'text',
  session_id: 'welcome',
  created_at: new Date().toISOString(),
};

const DEFAULT_QUICK_REPLIES: QuickReply[] = [
  { label: '背古诗', icon: '📜', prompt: '教我背一首古诗' },
  { label: '数学题', icon: '🔢', prompt: '出一道二年级的数学题' },
  { label: '讲故事', icon: '📖', prompt: '讲一个恐龙的故事' },
  { label: '为什么', icon: '❓', prompt: '为什么天空是蓝色的？' },
];

export default function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [sessionId, setSessionId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [quickReplies, setQuickReplies] = useState<QuickReply[]>(DEFAULT_QUICK_REPLIES);
  const [lastIntent, setLastIntent] = useState<string>('');
  const scrollRef = useRef<any>(null);
  const [poemRefreshing, setPoemRefreshing] = useState<Record<string, boolean>>({});

  // 获取快捷回复
  const fetchQuickReplies = useCallback(async (intent?: string) => {
    try {
      const replies = await getQuickReplies(intent);
      if (replies.length > 0) {
        setQuickReplies(replies);
      }
    } catch (err) {
      console.error('获取快捷回复失败:', err);
    }
  }, []);

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollIntoView({ block: 'end' });
      }
    }, 100);
  }, []);

  const handleSendMessage = async (text: string, isRefresh = false) => {
    if (loading && !isRefresh) return;

    // 添加用户消息到列表
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      student_id: 'demo-student',
      role: 'user',
      content: text,
      content_type: 'text',
      session_id: sessionId || '',
      created_at: new Date().toISOString(),
    };

    if (!isRefresh) {
      setMessages(prev => [...prev, userMsg]);
    }
    setLoading(true);
    scrollToBottom();

    try {
      const res = await sendChatMessage(text, sessionId || undefined);

      // 更新会话ID（首次对话时）
      if (!sessionId && res.message.session_id) {
        setSessionId(res.message.session_id);
      }

      // 更新意图和快捷回复
      if (res.intent) {
        setLastIntent(res.intent);
        fetchQuickReplies(res.intent);
      }

      if (isRefresh) {
        // 替换最后一条AI消息
        setMessages(prev => {
          const filtered = prev.filter(m => m.role !== 'assistant' || m.id === 'welcome');
          return [...filtered, res.message];
        });
      } else {
        // 添加AI回复
        setMessages(prev => [...prev, res.message]);
      }
    } catch (err: any) {
      console.error('AI回复失败:', err);
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        student_id: 'demo-student',
        role: 'assistant',
        content: '哎呀，我的放大镜好像出问题了 🔍\n\n请稍后再试，或者换个问题问我～',
        content_type: 'text',
        session_id: sessionId || '',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMsg]);
      Taro.showToast({ title: '网络开小差了', icon: 'none' });
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const handleQuickAction = (prompt: string) => {
    handleSendMessage(prompt);
  };

  const handleImagePick = () => {
    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        Taro.showToast({ title: '图片已选择（OCR功能开发中）', icon: 'none' });
        handleSendMessage(`[图片] 我上传了一道题，请帮我看看`);
      },
    });
  };

  // 换一首古诗
  const handleRefreshPoem = () => {
    const refreshTexts = [
      '再教我一首古诗',
      '换一首古诗',
      '我想背另一首诗',
    ];
    const text = refreshTexts[Math.floor(Math.random() * refreshTexts.length)];
    handleSendMessage(text, true);
  };

  // 古诗背诵完成
  const handleCompletePoem = () => {
    // 这里可以调用完成任务API来发放积分
    Taro.showToast({ title: '背诵完成！+15⭐', icon: 'success' });
  };

  // 打字机效果
  const [typedContents, setTypedContents] = useState<Record<string, string>>({});

  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.role === 'assistant' && !typedContents[lastMsg.id] && lastMsg.id !== 'welcome') {
      const fullText = lastMsg.content;
      let currentIndex = 0;
      const interval = setInterval(() => {
        currentIndex += 3;
        if (currentIndex >= fullText.length) {
          setTypedContents(prev => ({ ...prev, [lastMsg.id]: fullText }));
          clearInterval(interval);
        } else {
          setTypedContents(prev => ({ ...prev, [lastMsg.id]: fullText.slice(0, currentIndex) }));
        }
      }, 12);
      return () => clearInterval(interval);
    }
  }, [messages]);

  const getDisplayContent = (msg: ChatMessage) => {
    if (msg.id === 'welcome') return msg.content;
    if (msg.role === 'assistant' && typedContents[msg.id] !== undefined) {
      return typedContents[msg.id];
    }
    return msg.content;
  };

  return (
    <View className="ai-chat-page">
      {/* 头部 */}
      <View className="chat-header">
        <View className="header-left">
          <Text className="header-avatar">🦕</Text>
          <View className="header-info">
            <Text className="header-title">考古助手</Text>
            <View className="header-status">
              <View className="status-dot" />
              <Text className="status-text">在线</Text>
            </View>
          </View>
        </View>
        {lastIntent && (
          <View className="header-intent">
            <Text className="intent-text">{lastIntent === 'chat' ? '闲聊中' : '学习中'}</Text>
          </View>
        )}
      </View>

      {/* 消息列表 */}
      <ScrollView
        className="chat-messages"
        scrollY
        enableFlex
        scrollIntoView={`msg-${messages[messages.length - 1]?.id}`}
        style={{ flex: 1 }}
      >
        <View className="messages-container">
          {messages.map((msg, idx) => (
            <View key={msg.id} id={`msg-${msg.id}`}>
              <ChatMessageBubble
                role={msg.role}
                content={getDisplayContent(msg)}
                intent={msg.intent}
                intentConfidence={msg.intent_confidence}
                imageUrl={msg.image_url}
                meta={msg.meta}
                onRefreshPoem={msg.intent === 'poem' ? handleRefreshPoem : undefined}
                onCompletePoem={msg.intent === 'poem' ? handleCompletePoem : undefined}
              />
              {/* 加载指示器 */}
              {idx === messages.length - 1 && msg.role === 'user' && loading && (
                <View className="typing-indicator">
                  <View className="typing-avatar">
                    <Text>🦕</Text>
                  </View>
                  <View className="typing-bubble">
                    <View className="typing-dots">
                      <View className="dot" />
                      <View className="dot" />
                      <View className="dot" />
                    </View>
                  </View>
                </View>
              )}
            </View>
          ))}
        </View>
        <View style={{ height: '20px' }} />
      </ScrollView>

      {/* 快捷操作 */}
      <QuickActions actions={quickReplies} onAction={handleQuickAction} />

      {/* 输入栏 */}
      <ChatInput
        onSend={handleSendMessage}
        onImagePick={handleImagePick}
        loading={loading}
      />
    </View>
  );
}
