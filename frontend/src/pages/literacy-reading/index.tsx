import { useState, useEffect } from 'react';
import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { generateReading } from '../../api/vocabulary';
import type { ReadingPassage } from '../../api/vocabulary';
import './index.scss';

export default function LiteracyReading() {
  const [passage, setPassage] = useState<ReadingPassage | null>(null);
  const [loading, setLoading] = useState(false);

  const loadReading = async () => {
    setLoading(true);
    try {
      const data = await generateReading();
      setPassage(data);
    } catch (err) {
      Taro.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReading();
  }, []);

  const handleFinish = () => {
    Taro.showToast({ title: '🎉 精读完成！+15⭐', icon: 'success' });
    setTimeout(() => {
      Taro.navigateBack();
    }, 1500);
  };

  if (loading) {
    return (
      <View className="reading-page">
        <View className="reading-loading">
          <Text className="loading-text">正在生成精读短文...</Text>
        </View>
      </View>
    );
  }

  if (!passage) {
    return (
      <View className="reading-page">
        <View className="reading-empty">
          <Text className="empty-text">暂无精读内容</Text>
          <View className="empty-btn" onClick={loadReading}>
            <Text>重新加载</Text>
          </View>
        </View>
      </View>
    );
  }

  return (
    <View className="reading-page">
      {/* 标题 */}
      <View className="reading-header">
        <Text className="reading-title">{passage.title}</Text>
        <Text className="reading-summary">{passage.summary}</Text>
      </View>

      {/* 正文 */}
      <View className="reading-content">
        {passage.content.map((item, index) => (
          <View
            key={index}
            className={`char-block ${item.highlight ? 'highlight' : ''}`}
          >
            <Text className="char-hz">{item.hz}</Text>
            {item.py && <Text className="char-py">{item.py}</Text>}
          </View>
        ))}
      </View>

      {/* 操作 */}
      <View className="reading-actions">
        <View className="reading-btn btn-primary" onClick={handleFinish}>
          <Text>✅ 我读完了</Text>
        </View>
        <View className="reading-btn btn-secondary" onClick={loadReading}>
          <Text>🔄 换一篇</Text>
        </View>
        <View className="reading-back" onClick={() => Taro.navigateBack()}>
          <Text>← 返回聊天</Text>
        </View>
      </View>
    </View>
  );
}
