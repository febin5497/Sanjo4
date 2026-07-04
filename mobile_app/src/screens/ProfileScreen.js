import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import * as SecureStore from 'expo-secure-store';
import { staffAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';

const getDynamicStyles = (colors) => {
  return StyleSheet.create({
    container: {
      flex: 1,
    },
    content: {
      padding: GlassTokens.spacing.lg,
    },
    profileCard: {
      ...GlobalStyles.cardLarge,
      alignItems: 'center',
      marginBottom: GlassTokens.spacing.xxl,
      paddingVertical: GlassTokens.spacing.xl,
    },
    avatarContainer: {
      marginBottom: GlassTokens.spacing.lg,
    },
    avatar: {
      width: 90,
      height: 90,
      borderRadius: 45,
      backgroundColor: colors.primaryLight,
      justifyContent: 'center',
      alignItems: 'center',
      borderWidth: 3,
      borderColor: colors.primary,
      shadowColor: colors.primary,
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.2,
      shadowRadius: 16,
      elevation: 8,
    },
    avatarText: {
      fontSize: 36,
      fontWeight: '800',
      color: '#ffffff',
    },
    name: {
      ...GlobalStyles.title,
      color: colors.primary,
      marginBottom: GlassTokens.spacing.sm,
    },
    role: {
      ...GlobalStyles.label,
      color: colors.primary,
    },
    section: {
      marginBottom: GlassTokens.spacing.xxl,
    },
    sectionTitle: {
      ...GlobalStyles.subtitle,
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.lg,
      fontWeight: '700',
    },
    infoCard: {
      ...GlobalStyles.card,
      overflow: 'hidden',
    },
    infoRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.lg,
    },
    borderTop: {
      borderTopWidth: 1,
      borderTopColor: colors.border.glass,
    },
    infoLabel: {
      ...GlobalStyles.label,
      color: colors.primary,
    },
    infoValue: {
      ...GlobalStyles.body,
      fontWeight: '700',
      color: colors.text.primary,
      textAlign: 'right',
      flex: 1,
      marginLeft: GlassTokens.spacing.md,
    },
    actionCard: {
      ...GlobalStyles.card,
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: GlassTokens.spacing.md,
    },
    actionIcon: {
      fontSize: 28,
      marginRight: GlassTokens.spacing.md,
    },
    actionContent: {
      flex: 1,
    },
    actionTitle: {
      ...GlobalStyles.subtitle,
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.xs,
      fontWeight: '600',
    },
    actionSubtitle: {
      ...GlobalStyles.caption,
      color: colors.text.secondary,
    },
    actionArrow: {
      fontSize: 20,
      color: colors.primaryLight,
    },
    spacer: {
      height: GlassTokens.spacing.xl,
    },
  });
};

