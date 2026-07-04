import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

import { API_BASE_URL } from './api';

const notificationAPI = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add JWT token to requests
notificationAPI.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const notificationsService = {
  // Get all notifications
  getNotifications: async (limit = 20, offset = 0, unreadOnly = false) => {
    try {
      const response = await notificationAPI.get('/api/notifications', {
        params: {
          limit,
          offset,
          unread_only: unreadOnly,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      throw error;
    }
  },

  // Get unread count
  getUnreadCount: async () => {
    try {
      const response = await notificationAPI.get('/api/notifications/unread-count');
      return response.data;
    } catch (error) {
      console.error('Error fetching unread count:', error);
      throw error;
    }
  },

  // Mark as read
  markAsRead: async (notificationId) => {
    try {
      const response = await notificationAPI.put(
        `/api/notifications/${notificationId}/read`
      );
      return response.data;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  },

  // Mark all as read
  markAllAsRead: async () => {
    try {
      const response = await notificationAPI.put(
        '/api/notifications/mark-all-read'
      );
      return response.data;
    } catch (error) {
      console.error('Error marking all as read:', error);
      throw error;
    }
  },

  // Delete notification
  deleteNotification: async (notificationId) => {
    try {
      const response = await notificationAPI.delete(
        `/api/notifications/${notificationId}`
      );
      return response.data;
    } catch (error) {
      console.error('Error deleting notification:', error);
      throw error;
    }
  },

  // Clear all
  clearAll: async () => {
    try {
      const response = await notificationAPI.delete(
        '/api/notifications/clear-all'
      );
      return response.data;
    } catch (error) {
      console.error('Error clearing notifications:', error);
      throw error;
    }
  },

  // Register FCM token
  registerFCMToken: async (fcmToken) => {
    try {
      const response = await notificationAPI.post(
        '/api/notifications/register-fcm',
        { fcm_token: fcmToken }
      );
      return response.data;
    } catch (error) {
      console.error('Error registering FCM token:', error);
      throw error;
    }
  },
};

export default notificationsService;
