import { useState, useEffect, useCallback } from 'react';
import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { getQuizGroup, submitQuizResults } from '../../api/vocabulary';
import type { Character, ReviewResult } from '../../api/vocabulary';
import './index.scss';

interface StackChar extends Character {
  status: 'front' | 'back' | 'know' | 'unknow';
}

export default function LiteracyQuiz() {
  const [groupId, setGroupId] = useState(0);
  const [stack, setStack] = useState<StackChar[]>([]);
  const [loading, setLoading] = useState(false);
  const [isReviewRound, setIsReviewRound] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [resultStats, setResultStats] = useState({ know: 0, unknow: 0 });
  const [animating, setAnimating] = useState(false);

  // 加载检测组
  const loadQuiz = useCallback(async () => {
    setLoading(true);
    try {
      const group = await getQuizGroup();
      if (group.total === 0) {
        Taro.showToast({ title: '暂无生字可检测', icon: 'none' });
        return;
      }
      setGroupId(group.group_id);
      setStack(group.characters.map(c => ({ ...c, status: 'front' })));
      setIsReviewRound(false);
      setShowResult(false);
    } catch (err) {
      Taro.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadQuiz();
  }, [loadQuiz]);

  // 处理卡片操作
  const handleAction = async (action: 'know' | 'unknow' | 'study') => {
    if (animating || stack.length === 0) return;
    setAnimating(true);

    const top = stack[0];

    if (action === 'study') {
      // 翻转
      setStack(prev => prev.map((c, i) => i === 0 ? { ...c, status: 'back' } : c));
      setAnimating(false);
      return;
    }

    // 认识/不认识：先播放动画
    setStack(prev => prev.map((c, i) => i === 0 ? { ...c, status: action } : c));

    // 等待动画完成后移除
    setTimeout(async () => {
      const removed = { ...top, status: action };
      const newStack = stack.slice(1);

      // 提交结果
      const result: ReviewResult = {
        character_id: removed.id,
        result: action,
        group_id: groupId,
        review_round: isReviewRound ? 1 : 0,
      };
      try {
        await submitQuizResults([result]);
      } catch (e) {
        console.error('提交失败', e);
      }

      // 如果不认识且不是复习轮，添加到复习队列
      if (action === 'unknow' && !isReviewRound) {
        newStack.push({ ...removed, status: 'front' });
      }

      setStack(newStack);
      setAnimating(false);

      // 检查是否结束
      if (newStack.length === 0) {
        checkGroupEnd();
      }
    }, 350);
  };

  // 翻转顶部卡片
  const flipCard = () => {
    if (animating || stack.length === 0) return;
    const top = stack[0];
    if (top.status === 'back') {
      setStack(prev => prev.map((c, i) => i === 0 ? { ...c, status: 'front' } : c));
    } else {
      setStack(prev => prev.map((c, i) => i === 0 ? { ...c, status: 'back' } : c));
    }
  };

  // 检查组结束
  const checkGroupEnd = () => {
    // 这里简单处理：显示结果
    // 实际应该从API重新获取统计
    setShowResult(true);
  };

  // 再来一遍（复习轮）
  const retryGroup = async () => {
    // 重新获取本组
    setLoading(true);
    try {
      const group = await getQuizGroup();
      if (group.total === 0) {
        Taro.showToast({ title: '本组已全部掌握！', icon: 'success' });
        return;
      }
      setGroupId(group.group_id);
      setStack(group.characters.map(c => ({ ...c, status: 'front' })));
      setIsReviewRound(true);
      setShowResult(false);
    } catch (err) {
      Taro.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      setLoading(false);
    }
  };

  // 下一组
  const nextGroup = () => {
    loadQuiz();
  };

  // 渲染卡片堆叠
  const renderStack = () => {
    const visible = stack.slice(0, 3);
    return visible.map((char, index) => {
      const isTop = index === 0;
      const isBack = char.status === 'back';
      const isKnow = char.status === 'know';
      const isUnknow = char.status === 'unknow';

      let cardClass = 'quiz-card';
      if (isKnow) cardClass += ' swipe-left';
      if (isUnknow) cardClass += ' swipe-right';
      if (isBack) cardClass += ' flipped';

      return (
        <View
          key={char.id}
          className={cardClass}
          style={{ zIndex: 10 - index }}
          onClick={isTop && !animating ? flipCard : undefined}
        >
          {/* 正面 - 田字格 */}
          <View className="card-front">
            <View className="tianzig">
              <View className="tianzig-line-h" />
              <View className="tianzig-line-v" />
              <View className="tianzig-dash-h" />
              <View className="tianzig-dash-v" />
              <Text className="tianzig-char">{char.character}</Text>
            </View>
            {isTop && (
              <View className="card-actions">
                <View className="card-btn btn-know" onClick={() => handleAction('know')}>
                  <Text>✓ 认识</Text>
                </View>
                <View className="card-btn btn-study" onClick={() => handleAction('study')}>
                  <Text>🔄 再学</Text>
                </View>
                <View className="card-btn btn-unknow" onClick={() => handleAction('unknow')}>
                  <Text>✗ 不会</Text>
                </View>
              </View>
            )}
          </View>

          {/* 背面 - 详情 */}
          <View className="card-back">
            <Text className="card-pinyin">{char.pinyin}</Text>
            <Text className="card-radical">{char.radical}</Text>
            <View className="card-words">
              {char.words?.map((w, i) => (
                <Text key={i} className="word-tag">{w}</Text>
              ))}
            </View>
            <Text className="card-example">「{char.example}」</Text>
            <View className="card-brainstorm">
              <Text className="brainstorm-title">💡 同偏旁</Text>
              <View className="brainstorm-chars">
                {char.brainstorm?.map((b, i) => (
                  <Text key={i} className="brainstorm-char">{b}</Text>
                ))}
              </View>
            </View>
            <Text className="flip-hint">点击翻回</Text>
          </View>
        </View>
      );
    });
  };

  if (loading && stack.length === 0) {
    return (
      <View className="quiz-page">
        <View className="quiz-loading">
          <Text className="loading-text">加载中...</Text>
        </View>
      </View>
    );
  }

  if (showResult) {
    return (
      <View className="quiz-page">
        <View className="result-card">
          <Text className="result-title">🎉 检测完成</Text>
          <View className="result-stats">
            <View className="result-stat stat-know">
              <Text className="stat-num">{resultStats.know}</Text>
              <Text className="stat-label">认识</Text>
            </View>
            <View className="result-stat stat-unknow">
              <Text className="stat-num">{resultStats.unknow}</Text>
              <Text className="stat-label">不认识</Text>
            </View>
          </View>
          <View className="result-actions">
            <View className="result-btn btn-primary" onClick={retryGroup}>
              <Text>再来一遍</Text>
            </View>
            <View className="result-btn btn-secondary" onClick={nextGroup}>
              <Text>下一组</Text>
            </View>
          </View>
          <View className="result-back" onClick={() => Taro.navigateBack()}>
            <Text>← 返回聊天</Text>
          </View>
        </View>
      </View>
    );
  }

  return (
    <View className="quiz-page">
      {/* 顶部进度 */}
      <View className="quiz-header">
        <Text className="group-title">
          {isReviewRound ? '🔁 复习轮' : `📚 第 ${groupId} 组`}
        </Text>
        <Text className="progress-text">
          剩余 {stack.length} 字
        </Text>
      </View>

      {/* 卡片堆叠 */}
      <View className="card-stack">
        {renderStack()}
      </View>

      {/* 手势提示 */}
      <View className="gesture-hint">
        <Text className="hint-left">👈 认识</Text>
        <Text className="hint-center">🔄 再学一下</Text>
        <Text className="hint-right">不认识 👉</Text>
      </View>
    </View>
  );
}
