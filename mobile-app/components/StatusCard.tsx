import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { ThemedText } from '@/components/themed-text';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface StatusCardProps {
  title: string;
  status: string;
  type?: 'emergency' | 'warning' | 'success' | 'info';
  children?: React.ReactNode;
  style?: ViewStyle;
}

export const StatusCard: React.FC<StatusCardProps> = ({ 
  title, 
  status, 
  type = 'info', 
  children,
  style 
}) => {
  const colorScheme = useColorScheme() ?? 'light';
  const themeColors = Colors[colorScheme];

  const getStatusColor = () => {
    switch (type) {
      case 'emergency': return themeColors.emergency;
      case 'warning': return themeColors.warning;
      case 'success': return themeColors.success;
      default: return themeColors.info;
    }
  };

  return (
    <View style={[styles.card, { borderColor: getStatusColor() }, style]}>
      <View style={styles.header}>
        <ThemedText type="subtitle">{title}</ThemedText>
        <View style={[styles.badge, { backgroundColor: getStatusColor() }]}>
          <ThemedText style={styles.badgeText}>{status}</ThemedText>
        </View>
      </View>
      {children && <View style={styles.content}>{children}</View>}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    marginBottom: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  content: {
    marginTop: 8,
  },
});
