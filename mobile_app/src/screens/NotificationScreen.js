import React, { useEffect, useState } from 'react';
import {
  View,
  ScrollView,
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { useTheme } from '../context/ThemeContext';
import notificationsService from '../services/notifications';

const NotificationScreen = () => {
  const { colors, isDarkMode } = useTheme();
  const dynamicStyles = getDynamicStyles(colors);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationsService.getNotifications(50, 0, false);
      if (response.success) {
        setNotifications(response.data || []);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
      Alert.alert('Error', 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchNotifications();
    setRefreshing(false);
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationsService.markAsRead(notificationId);
      await fetchNotifications();
    } catch (error) {
      Alert.alert('Error', 'Failed to mark as read');
    }
  };

  const handleDelete = async (notificationId) => {
    try {
      await notificationsService.deleteNotification(notificationId);
      await fetchNotifications();
      Alert.alert('Success', 'Notification deleted');
    } catch (error) {
      Alert.alert('Error', 'Failed to delete notification');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsService.markAllAsRead();
      await fetchNotifications();
      Alert.alert('Success', 'All notifications marked as read');
    } catch (error) {
      Alert.alert('Error', 'Failed to mark all as read');
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'attendance':
        return 'assignment-ind';
      case 'project':
        return 'assignment';
      case 'staff':
        return 'people';
      case 'system':
        return 'settings';
      default:
        return 'notifications';
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'attendance':
        return colors.primary;
      case 'project':
        return colors.secondary;
      case 'staff':
        return colors.icon.success;
      case 'system':
        return colors.icon.warning;
      default:
        return colors.text.secondary;
    }
  };

  return (
    <View style={dynamicStyles.container}>
      <View style={dynamicStyles.header}>
        <Text style={dynamicStyles.headerTitle}>Notifications</Text>
        {notifications.length > 0 && (
          <TouchableOpacity
            style={dynamicStyles.markAllButton}
            onPress={handleMarkAllAsRead}
          >
            <Text style={dynamicStyles.markAllButtonText}>Mark All Read</Text>
          </TouchableOpacity>
        )}
      </View>

      {loading && !refreshing ? (
        <View style={dynamicStyles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : notifications.length > 0 ? (
        <ScrollView
          style={dynamicStyles.scrollView}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {notifications.map((notification) => (
            <View
              key={notification.id}
              style={[
                dynamicStyles.notificationItem,
                !notification.isRead && dynamicStyles.unreadNotification,
              ]}
            >
              <View
                style={[
                  dynamicStyles.iconContainer,
                  {
                    backgroundColor: getNotificationColor(notification.type) + '20',
                  },
                ]}
              >
                <MaterialIcons
                  name={getNotificationIcon(notification.type)}
                  size={24}
                  color={getNotificationColor(notification.type)}
                />
              </View>

              <View style={dynamicStyles.contentContainer}>
                <Text style={dynamicStyles.title}>{notification.title}</Text>
                <Text style={dynamicStyles.message} numberOfLines={2}>
                  {notification.message}
                </Text>
                <Text style={dynamicStyles.timestamp}>
                  {new Date(notification.createdAt).toLocaleString()}
                </Text>
              </View>

              <View style={dynamicStyles.actionsContainer}>
                {!notification.isRead && (
                  <TouchableOpacity
                    style={dynamicStyles.actionButton}
                    onPress={() => handleMarkAsRead(notification.id)}
                  >
                    <MaterialIcons name="done" size={20} color={colors.icon.success} />
                  </TouchableOpacity>
                )}
                <TouchableOpacity
                  style={dynamicStyles.actionButton}
                  onPress={() => handleDelete(notification.id)}
                >
                  <MaterialIcons name="delete" size={20} color={colors.icon.danger} />
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </ScrollView>
      ) : (
        <View style={dynamicStyles.emptyContainer}>
          <MaterialIcons name="notifications-none" size={48} color={colors.text.tertiary} />
          <Text style={dynamicStyles.emptyText}>No notifications</Text>
        </View>
      )}
    </View>
  );
};

const getDynamicStyles = (colors) => {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background.secondary,
    },
    header: {
      backgroundColor: colors.background.primary,
      paddingHorizontal: GlassTokens.spacing.lg,
      paddingVertical: GlassTokens.spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: colors.border.light,
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    headerTitle: {
      ...GlobalStyles.title,
      color: colors.text.primary,
    },
    markAllButton: {
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.xs,
      backgroundColor: colors.primary,
      borderRadius: GlassTokens.radius.sm,
      shadowColor: colors.primary,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.2,
      shadowRadius: 8,
      elevation: 4,
    },
    markAllButtonText: {
      ...GlobalStyles.buttonText,
      fontSize: 12,
    },
    scrollView: {
      flex: 1,
    },
    notificationItem: {
      flexDirection: 'row',
      padding: GlassTokens.spacing.md,
      marginHorizontal: GlassTokens.spacing.sm,
      marginVertical: GlassTokens.spacing.xs,
      backgroundColor: colors.background.tertiary,
      borderRadius: GlassTokens.radius.md,
      borderWidth: 1,
      borderColor: colors.border.glass,
      alignItems: 'flex-start',
    },
    unreadNotification: {
      backgroundColor: colors.primaryLight,
      borderLeftWidth: 4,
      borderLeftColor: colors.primary,
    },
    iconContainer: {
      width: 48,
      height: 48,
      borderRadius: 24,
      justifyContent: 'center',
      alignItems: 'center',
      marginRight: GlassTokens.spacing.md,
    },
    contentContainer: {
      flex: 1,
      marginRight: GlassTokens.spacing.sm,
    },
    title: {
      ...GlobalStyles.body,
      fontWeight: '600',
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.xs,
    },
    message: {
      ...GlobalStyles.caption,
      marginBottom: GlassTokens.spacing.xs,
      lineHeight: 18,
    },
    timestamp: {
      ...GlobalStyles.caption,
      color: colors.text.tertiary,
    },
    actionsContainer: {
      flexDirection: 'row',
      gap: GlassTokens.spacing.sm,
    },
    actionButton: {
      padding: GlassTokens.spacing.sm,
      borderRadius: GlassTokens.radius.sm,
      backgroundColor: colors.background.tertiary,
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
    },
    emptyContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
    },
    emptyText: {
      ...GlobalStyles.body,
      marginTop: GlassTokens.spacing.lg,
      color: colors.text.secondary,
    },
  });
};

const styles = StyleSheet.create({
  // Placeholder - will be replaced with getDynamicStyles
  container: { flex: 1 },
});

export default NotificationScreen;
