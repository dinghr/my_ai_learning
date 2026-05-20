import { View, Text } from '@tarojs/components';
import './index.scss';

interface WishProgressProps {
  name: string;
  icon: string;
  pointsRequired: number;
  pointsProgress: number;
  onClick?: () => void;
}

export default function WishProgress({
  name,
  icon,
  pointsRequired,
  pointsProgress,
  onClick,
}: WishProgressProps) {
  const percentage = Math.min(100, Math.round((pointsProgress / pointsRequired) * 100));
  const remaining = Math.max(0, pointsRequired - pointsProgress);

  return (
    <View className="wish-progress-bar" onClick={onClick}>
      <View className="wish-progress-content">
        <View className="wish-progress-info">
          <Text className="wish-icon">{icon}</Text>
          <Text className="wish-name">{name}</Text>
          <Text className="wish-remaining">还差 {remaining}⭐</Text>
        </View>
        <Text className="wish-percentage">{percentage}%</Text>
      </View>
      <View className="wish-progress-track">
        <View
          className="wish-progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </View>
    </View>
  );
}