export const ProfileScreen = () => {
  const { signOut, state } = useAuth();
  const { colors, isDarkMode, toggleTheme } = useTheme();
  const dynamicStyles = getDynamicStyles(colors);
  const [staffId, setStaffId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    bootstrapAsync();
  }, []);

  const bootstrapAsync = async () => {
    try {
      const staffId = await SecureStore.getItemAsync('staff_id');
      if (staffId) {
        const numId = parseInt(staffId);
        setStaffId(numId);
        await fetchProfile(numId);
      }
    } catch (error) {
      console.log('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProfile = async (id) => {
    try {
      // Use mock profile data for now
      setProfile({
        id: id,
        name: state.user?.name || 'Employee',
        role: state.user?.role || 'Staff Member',
        phone: '+91-XXXXXXXXXX',
        joining_date: new Date('2023-01-15'),
        salary: 45000,
        pf: 3600,
        esi: 500,
      });
    } catch (error) {
      console.log('Error fetching profile:', error);
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={[dynamicStyles.container, { backgroundColor: colors.background.secondary }]}>
        <View style={GlobalStyles.centered}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[dynamicStyles.container, { backgroundColor: colors.background.primary }]}>
      <ScrollView style={[dynamicStyles.content, { backgroundColor: colors.background.primary }]}>
        {/* Profile Header */}
        <View style={dynamicStyles.profileCard}>
          <View style={dynamicStyles.avatarContainer}>
            <View style={dynamicStyles.avatar}>
              <Text style={dynamicStyles.avatarText}>
                {profile?.name?.charAt(0).toUpperCase() || 'E'}
              </Text>
            </View>
          </View>
          <Text style={dynamicStyles.name}>{profile?.name || 'Employee'}</Text>
          <Text style={dynamicStyles.role}>{profile?.role || 'Staff Member'}</Text>
        </View>

        {/* Personal Information */}
        <View style={dynamicStyles.section}>
          <Text style={dynamicStyles.sectionTitle}>Personal Information</Text>

          <View style={dynamicStyles.infoCard}>
            <View style={dynamicStyles.infoRow}>
              <Text style={dynamicStyles.infoLabel}>Email</Text>
              <Text style={dynamicStyles.infoValue}>{profile?.user?.email || 'N/A'}</Text>
            </View>

            <View style={[dynamicStyles.infoRow, dynamicStyles.borderTop]}>
              <Text style={dynamicStyles.infoLabel}>Phone</Text>
              <Text style={dynamicStyles.infoValue}>{profile?.phone || 'N/A'}</Text>
            </View>

            <View style={[dynamicStyles.infoRow, dynamicStyles.borderTop]}>
              <Text style={dynamicStyles.infoLabel}>Joining Date</Text>
              <Text style={dynamicStyles.infoValue}>
                {profile?.joining_date
                  ? new Date(profile.joining_date).toLocaleDateString()
                  : 'N/A'}
              </Text>
            </View>

            <View style={[dynamicStyles.infoRow, dynamicStyles.borderTop]}>
              <Text style={dynamicStyles.infoLabel}>Employee ID</Text>
              <Text style={dynamicStyles.infoValue}>{profile?.id || 'N/A'}</Text>
            </View>
          </View>
        </View>

        {/* Salary Information */}
        {profile?.salary && (
          <View style={dynamicStyles.section}>
            <Text style={dynamicStyles.sectionTitle}>Salary Information</Text>

            <View style={dynamicStyles.infoCard}>
              <View style={dynamicStyles.infoRow}>
                <Text style={dynamicStyles.infoLabel}>Basic Salary</Text>
                <Text style={dynamicStyles.infoValue}>₹{profile.salary.toLocaleString()}</Text>
              </View>

              {profile?.pf && (
                <View style={[dynamicStyles.infoRow, dynamicStyles.borderTop]}>
                  <Text style={dynamicStyles.infoLabel}>PF Amount</Text>
                  <Text style={dynamicStyles.infoValue}>₹{profile.pf.toLocaleString()}</Text>
                </View>
              )}

              {profile?.esi && (
                <View style={[dynamicStyles.infoRow, dynamicStyles.borderTop]}>
                  <Text style={dynamicStyles.infoLabel}>ESI Amount</Text>
                  <Text style={dynamicStyles.infoValue}>₹{profile.esi.toLocaleString()}</Text>
                </View>
              )}
            </View>
          </View>
        )}

        {/* Actions */}
        <View style={dynamicStyles.section}>
          <TouchableOpacity
            style={dynamicStyles.actionCard}
            onPress={() => Alert.alert('Documents', 'Your Documents:\n\n✓ Payslips (12 files)\n✓ Contracts (1 file)\n✓ Certificates (3 files)\n\nDownload?', [
              { text: 'Download All', onPress: () => Alert.alert('Success', 'Documents downloaded!') },
              { text: 'View Online', onPress: () => Alert.alert('View', 'Opening document viewer...') },
              { text: 'Close', onPress: () => {} }
            ])}
          >
            <Text style={dynamicStyles.actionIcon}>📋</Text>
            <View style={dynamicStyles.actionContent}>
              <Text style={dynamicStyles.actionTitle}>Documents</Text>
              <Text style={dynamicStyles.actionSubtitle}>View your payslips and documents</Text>
            </View>
            <Text style={dynamicStyles.actionArrow}>›</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={dynamicStyles.actionCard}
            onPress={() => Alert.alert('Change Password', 'Current Password: ___________\n\nNew Password: ___________\n\nConfirm: ___________\n\nUpdate?', [
              { text: 'Update', onPress: () => Alert.alert('Success', 'Password changed successfully!') },
              { text: 'Cancel', onPress: () => {} }
            ])}
          >
            <Text style={dynamicStyles.actionIcon}>🔐</Text>
            <View style={dynamicStyles.actionContent}>
              <Text style={dynamicStyles.actionTitle}>Change Password</Text>
              <Text style={dynamicStyles.actionSubtitle}>Update your account password</Text>
            </View>
            <Text style={dynamicStyles.actionArrow}>›</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={dynamicStyles.actionCard}
            onPress={() => Alert.alert('About App', 'Construction Manager Pro\n\nVersion: 2.1.0\nBuild: 156\nReleased: March 2026\n\nVisit website for more info', [
              { text: 'Visit Website', onPress: () => Alert.alert('Website', 'Opening company website...') },
              { text: 'Close', onPress: () => {} }
            ])}
          >
            <Text style={dynamicStyles.actionIcon}>ℹ️</Text>
            <View style={dynamicStyles.actionContent}>
              <Text style={dynamicStyles.actionTitle}>About</Text>
              <Text style={dynamicStyles.actionSubtitle}>App version and information</Text>
            </View>
            <Text style={dynamicStyles.actionArrow}>›</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={dynamicStyles.actionCard}
            onPress={toggleTheme}
          >
            <Text style={dynamicStyles.actionIcon}>{isDarkMode ? '🌙' : '☀️'}</Text>
            <View style={dynamicStyles.actionContent}>
              <Text style={dynamicStyles.actionTitle}>Display Mode</Text>
              <Text style={dynamicStyles.actionSubtitle}>{isDarkMode ? 'Dark Mode' : 'Light Mode'} • Tap to switch</Text>
            </View>
            <Text style={dynamicStyles.actionArrow}>›</Text>
          </TouchableOpacity>
        </View>

        <View style={dynamicStyles.spacer} />
        </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({});
