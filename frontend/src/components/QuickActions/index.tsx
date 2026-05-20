import { View, Text } from '@tarojs/components';
import './index.scss';

export interface QuickActionItem {
  label: string;
  icon: string;
  prompt: string;
  color?: string;
}

interface QuickActionsProps {
  actions: QuickActionItem[];
  onAction: (prompt: string) => void;
}

export default function QuickActions({ actions, onAction }: QuickActionsProps) {
  return (
    <View className="quick-actions-bar">
      {actions.map((action, idx) => (
        <View
          key={idx}
          className="quick-action-chip"
          style={action.color ? { backgroundColor: `${action.color}20`, borderColor: `${action.color}30` } : {}}
          onClick={() => onAction(action.prompt)}
        >
          <Text className="chip-icon">{action.icon}</Text>
          <Text className="chip-label" style={action.color ? { color: action.color } : {}}>{action.label}</Text>
        </View>
      ))}
    </View>
  );
}
