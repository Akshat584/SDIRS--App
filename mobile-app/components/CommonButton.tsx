import React from 'react';
import { TouchableOpacity, StyleSheet, Text, ActivityIndicator } from 'react-native';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface CommonButtonProps {
  title: string;
  onPress: () => void;
  type?: 'primary' | 'secondary' | 'emergency';
  loading?: boolean;
  disabled?: boolean;
}

export const CommonButton: React.FC<CommonButtonProps> = ({ 
  title, 
  onPress, 
  type = 'primary', 
  loading = false, 
  disabled = false 
}) => {
  const colorScheme = useColorScheme() ?? 'light';
  const themeColors = Colors[colorScheme];

  const getBackgroundColor = () => {
    if (disabled) return '#cccccc';
    switch (type) {
      case 'emergency': return themeColors.emergency;
      case 'secondary': return 'transparent';
      default: return themeColors.tint;
    }
  };

  return (
    <TouchableOpacity 
      style={[
        styles.button, 
        { backgroundColor: getBackgroundColor() },
        type === 'secondary' && { borderWidth: 1, borderColor: themeColors.tint }
      ]}
      onPress={onPress}
      disabled={disabled || loading}
    >
      {loading ? (
        <ActivityIndicator color="white" />
      ) : (
        <Text style={[
          styles.text, 
          type === 'secondary' && { color: themeColors.tint }
        ]}>
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 54,
  },
  text: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
    letterSpacing: 0.5,
  },
});
