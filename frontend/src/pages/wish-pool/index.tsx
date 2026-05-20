import { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, Input } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { getWishes, createWish, addWishProgress, completeWish } from '../../api/wish';
import { getPointsSummary } from '../../api/points';
import { Wish } from '../../api/wish';
import './index.scss';

export default function WishPool() {
  const [wishes, setWishes] = useState<Wish[]>([]);
  const [pointsBalance, setPointsBalance] = useState(0);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newWishName, setNewWishName] = useState('');
  const [newWishPoints, setNewWishPoints] = useState('');
  const [selectedIcon, setSelectedIcon] = useState('🎁');
  const [loading, setLoading] = useState(true);

  const icons = ['🎁', '🦕', '🎮', '📖', '🎬', '🧺', '🏕️', '🧸', '🍦', '🎯'];

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [wishesData, pointsData] = await Promise.all([
        getWishes(),
        getPointsSummary(),
      ]);
      setWishes(wishesData);
      setPointsBalance(pointsData.balance);
    } catch (err) {
      console.error('获取数据失败:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAddWish = async () => {
    if (!newWishName.trim()) {
      Taro.showToast({ title: '请输入愿望名称', icon: 'none' });
      return;
    }
    const points = parseInt(newWishPoints) || 100;
    if (points < 10) {
      Taro.showToast({ title: '积分至少10', icon: 'none' });
      return;
    }

    try {
      await createWish({
        name: newWishName.trim(),
        icon: selectedIcon,
        points_required: points,
      });
      Taro.showToast({ title: '愿望添加成功！', icon: 'success' });
      setNewWishName('');
      setNewWishPoints('');
      setSelectedIcon('🎁');
      setShowAddForm(false);
      await fetchData();
    } catch (err) {
      Taro.showToast({ title: '添加失败', icon: 'none' });
    }
  };

  const handleInvest = async (wishId: string, amount: number) => {
    if (amount <= 0) return;
    if (amount > pointsBalance) {
      Taro.showToast({ title: '积分不足', icon: 'none' });
      return;
    }

    try {
      await addWishProgress(wishId, amount);
      Taro.showToast({ title: `投入 ${amount} 积分`, icon: 'success' });
      await fetchData();
    } catch (err) {
      Taro.showToast({ title: '投入失败', icon: 'none' });
    }
  };

  const handleComplete = async (wishId: string) => {
    try {
      await completeWish(wishId);
      Taro.showToast({ title: '愿望达成！🎉', icon: 'success' });
      await fetchData();
    } catch (err) {
      Taro.showToast({ title: '操作失败', icon: 'none' });
    }
  };

  if (loading) {
    return (
      <View className="page-loading">
        <Text className="loading-text">加载中...</Text>
      </View>
    );
  }

  return (
    <View className="wish-pool-page">
      {/* 头部 */}
      <View className="wish-header">
        <View className="header-top">
          <Text className="header-title">🎁 愿望池</Text>
          <View className="header-points">
            <Text className="points-icon">⭐</Text>
            <Text className="points-value">{pointsBalance}</Text>
          </View>
        </View>
        <Text className="header-subtitle">用积分兑换心中的小愿望</Text>
      </View>

      <ScrollView className="wish-scroll" scrollY>
        {/* 愿望列表 */}
        <View className="wish-list">
          {wishes.length === 0 ? (
            <View className="empty-wishes">
              <Text className="empty-icon">🌟</Text>
              <Text className="empty-text">还没有愿望，添加一个吧！</Text>
            </View>
          ) : (
            wishes.map(wish => {
              const percentage = Math.min(100, Math.round((wish.points_progress / wish.points_required) * 100));
              const isCompleted = wish.status === 'completed';
              const canComplete = !isCompleted && wish.points_progress >= wish.points_required;

              return (
                <View key={wish.id} className={`wish-card ${isCompleted ? 'completed' : ''}`}>
                  <View className="wish-card-header">
                    <View className="wish-card-left">
                      <Text className="wish-card-icon">{wish.icon}</Text>
                      <View className="wish-card-info">
                        <Text className="wish-card-name">{wish.name}</Text>
                        <Text className="wish-card-progress">
                          {wish.points_progress} / {wish.points_required} ⭐
                        </Text>
                      </View>
                    </View>
                    <View className="wish-card-status">
                      {isCompleted ? (
                        <Text className="status-completed">✓ 已达成</Text>
                      ) : (
                        <Text className="status-percent">{percentage}%</Text>
                      )}
                    </View>
                  </View>

                  {/* 进度条 */}
                  <View className="wish-card-bar">
                    <View className="wish-card-track">
                      <View
                        className={`wish-card-fill ${isCompleted ? 'complete' : ''}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </View>
                  </View>

                  {/* 操作按钮 */}
                  {!isCompleted && (
                    <View className="wish-card-actions">
                      {canComplete ? (
                        <View
                          className="action-btn complete-btn"
                          onClick={() => handleComplete(wish.id)}
                        >
                          <Text>🎉 兑换愿望</Text>
                        </View>
                      ) : (
                        <>
                          <View
                            className="action-btn invest-btn"
                            onClick={() => handleInvest(wish.id, 10)}
                          >
                            <Text>+10 ⭐</Text>
                          </View>
                          <View
                            className="action-btn invest-btn"
                            onClick={() => handleInvest(wish.id, 50)}
                          >
                            <Text>+50 ⭐</Text>
                          </View>
                          <View
                            className="action-btn invest-btn invest-all"
                            onClick={() => {
                              const invest = Math.min(pointsBalance, wish.points_required - wish.points_progress);
                              if (invest > 0) handleInvest(wish.id, invest);
                            }}
                          >
                            <Text>全部投入</Text>
                          </View>
                        </>
                      )}
                    </View>
                  )}
                </View>
              );
            })
          )}
        </View>

        {/* 添加愿望按钮 */}
        {!showAddForm && (
          <View className="add-wish-trigger" onClick={() => setShowAddForm(true)}>
            <Text className="add-wish-icon">+</Text>
            <Text className="add-wish-text">添加新愿望</Text>
          </View>
        )}

        {/* 添加愿望表单 */}
        {showAddForm && (
          <View className="add-wish-form">
            <Text className="form-title">添加新愿望</Text>

            {/* 图标选择 */}
            <View className="icon-selector">
              {icons.map(icon => (
                <View
                  key={icon}
                  className={`icon-option ${selectedIcon === icon ? 'selected' : ''}`}
                  onClick={() => setSelectedIcon(icon)}
                >
                  <Text>{icon}</Text>
                </View>
              ))}
            </View>

            <Input
              className="form-input"
              placeholder="愿望名称（如：去恐龙博物馆）"
              value={newWishName}
              onInput={(e) => setNewWishName(e.detail.value)}
            />

            <Input
              className="form-input"
              placeholder="需要多少积分（如：200）"
              type="number"
              value={newWishPoints}
              onInput={(e) => setNewWishPoints(e.detail.value)}
            />

            <View className="form-actions">
              <View className="form-btn cancel" onClick={() => setShowAddForm(false)}>
                <Text>取消</Text>
              </View>
              <View className="form-btn confirm" onClick={handleAddWish}>
                <Text>添加</Text>
              </View>
            </View>
          </View>
        )}

        <View style={{ height: '40px' }} />
      </ScrollView>
    </View>
  );
}
