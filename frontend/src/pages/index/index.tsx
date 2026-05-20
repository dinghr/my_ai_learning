import { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import DinoStatus from '../../components/DinoStatus';
import TaskCard from '../../components/TaskCard';
import WishProgress from '../../components/WishProgress';
import Celebration from '../../components/Celebration';
import { getTasks, completeTask, getDailyProgress } from '../../api/task';
import { getFeaturedWish } from '../../api/wish';
import { getPointsSummary } from '../../api/points';
import { Task, DailyProgress } from '../../api/task';
import { Wish } from '../../api/wish';
import { PointsSummary } from '../../api/points';
import './index.scss';

export default function Index() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [progress, setProgress] = useState<DailyProgress | null>(null);
  const [featuredWish, setFeaturedWish] = useState<Wish | null>(null);
  const [pointsSummary, setPointsSummary] = useState<PointsSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'daily' | 'long_term'>('daily');
  const [celebration, setCelebration] = useState<{ visible: boolean; points: number }>({
    visible: false,
    points: 0,
  });
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [tasksData, progressData, wishData, pointsData] = await Promise.all([
        getTasks(activeTab),
        getDailyProgress(),
        getFeaturedWish(),
        getPointsSummary(),
      ]);
      setTasks(tasksData);
      setProgress(progressData);
      setFeaturedWish(wishData);
      setPointsSummary(pointsData);
    } catch (err) {
      console.error('获取数据失败:', err);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCompleteTask = async (taskId: string) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;

      const result = await completeTask(taskId);
      console.log('完成结果:', result);

      // 播放庆祝动画
      setCelebration({ visible: true, points: task.points });

      // 刷新数据
      await fetchData();
    } catch (err) {
      Taro.showToast({ title: err.message || '完成失败', icon: 'none' });
    }
  };

  const handleCelebrationComplete = () => {
    setCelebration({ visible: false, points: 0 });
  };

  const handleGoWishPool = () => {
    Taro.navigateTo({ url: '/pages/wish-pool/index' });
  };

  const filteredTasks = tasks.filter(t => t.task_type === activeTab);

  if (loading) {
    return (
      <View className="page-loading">
        <Text className="loading-text">加载中...</Text>
      </View>
    );
  }

  return (
    <View className="index-page">
      {/* 顶部恐龙状态区 */}
      {progress && pointsSummary && (
        <DinoStatus
          pointsBalance={pointsSummary.balance}
          completedCount={progress.completed}
          totalCount={progress.total}
          pointsToday={progress.points_today}
        />
      )}

      <ScrollView
        className="task-scroll"
        scrollY
        enableFlex
        style={{ flex: 1 }}
      >
        {/* Tab 切换 */}
        <View className="task-tabs">
          <View
            className={`task-tab ${activeTab === 'daily' ? 'active' : ''}`}
            onClick={() => setActiveTab('daily')}
          >
            <Text>每日打卡</Text>
          </View>
          <View
            className={`task-tab ${activeTab === 'long_term' ? 'active' : ''}`}
            onClick={() => setActiveTab('long_term')}
          >
            <Text>长期目标</Text>
          </View>
        </View>

        {/* 任务列表 */}
        <View className="task-list">
          {filteredTasks.length === 0 ? (
            <View className="empty-state">
              <Text className="empty-icon">📝</Text>
              <Text className="empty-text">
                {activeTab === 'daily' ? '还没有每日任务' : '还没有长期目标'}
              </Text>
            </View>
          ) : (
            filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                id={task.id}
                name={task.name}
                icon={task.icon}
                points={task.points}
                category={task.category}
                isCompleted={task.is_completed_today}
                taskType={task.task_type}
                currentValue={task.current_value}
                targetValue={task.target_value}
                unit={task.unit}
                onComplete={handleCompleteTask}
              />
            ))
          )}
        </View>

        {/* 底部间距，给愿望进度条留空间 */}
        <View style={{ height: '140px' }} />
      </ScrollView>

      {/* 底部愿望进度条 */}
      <View className="wish-progress-container">
        {featuredWish ? (
          <WishProgress
            name={featuredWish.name}
            icon={featuredWish.icon}
            pointsRequired={featuredWish.points_required}
            pointsProgress={featuredWish.points_progress}
            onClick={handleGoWishPool}
          />
        ) : (
          <View className="wish-empty" onClick={handleGoWishPool}>
            <Text className="wish-empty-text">🎁 还没有愿望，去许愿池添加吧</Text>
          </View>
        )}
      </View>

      {/* 庆祝动效 */}
      <Celebration
        visible={celebration.visible}
        points={celebration.points}
        onComplete={handleCelebrationComplete}
      />
    </View>
  );
}
