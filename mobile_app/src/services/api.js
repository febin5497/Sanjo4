import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

const { apiBaseUrl, apiTimeout } = Constants.expoConfig?.extra || {};
export const API_BASE_URL = apiBaseUrl || 'http://192.168.1.92:5000';

// Callback for session expiry - set by AuthContext
let onSessionExpired = null;
export const setOnSessionExpired = (callback) => {
  onSessionExpired = callback;
};

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: apiTimeout || 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.log('Error retrieving token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await SecureStore.deleteItemAsync('auth_token');
      await SecureStore.deleteItemAsync('staff_id');
      await SecureStore.deleteItemAsync('user_data');
      await SecureStore.deleteItemAsync('user_role');
      if (onSessionExpired) {
        onSessionExpired();
      }
    }
    return Promise.reject(error);
  }
);

// ==================== AUTH ENDPOINTS ====================
export const authAPI = {
  login: async (email, password) => {
    const response = await apiClient.post('/api/auth/login', { username: email, password });
    return response.data;
  },

  logout: async () => {
    return apiClient.post('/api/auth/logout');
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },
};

// ==================== ATTENDANCE ENDPOINTS ====================
export const attendanceAPI = {
  punchIn: async (staffId, photoPath, location = null) => {
    try {
      const formData = new FormData();

      // Add timestamp in ISO 8601 format
      const timestamp = new Date().toISOString();
      formData.append('timestamp_captured', timestamp);

      console.log('Punch In - Photo Path:', photoPath);
      console.log('Punch In - Timestamp:', timestamp);
      console.log('Punch In - Location:', location);

      // Add location if available
      if (location) {
        formData.append('latitude', String(location.latitude));
        formData.append('longitude', String(location.longitude));
        formData.append('location_accuracy', String(location.accuracy || 0));
      }

      // Add photo file - for React Native/Expo, use URI directly
      if (photoPath) {
        const photoName = `punch_in_${Date.now()}.jpg`;

        // In React Native, FormData can handle file URIs directly
        formData.append('photo', {
          uri: photoPath,
          type: 'image/jpeg',
          name: photoName,
        });

        console.log('Photo appended to FormData with URI');
      }

      // Get token for Authorization header
      const token = await SecureStore.getItemAsync('auth_token');
      console.log('Token retrieved:', token ? 'YES' : 'NO');

      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
        console.log('Authorization header set');
      }

      // Use fetch API directly for better React Native file upload handling
      // DO NOT set Content-Type header - let React Native handle it with FormData
      const response = await fetch(`${API_BASE_URL}/api/attendance/punch-in-photo`, {
        method: 'POST',
        headers,
        body: formData,
      });

      console.log('Request sent, status:', response.status);

      const data = await response.json();
      console.log('Punch In Response:', data, 'Status:', response.status);

      if (!response.ok) {
        throw new Error(data.error || `Upload failed with status ${response.status}`);
      }

      return { data, status: response.status };
    } catch (error) {
      console.log('Punch In Error:', error.message);
      console.log('Full Error:', error);
      throw error;
    }
  },

  punchOut: async (staffId) => {
    try {
      // Get token for Authorization header
      const token = await SecureStore.getItemAsync('auth_token');
      console.log('Punch Out - Token retrieved:', token ? 'YES' : 'NO');

      const headers = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
        console.log('Punch Out - Authorization header set');
      }

      // Simple JSON request for punch out (no photo required)
      const response = await fetch(`${API_BASE_URL}/api/attendance/punch-out`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          timestamp_captured: new Date().toISOString(),
        }),
      });

      console.log('Punch Out - Request sent, status:', response.status);

      const data = await response.json();
      console.log('Punch Out Response:', data, 'Status:', response.status);

      if (!response.ok) {
        throw new Error(data.error || `Punch out failed with status ${response.status}`);
      }

      return { data, status: response.status };
    } catch (error) {
      console.log('Punch Out Error:', error.message);
      console.log('Full Error:', error);
      throw error;
    }
  },

  getAttendanceHistory: async (staffId, startDate, endDate) => {
    const response = await apiClient.get('/api/attendance', {
      params: {
        staff_id: staffId,
        start_date: startDate,
        end_date: endDate,
      },
    });
    return response.data;
  },

  getAttendanceStats: async (staffId, startDate, endDate) => {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await apiClient.get(`/api/attendance/stats/${staffId}`, {
      params: params.start_date || params.end_date ? params : undefined,
    });
    return response.data;
  },

  getCurrentStatus: async (staffId) => {
    const response = await apiClient.get('/api/attendance/today-status', {
      params: {
        staff_id: staffId,
      },
    });
    return response.data;
  },

  getReport: async (startDate, endDate, staffId) => {
    const response = await apiClient.get('/api/attendance/report', {
      params: {
        start_date: startDate,
        end_date: endDate,
        staff_id: staffId,
      },
    });
    return response.data;
  },
};

// ==================== STAFF ENDPOINTS ====================
export const staffAPI = {
  getProfile: async (staffId) => {
    const response = await apiClient.get(`/api/staff/${staffId}`);
    return response.data;
  },

  updateProfile: async (staffId, data) => {
    const response = await apiClient.put(`/api/staff/${staffId}`, data);
    return response.data;
  },

  getList: async () => {
    const response = await apiClient.get('/api/staff');
    return response.data;
  },
};

// ==================== PROJECTS ENDPOINTS ====================
export const projectsAPI = {
  getList: async () => {
    const response = await apiClient.get('/api/projects');
    return response.data;
  },

  getDetails: async (projectId) => {
    const response = await apiClient.get(`/api/projects/${projectId}`);
    return response.data;
  },
};

// ==================== TASKS ENDPOINTS ====================
export const tasksAPI = {
  getAssignedTasks: async (staffId) => {
    try {
      // Try the tasks endpoint first
      const response = await apiClient.get('/api/tasks', {
        params: {
          staff_id: staffId,
        },
      });
      return response.data;
    } catch (error) {
      // If that fails, return empty data
      console.log('Tasks endpoint not available');
      return { success: true, data: [] };
    }
  },

  updateTaskStatus: async (taskId, status) => {
    const response = await apiClient.put(`/api/tasks/${taskId}`, { status });
    return response.data;
  },
};

// ==================== NOTIFICATIONS ENDPOINTS ====================
export const notificationsAPI = {
  registerDevice: async (staffId, fcmToken, deviceName) => {
    const response = await apiClient.post('/api/notifications/register', {
      staff_id: staffId,
      fcm_token: fcmToken,
      device_name: deviceName,
    });
    return response.data;
  },

  getNotifications: async () => {
    const response = await apiClient.get('/api/notifications');
    return response.data;
  },
};

export default apiClient;
