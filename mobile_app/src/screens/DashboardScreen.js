import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as SecureStore from 'expo-secure-store';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import HRDashboard from '../components/HRDashboard.jsx';
import ManagerDashboard from '../components/ManagerDashboard.jsx';
import EngineerDashboard from '../components/EngineerDashboard.jsx';
import DriverDashboard from '../components/DriverDashboard.jsx';
import { Colors, GlobalStyles } from '../theme';

/**
 * DashboardScreen Component
 * Routes to role-specific dashboards based on user role
 *
 * Roles:
 * - driver: DriverDashboard
 * - engineer: EngineerDashboard (default)
 * - hr: HRDashboard
 * - manager/admin: ManagerDashboard
 */
export const DashboardScreen = () => {
  const { state } = useAuth();
  const { colors } = useTheme();
  const [staffId, setStaffId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const userRole = state.user?.role?.toLowerCase();

  useEffect(() => {
    bootstrapAsync();
  }, []);

  const bootstrapAsync = async () => {
    try {
      const staffId = await SecureStore.getItemAsync('staff_id');
      if (staffId) {
        setStaffId(parseInt(staffId));
      }
    } catch (error) {
      console.log('Error loading staff ID:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading while user data is being loaded
  if (isLoading) {
    return (
      <SafeAreaView style={[GlobalStyles.container, { backgroundColor: colors.background.primary }]}>
        <View style={GlobalStyles.centered}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={[GlobalStyles.subtitle, { marginTop: 16, color: colors.text.secondary }]}>
            Loading Dashboard...
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  // No staff ID available
  if (!staffId) {
    return (
      <SafeAreaView style={[GlobalStyles.container, { backgroundColor: colors.background.primary }]}>
        <View style={GlobalStyles.centered}>
          <Text style={[GlobalStyles.title, { color: colors.icon.danger }]}>
            Staff ID not found
          </Text>
          <Text style={[GlobalStyles.caption, { marginTop: 8, color: colors.text.secondary }]}>
            Please login again
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  // ROLE-BASED DASHBOARD ROUTING
  switch (userRole) {
    case 'driver':
      return <DriverDashboard userId={staffId} />;

    case 'engineer':
      return <EngineerDashboard userId={staffId} />;

    case 'hr':
      return <HRDashboard userId={staffId} />;

    case 'manager':
    case 'admin':
      return <ManagerDashboard userId={staffId} userRole={userRole} />;

    default:
      // Fallback to engineer dashboard for unknown roles
      return <EngineerDashboard userId={staffId} />;
  }
};

const styles = StyleSheet.create({});
