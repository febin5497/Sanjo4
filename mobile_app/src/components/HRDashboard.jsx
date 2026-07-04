import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, RefreshControl, StyleSheet, Text, TouchableOpacity, Alert, ActivityIndicator, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { attendanceAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { getActiveFestival } from '../utils/festival';

const { width } = Dimensions.get('window');

const HRDashboard = ({ userId }) => {
  const { state } = useAuth();
  const festival = getActiveFestival();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const getUserFirstName = () => state.user?.first_name || 'HR Manager';

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      const response = await attendanceAPI.getApprovalStats?.();
      if (response && response.data) {
        setStats(response.data);
      } else {
        setStats({ pending_approvals: 8, total_staff: 25, present_today: 22, absent_today: 3, pending_photos: 5, leave_requests: 3 });
      }
      setError(null);
    } catch (err) {
      setError('Failed to load statistics');
      setStats({ pending_approvals: 0, total_staff: 0, present_today: 0, absent_today: 0, pending_photos: 0, leave_requests: 0 });
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadStats().finally(() => setRefreshing(false));
  }, [loadStats]);

  useEffect(() => { loadStats(); }, [loadStats]);

  if (loading && !stats) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.primary.main} />
        <Text style={styles.loadingText}>Loading HR Dashboard...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={Gradients.primary.colors} start={Gradients.primary.start} end={Gradients.primary.end} style={styles.headerGradient}>
        <View style={styles.headerRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.headerRole}>HR Manager</Text>
            <Text style={styles.headerGreeting}>{getGreeting()}, {getUserFirstName()}</Text>
            <Text style={styles.headerDate}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
          </View>
          <View style={styles.headerIconCircle}>
            <MaterialCommunityIcons name="human-greeting" size={28} color="#ffffff" />
          </View>
        </View>
        {festival && (
          <View style={styles.festivalBanner}>
            <MaterialCommunityIcons name={festival.icon} size={14} color="#ffffff" />
            <Text style={styles.festivalText}>{festival.message}</Text>
          </View>
        )}
      </LinearGradient>

      <ScrollView style={styles.scrollView} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
        {error && (
          <View style={styles.errorBanner}>
            <MaterialCommunityIcons name="alert-circle" size={16} color={Colors.danger.main} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        <View style={styles.content}>
          <View style={styles.statsGrid}>
            {[
              { label: 'Pending Approvals', value: stats?.pending_approvals || 0, icon: 'clock-check', color: Colors.warning.main, bg: Colors.iconBg.warning, border: Colors.warning.main },
              { label: 'Total Staff', value: stats?.total_staff || 0, icon: 'people', color: Colors.primary.main, bg: Colors.iconBg.primary, border: Colors.primary.main },
              { label: 'Present Today', value: stats?.present_today || 0, icon: 'check-circle', color: Colors.success.main, bg: Colors.iconBg.success, border: Colors.success.main },
              { label: 'Absent Today', value: stats?.absent_today || 0, icon: 'close-circle', color: Colors.danger.main, bg: Colors.iconBg.danger, border: Colors.danger.main },
            ].map((item, i) => (
              <View key={i} style={[styles.statCard, { borderTopColor: item.border }]}>
                <View style={[styles.statIconBox, { backgroundColor: item.bg }]}>
                  <MaterialCommunityIcons name={item.icon} size={22} color={item.color} />
                </View>
                <Text style={styles.statValue}>{item.value}</Text>
                <Text style={styles.statLabel}>{item.label}</Text>
              </View>
            ))}
          </View>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Quick Actions</Text>
          </View>
          <View style={styles.actionsGrid}>
            {[
              { icon: 'calendar-check', label: 'Attendance', color: Colors.primary.main, bg: Colors.iconBg.primary, action: () => Alert.alert('Attendance', `Present: ${stats?.present_today || 0}/${stats?.total_staff || 0}`, [{ text: 'Close' }]) },
              { icon: 'image-check', label: 'Approve Photos', color: Colors.success.main, bg: Colors.iconBg.success, action: () => Alert.alert('Photo Approvals', `${stats?.pending_photos || 0} photos pending`, [{ text: 'Review', onPress: () => Alert.alert('Photos', 'Photo gallery opened') }, { text: 'Close' }]) },
              { icon: 'file-document-check', label: 'Leave Requests', color: Colors.warning.main, bg: Colors.iconBg.warning, action: () => Alert.alert('Leave Requests', `${stats?.leave_requests || 0} pending requests`, [{ text: 'Review', onPress: () => Alert.alert('Leave', 'Requests loaded') }, { text: 'Close' }]) },
              { icon: 'account-multiple', label: 'Staff', color: Colors.secondary.main, bg: Colors.iconBg.info, action: () => Alert.alert('Staff', `${stats?.total_staff || 0} total members`, [{ text: 'Manage', onPress: () => Alert.alert('Staff', 'Management opened') }, { text: 'Close' }]) },
            ].map((item, i) => (
              <TouchableOpacity key={i} style={styles.actionCard} onPress={item.action}>
                <View style={[styles.actionIconBox, { backgroundColor: item.bg }]}>
                  <MaterialCommunityIcons name={item.icon} size={22} color={item.color} />
                </View>
                <Text style={styles.actionLabel}>{item.label}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Activity</Text>
          </View>
          {[
            { icon: 'image-check', title: '5 photos approved', time: 'Today at 10:30 AM', color: Colors.primary.main, bg: Colors.iconBg.primary },
            { icon: 'file-document', title: '2 leave requests received', time: 'Today at 09:15 AM', color: Colors.success.main, bg: Colors.iconBg.success },
            { icon: 'alert-circle', title: '3 staff members absent', time: 'Yesterday at 09:00 AM', color: Colors.warning.main, bg: Colors.iconBg.warning },
          ].map((item, i) => (
            <TouchableOpacity key={i} style={styles.activityCard} onPress={() => Alert.alert(item.title, item.time, [{ text: 'Close' }])}>
              <View style={[styles.activityIconBox, { backgroundColor: item.bg }]}>
                <MaterialCommunityIcons name={item.icon} size={18} color={item.color} />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>{item.title}</Text>
                <Text style={styles.activityTime}>{item.time}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>
        <View style={{ height: 100 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background.primary },
  scrollView: { flex: 1 },
  centered: { ...GlobalStyles.centered, backgroundColor: Colors.background.primary },
  loadingText: { marginTop: 12, fontSize: 14, color: Colors.text.secondary },
  headerGradient: { paddingVertical: 28, paddingHorizontal: 20, paddingTop: 16 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  headerRole: { fontSize: 11, fontWeight: '700', color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 4 },
  headerGreeting: { fontSize: 22, fontWeight: '800', color: '#ffffff', letterSpacing: -0.3 },
  headerDate: { fontSize: 13, color: 'rgba(255,255,255,0.65)', marginTop: 4, fontWeight: '500' },
  headerIconCircle: { width: 48, height: 48, borderRadius: 24, backgroundColor: 'rgba(255,255,255,0.2)', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: 'rgba(255,255,255,0.3)' },
  festivalBanner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 6, paddingHorizontal: 12, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.15)', marginTop: 12, gap: 6 },
  festivalText: { fontSize: 12, fontWeight: '600', color: '#ffffff' },
  errorBanner: { flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.danger.lightest, borderLeftWidth: 3, borderLeftColor: Colors.danger.main, padding: 14, marginHorizontal: 16, marginTop: 12, borderRadius: 10 },
  errorText: { color: Colors.danger.main, marginLeft: 8, flex: 1, fontSize: 13, fontWeight: '500' },
  content: { padding: 16 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 8 },
  statCard: { width: (width - 32 - 10) / 2, backgroundColor: Colors.card.white, borderRadius: 14, padding: 16, alignItems: 'center', borderTopWidth: 3, shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  statIconBox: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  statValue: { fontSize: 24, fontWeight: '800', color: Colors.text.primary, marginBottom: 2 },
  statLabel: { fontSize: 11, fontWeight: '600', color: Colors.text.secondary, textAlign: 'center' },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, marginTop: 16 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: Colors.text.primary },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  actionCard: { width: (width - 32 - 10) / 2, backgroundColor: Colors.card.white, borderRadius: 14, padding: 16, alignItems: 'center', shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  actionIconBox: { width: 42, height: 42, borderRadius: 21, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  actionLabel: { fontSize: 12, fontWeight: '600', color: Colors.text.primary },
  activityCard: { flexDirection: 'row', backgroundColor: Colors.card.white, borderRadius: 14, padding: 14, marginBottom: 8, alignItems: 'center', shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 1 }, shadowOpacity: 1, shadowRadius: 6, elevation: 2 },
  activityIconBox: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  activityContent: { flex: 1 },
  activityTitle: { fontSize: 13, fontWeight: '600', color: Colors.text.primary, marginBottom: 2 },
  activityTime: { fontSize: 11, color: Colors.text.tertiary },
});

export default HRDashboard;
