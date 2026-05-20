import { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { getCurrentStudent } from '../../api/student';
import { getPointsSummary, getPointsRecords, PointsSummary, PointsRecord } from '../../api/points';
import { Student } from '../../api/student';
import './index.scss';

export default function Profile() {
  const [student, setStudent] = useState<Student | null>(null);
  const [pointsSummary, setPointsSummary] = useState<PointsSummary | null>(null);
  const [pointsRecords, setPointsRecords] = useState<PointsRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<'overview' | 'history'>('overview');

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [studentData, summaryData, recordsData] = await Promise.all([
        getCurrentStudent(),
        getPointsSummary(),
        getPointsRecords(),
      ]);
      setStudent(studentData);
      setPointsSummary(summaryData);
      setPointsRecords(recordsData.slice(0, 20));
    } catch (err) {
      console.error('获取数据失败:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGoWishPool = () => {
    Taro.navigateTo({ url: '/pages/wish-pool/index' });
  };

  if (loading) {
    return (
      <View className="page-loading">
        <Text className="loading-text">加载中...</Text>
      </View>
    );
  }

  return (
    <View className="profile-page">
      {/* 顶部用户信息 */}
      <View className="profile-header">
        <View className="user-info">
          <View className="user-avatar">
            <Text className="avatar-emoji">🦕</Text>
          </View>
          <View className="user-details">
            <Text className="user-name">{student?.name || '小朋友'}</Text>
            <Text className="user-nickname">
              {student?.nickname ? `${student.nickname} · ` : ''}
              {student?.grade || '未知年级'}
            </Text>
          </View>
          <View className="user-level">
            <Text className="level-badge">Lv.{Math.floor((pointsSummary?.balance || 0) / 100) + 1}</Text>
          </View>
        </View>
      </View>

      <ScrollView className="profile-scroll" scrollY>
        {/* 积分总览卡片 */}
        {pointsSummary && (
          <View className="points-overview">
            <View className="points-card">
              <View className="points-main">
                <Text className="points-label">积分余额</Text>
                <Text className="points-balance">{pointsSummary.balance}</Text>
              </View>
              <View className="points-stats">
                <View className="points-stat">
                  <Text className="stat-value">{pointsSummary.total_earned}</Text>
                  <Text className="stat-label">累计获得</Text>
                </View>
                <View className="points-divider" />
                <View className="points-stat">
                  <Text className="stat-value">{pointsSummary.total_spent}</Text>
                  <Text className="stat-label">累计消耗</Text>
                </View>
              </View>
            </View>
          </View>
        )}

        {/* Tab切换 */}
        <View className="section-tabs">
          <View
            className={`section-tab ${activeSection === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveSection('overview')}
          >
            <Text>成长概览</Text>
          </View>
          <View
            className={`section-tab ${activeSection === 'history' ? 'active' : ''}`}
            onClick={() => setActiveSection('history')}
          >
            <Text>积分明细</Text>
          </View>
        </View>

        {/* 成长概览 */}
        {activeSection === 'overview' && (
          <View className="overview-section">
            {/* 快捷入口 */}
            <View className="quick-actions">
              <View className="quick-action" onClick={handleGoWishPool}>
                <View className="quick-icon" style={{ background: 'linear-gradient(135deg, #FFD700, #FFA500)' }}>
                  <Text>🎁</Text>
                </View>
                <Text className="quick-text">愿望池</Text>
              </View>
              <View className="quick-action">
                <View className="quick-icon" style={{ background: 'linear-gradient(135deg, #90CAF9, #64B5F6)' }}>
                  <Text>📚</Text>
                </View>
                <Text className="quick-text">错题本</Text>
              </View>
              <View className="quick-action">
                <View className="quick-icon" style={{ background: 'linear-gradient(135deg, #CE93D8, #BA68C8)' }}>
                  <Text>🏆</Text>
                </View>
                <Text className="quick-text">成就</Text>
              </View>
            </View>

            {/* 成长数据 */}
            <View className="growth-stats">
              <Text className="section-title">成长数据</Text>
              <View className="growth-grid">
                <View className="growth-item">
                  <Text className="growth-value">{Math.floor((pointsSummary?.balance || 0) / 100) + 1}</Text>
                  <Text className="growth-label">恐龙等级</Text>
                </View>
                <View className="growth-item">
                  <Text className="growth-value">{pointsRecords.filter(r => r.points > 0).length}</Text>
                  <Text className="growth-label">打卡次数</Text>
                </View>
                <View className="growth-item">
                  <Text className="growth-value">{pointsRecords.filter(r => r.source_type === 'wish').length}</Text>
                  <Text className="growth-label">愿望投入</Text>
                </View>
              </View>
            </View>
          </View>
        )}

        {/* 积分明细 */}
        {activeSection === 'history' && (
          <View className="history-section">
            {pointsRecords.length === 0 ? (
              <View className="empty-history">
                <Text className="empty-icon">📋</Text>
                <Text className="empty-text">还没有积分记录</Text>
              </View>
            ) : (
              <View className="records-list">
                {pointsRecords.map(record => (
                  <View key={record.id} className="record-item">
                    <View className="record-left">
                      <View className={`record-badge ${record.points > 0 ? 'earn' : 'spend'}`}>
                        <Text>{record.points > 0 ? '+' : ''}{record.points}</Text>
                      </View>
                      <View className="record-info">
                        <Text className="record-desc">{record.description || '积分变动'}</Text>
                        <Text className="record-type">
                          {record.source_type === 'task' ? '📝 任务' :
                           record.source_type === 'wish' ? '🎁 愿望' :
                           record.source_type === 'manual' ? '⚙️ 手动' : '其他'}
                        </Text>
                      </View>
                    </View>
                    <View className="record-right">
                      <Text className="record-balance">余额 {record.balance}</Text>
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        <View style={{ height: '40px' }} />
      </ScrollView>
    </View>
  );
}
