import { useState, useEffect, useCallback } from 'react';
import { View, Text } from '@tarojs/components';
import './index.scss';

interface CelebrationProps {
  visible: boolean;
  points: number;
  onComplete: () => void;
}

export default function Celebration({ visible, points, onComplete }: CelebrationProps) {
  const [phase, setPhase] = useState<'entering' | 'showing' | 'exiting' | 'hidden'>('hidden');

  const startAnimation = useCallback(() => {
    setPhase('entering');
    
    // 进入动画完成后切换到显示状态
    setTimeout(() => {
      setPhase('showing');
    }, 300);

    // 2.5秒后开始退出
    setTimeout(() => {
      setPhase('exiting');
    }, 2500);

    // 3秒后完全隐藏
    setTimeout(() => {
      setPhase('hidden');
      onComplete();
    }, 2900);
  }, [onComplete]);

  useEffect(() => {
    if (visible && phase === 'hidden') {
      startAnimation();
    }
  }, [visible, phase, startAnimation]);

  if (phase === 'hidden') return null;

  return (
    <View className={`celebration-overlay ${phase}`}>
      {/* 彩屑粒子 */}
      <View className="confetti-container">
        {Array.from({ length: 20 }).map((_, i) => (
          <View
            key={i}
            className="confetti"
            style={{
              left: `${5 + (i * 5) % 90}%`,
              animationDelay: `${(i * 0.1) % 0.8}s`,
              animationDuration: `${1.5 + (i % 3) * 0.5}s`,
              backgroundColor: ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98FB98'][i % 6],
            }}
          />
        ))}
      </View>

      {/* 恐龙庆祝 */}
      <View className={`dino-celebration ${phase}`}>
        <View className="dino-bounce">
          <Text className="dino-emoji">🦕</Text>
          <View className="dino-sparkles">
            <Text className="sparkle">✨</Text>
            <Text className="sparkle">✨</Text>
          </View>
        </View>
      </View>

      {/* 积分弹出 */}
      <View className={`points-popup ${phase}`}>
        <View className="points-glow">
          <Text className="points-icon">⭐</Text>
          <Text className="points-value">+{points}</Text>
        </View>
        <Text className="points-label">太棒了！</Text>
      </View>
    </View>
  );
}
