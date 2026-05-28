import { useState, useEffect } from 'react';
import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { generateReading } from '../../api/vocabulary';
import type { ReadingPassage } from '../../api/vocabulary';
import './index.scss';

const THEMES = ['随机', '春天', '夏天', '秋天', '冬天', '亲情', '自然', '校园'];

export default function LiteracyReading() {
  const [passage, setPassage] = useState<ReadingPassage | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentTheme, setCurrentTheme] = useState('随机');

  const loadReading = async (theme?: string) => {
    setLoading(true);
    try {
      const data = await generateReading(theme || currentTheme);
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

  const handleThemeChange = (theme: string) => {
    setCurrentTheme(theme);
    loadReading(theme);
  };

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
          <Text className="loading-text">正在翻阅经典文集...</Text>
        </View>
      </View>
    );
  }

  return (
    <View className="reading-page">
      {/* 主题选择 */}
      <View className="theme-selector">
        {THEMES.map(t => (
          <View
            key={t}
            className={`theme-tag ${currentTheme === t ? 'active' : ''}`}
            onClick={() => handleThemeChange(t)}
          >
            <Text>{t}</Text>
          </View>
        ))}
      </View>

      {/* 标题 */}
      <View className="reading-header">
        <Text className="reading-title">{passage?.title}</Text>
        {passage?.author && (
          <Text className="reading-author">{passage.author}</Text>
        )}
        <Text className="reading-summary">{passage?.summary}</Text>
      </View>

      {/* 正文 */}
      <View className="reading-content">
        {passage?.content.map((item, index) => (
          <View key={index} className="char-block">
            <Text className="char-hz">{item.hz}</Text>
            {item.py && <Text className="char-py">{item.py}</Text>}
          </View>
        ))}
      </View>

      {/* 好词积累 */}
      {passage?.highlight_words && passage.highlight_words.length > 0 && (
        <View className="highlight-words">
          <Text className="highlight-title">✨ 好词积累</Text>
          <View className="highlight-list">
            {passage.highlight_words.map((word, idx) => (
              <View key={idx} className="highlight-tag">
                <Text>{word}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* 操作 */}
      <View className="reading-actions">
        <View className="reading-btn btn-primary" onClick={handleFinish}>
          <Text>✅ 我读完了</Text>
        </View>
        <View className="reading-btn btn-secondary" onClick={() => loadReading()}>
          <Text>🔄 换一篇</Text>
        </View>
        <View className="reading-back" onClick={() => Taro.navigateBack()}>
          <Text>← 返回聊天</Text>
        </View>
      </View>
    </View>
  );
}
