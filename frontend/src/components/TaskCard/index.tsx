import { useState } from 'react';
import { View, Text } from '@tarojs/components';
import './index.scss';

interface TaskCardProps {
  id: string;
  name: string;
  icon: string;
  points: number;
  category: string;
  isCompleted: boolean;
  taskType: 'daily' | 'long_term';
  currentValue?: number;
  targetValue?: number;
  unit?: string;
  onComplete: (taskId: string) => void;
}

export default function TaskCard({
  id,
  name,
  icon,
  points,
  category,
  isCompleted,
  taskType,
  currentValue,
  targetValue,
  unit,
  onComplete,
}: TaskCardProps) {
  const [pressing, setPressing] = useState(false);

  const categoryLabels: Record<string, string> = {
    sport: '运动',
    labor: '劳动',
    writing: '练字',
    reading: '阅读',
    custom: '自定义',
  };

  const handleClick = () => {
    if (isCompleted) return;
    onComplete(id);
  };

  const progress = targetValue && targetValue > 0
    ? Math.min(100, Math.round((currentValue || 0) / targetValue * 100))
    : 0;

  return (
    <View
      className={`task-card ${isCompleted ? 'completed' : ''} ${pressing ? 'pressing' : ''}`}
      onClick={handleClick}
      onTouchStart={() => setPressing(true)}
      onTouchEnd={() => setPressing(false)}
    >
      {/* 完成标记 */}
      {isCompleted && (
        <View className="completed-badge">
          <Text className="completed-icon">✓</Text>
        </View>
      )}

      <View className="task-left">
        <View className={`task-icon ${category}`}>
          <Text className="task-icon-text">{icon}</Text>
        </View>
        <View className="task-info">
          <Text className="task-name">{name}</Text>
          <View className="task-meta">
            <Text className="task-category">{categoryLabels[category] || category}</Text>
            <Text className="task-type">{taskType === 'daily' ? '每日' : '长期'}</Text>
          </View>
          {taskType === 'long_term' && targetValue && (
            <View className="task-progress-bar">
              <View className="task-progress-fill" style={{ width: `${progress}%` }} />
              <Text className="task-progress-text">{currentValue || 0}/{targetValue}{unit}</Text>
            </View>
          )}
        </View>
      </View>

      <View className="task-right">
        <View className="task-points">
          <Text className="points-icon">⭐</Text>
          <Text className="points-value">+{points}</Text>
        </View>
      </View>
    </View>
  );
}
