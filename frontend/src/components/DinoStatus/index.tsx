import { View, Text } from '@tarojs/components';
import Spinosaurus from '../Spinosaurus';
import './index.scss';

interface DinoStatusProps {
  pointsBalance: number;
  completedCount: number;
  totalCount: number;
  pointsToday: number;
}

export default function DinoStatus({
  pointsBalance,
  completedCount,
  totalCount,
  pointsToday,
}: DinoStatusProps) {
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <View className="dino-status">
      {/* 背景装饰 */}
      <View className="status-bg-decoration">
        <View className="bg-circle c1" />
        <View className="bg-circle c2" />
        <View className="bg-circle c3" />
      </View>

      <View className="status-content">
        {/* 左侧恐龙 */}
        <View className="dino-area">
          <Spinosaurus
            level={Math.floor(pointsBalance / 100) + 1}
            name="小棘"
            mood={completedCount === totalCount && totalCount > 0 ? 'happy' : 'normal'}
          />
          {completedCount === totalCount && totalCount > 0 && (
            <Text className="dino-bubble">全部完成！🎉</Text>
          )}
        </View>

        {/* 右侧积分信息 */}
        <View className="stats-area">
          <View className="points-display">
            <Text className="points-label">积分</Text>
            <Text className="points-total">{pointsBalance}</Text>
            {pointsToday > 0 && (
              <Text className="points-today">+{pointsToday} 今日</Text>
            )}
          </View>

          <View className="progress-display">
            <View className="progress-header">
              <Text className="progress-label">今日打卡</Text>
              <Text className="progress-value">{completedCount}/{totalCount}</Text>
            </View>
            <View className="progress-track">
              <View
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </View>
          </View>
        </View>
      </View>
    </View>
  );
}
