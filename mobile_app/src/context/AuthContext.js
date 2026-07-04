import React, { createContext, useState, useEffect, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';
import { authAPI, setOnSessionExpired } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = React.useReducer(
    (prevState, action) => {
      switch (action.type) {
        case 'RESTORE_TOKEN':
          return {
            ...prevState,
            userToken: action.payload.token,
            user: action.payload.user,
            isLoading: false,
            passwordChangeRequired: action.payload.passwordChangeRequired || false,
          };
        case 'SIGN_IN':
          return {
            ...prevState,
            isSignout: false,
            userToken: action.payload.token,
            user: action.payload.user,
            userRole: action.payload.user.role,
            passwordChangeRequired: action.payload.passwordChangeRequired || false,
          };
        case 'SIGN_OUT':
          return {
            ...prevState,
            isSignout: true,
            userToken: null,
            user: null,
            userRole: null,
            passwordChangeRequired: false,
          };
        case 'PASSWORD_CHANGED':
          return {
            ...prevState,
            passwordChangeRequired: false,
          };
        case 'SET_USER':
          return {
            ...prevState,
            user: action.payload,
            userRole: action.payload.role,
          };
        case 'SET_LOADING':
          return {
            ...prevState,
            isLoading: action.payload,
          };
        default:
          return prevState;
      }
    },
    {
      isLoading: true,
      isSignout: false,
      userToken: null,
      user: null,
      userRole: null,
      passwordChangeRequired: false,
    }
  );

  // Register session expiry handler to auto-redirect to login on 401
  useEffect(() => {
    setOnSessionExpired(() => {
      SecureStore.deleteItemAsync('auth_token').catch(() => {});
      SecureStore.deleteItemAsync('staff_id').catch(() => {});
      SecureStore.deleteItemAsync('user_data').catch(() => {});
      SecureStore.deleteItemAsync('user_role').catch(() => {});
      dispatch({ type: 'SIGN_OUT' });
    });
  }, []);

  // Check if user is logged in on app start
  useEffect(() => {
    const bootstrapAsync = async () => {
      let userToken;
      let user = null;
      let passwordChangeRequired = false;
      try {
        userToken = await SecureStore.getItemAsync('auth_token');
        const storedUser = await SecureStore.getItemAsync('user_data');
        if (storedUser) {
          user = JSON.parse(storedUser);
        }
        const pcr = await SecureStore.getItemAsync('password_change_required');
        passwordChangeRequired = pcr === 'true';
      } catch (e) {
        // Restoring token failed
        console.log('Failed to restore token:', e);
      }

      dispatch({ type: 'RESTORE_TOKEN', payload: { token: userToken, user, passwordChangeRequired } });
    };

    bootstrapAsync();
  }, []);

  const authContext = {
    sign: async (email, password) => {
      dispatch({ type: 'SET_LOADING', payload: true });
      try {
        const response = await authAPI.login(email, password);

        // Handle backend response format
        if (response.access_token && response.user) {
          const token = response.access_token;
          const user = response.user;
          const passwordChangeRequired = user.password_change_required || false;

          // Store token and user data securely
          await SecureStore.setItemAsync('auth_token', token);
          await SecureStore.setItemAsync('user_id', user.id.toString());
          await SecureStore.setItemAsync('user_data', JSON.stringify(user));
          await SecureStore.setItemAsync('password_change_required', passwordChangeRequired.toString());
          if (user.staff_id) {
            await SecureStore.setItemAsync('staff_id', user.staff_id.toString());
          }
          if (user.role) {
            await SecureStore.setItemAsync('user_role', user.role);
          }

          dispatch({
            type: 'SIGN_IN',
            payload: { token, user, passwordChangeRequired },
          });

          return { success: true, user, passwordChangeRequired };
        } else if (response.error) {
          return { success: false, error: response.error };
        } else {
          return { success: false, error: 'Login failed' };
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message || 'Login error';
        return { success: false, error: errorMessage };
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    },

    signOut: async () => {
      dispatch({ type: 'SET_LOADING', payload: true });
      try {
        await authAPI.logout().catch(() => {}); // Ignore logout errors
        await SecureStore.deleteItemAsync('auth_token');
        await SecureStore.deleteItemAsync('user_id');
        await SecureStore.deleteItemAsync('staff_id');
        await SecureStore.deleteItemAsync('user_data');
        await SecureStore.deleteItemAsync('user_role');
        await SecureStore.deleteItemAsync('password_change_required');
        dispatch({ type: 'SIGN_OUT' });
      } catch (error) {
        console.log('Logout error:', error);
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    },

    changePassword: async (oldPassword, newPassword) => {
      try {
        const response = await authAPI.changePassword(oldPassword, newPassword);
        if (response.success) {
          await SecureStore.setItemAsync('password_change_required', 'false');
          dispatch({ type: 'PASSWORD_CHANGED' });
          return { success: true };
        } else {
          return { success: false, error: response.error || 'Failed to change password' };
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message || 'Password change failed';
        return { success: false, error: errorMessage };
      }
    },

    setUser: (user) => {
      dispatch({ type: 'SET_USER', payload: user });
    },

    getUserRole: () => state.user?.role || null,
    getUserId: () => state.user?.id || null,
    getStaffId: () => state.user?.staff_id || null,

    state,
  };

  return (
    <AuthContext.Provider value={authContext}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
