import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, RefreshControl, StyleSheet, Text, TouchableOpacity, Alert, ActivityIndicator, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { useAuth } from '../context/AuthContext';
import { getActiveFestival } from '../utils/festival';

const { width } = Dimensions.get('window');

const ManagerDashboard = ({ userId, userRole }) => {
  const { state } = useAuth();
  const festival = getActiveFestival();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const getUserFirstName = () => state.user?.first_name || 'Manager';
  const getDashboardTitle = () => userRole === 'admin' ? 'Admin' : 'Project Manager';
  const getDashboardSubtitle = () => userRole === 'admin' ? 'Full system access' : 'Oversee projects & team';

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      setStats({
        active_projects: 5, total_projects: 12, pending_tasks: 8, total_tasks: 34,
        team_members: 25, completion_rate: '85', on_leave: 3, active_today: 22,
      });
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard');
      setStats({ active_projects: 0, total_projects: 0, pending_tasks: 0, total_tasks: 0, team_members: 0, completion_rate: '0', on_leave: 0, active_today: 0 });
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
        <Text style={styles.loadingText}>Loading Manager Dashboard...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={Gradients.primary.colors} start={Gradients.primary.start} end={Gradients.primary.end} style={styles.headerGradient}>
        <View style={styles.headerRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.headerRole}>{getDashboardTitle()}</Text>
            <Text style={styles.headerGreeting}>{getGreeting()}, {getUserFirstName()}</Text>
            <Text style={styles.headerDate}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
          </View>
          <View style={styles.headerIconCircle}>
            <MaterialCommunityIcons name="briefcase" size={28} color="#ffffff" />
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
          <View style={styles.metricsRow}>
            <View style={[styles.metricCard, { borderTopColor: Colors.primary.main }]}>
              <View style={[styles.metricIconBox, { backgroundColor: Colors.iconBg.primary }]}>
                <MaterialCommunityIcons name="briefcase" size={20} color={Colors.primary.main} />
              </View>
              <Text style={styles.metricValue}>{stats?.active_projects || 0}</Text>
              <Text style={styles.metricLabel}>Active Projects</Text>
              <Text style={styles.metricSubtext}>of {stats?.total_projects || 0}</Text>
            </View>
            <View style={[styles.metricCard, { borderTopColor: Colors.warning.main }]}>
              <View style={[styles.metricIconBox, { backgroundColor: Colors.iconBg.warning }]}>
                <MaterialCommunityIcons name="checkbox-multiple-blank" size={20} color={Colors.warning.main} />
              </View>
              <Text style={styles.metricValue}>{stats?.pending_tasks || 0}</Text>
              <Text style={styles.metricLabel}>Pending Tasks</Text>
              <Text style={styles.metricSubtext}>of {stats?.total_tasks || 0}</Text>
            </View>
            <View style={[styles.metricCard, { borderTopColor: Colors.success.main }]}>
              <View style={[styles.metricIconBox, { backgroundColor: Colors.iconBg.success }]}>
                <MaterialCommunityIcons name="trending-up" size={20} color={Colors.success.main} />
              </View>
              <Text style={styles.metricValue}>{stats?.completion_rate}%</Text>
              <Text style={styles.metricLabel}>Completion Rate</Text>
              <Text style={styles.metricSubtext}>This month</Text>
            </View>
          </View>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Active Projects</Text>
            <TouchableOpacity onPress={() => Alert.alert('All Projects', `Total Projects: ${stats?.total_projects || 0}\nActive: ${stats?.active_projects || 0}\n\nTap Projects tab for full details`)}>
              <Text style={styles.sectionLink}>View All</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.projectCard} onPress={() => Alert.alert('Foundation Work - Phase 1', 'Status: Active\nProgress: 75%\nBudget: ₹45 Lakhs\nTeam: 10 members\nDue: Mar 30, 2026', [{ text: 'Close' }])}>
            <View style={styles.projectTop}>
              <View style={styles.projectInfo}>
                <Text style={styles.projectName}>Foundation Work - Phase 1</Text>
                <Text style={styles.projectDesc}>Concrete foundation laying</Text>
              </View>
              <View style={[styles.badge, { backgroundColor: Colors.success.lightest, borderColor: Colors.success.lighter }]}>
                <Text style={[styles.badgeText, { color: Colors.success.main }]}>Active</Text>
              </View>
            </View>
            <View style={styles.progressBarOuter}>
              <View style={[styles.progressBarInner, { width: '75%', backgroundColor: Colors.success.main }]} />
            </View>
            <View style={styles.projectMetaRow}>
              <Text style={styles.projectMeta}>75% Complete</Text>
              <Text style={styles.projectMeta}>10 members</Text>
              <Text style={styles.projectMeta}>Mar 30</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.projectCard} onPress={() => Alert.alert('Structural Design - Phase 2', 'Status: In Progress\nProgress: 45%\nBudget: ₹60 Lakhs\nTeam: 7 members\nDue: Apr 15, 2026', [{ text: 'Close' }])}>
            <View style={styles.projectTop}>
              <View style={styles.projectInfo}>
                <Text style={styles.projectName}>Structural Design - Phase 2</Text>
                <Text style={styles.projectDesc}>Steel structure installation</Text>
              </View>
              <View style={[styles.badge, { backgroundColor: Colors.warning.lightest, borderColor: Colors.warning.lighter }]}>
                <Text style={[styles.badgeText, { color: Colors.warning.main }]}>In Progress</Text>
              </View>
            </View>
            <View style={styles.progressBarOuter}>
              <View style={[styles.progressBarInner, { width: '45%', backgroundColor: Colors.warning.main }]} />
            </View>
            <View style={styles.projectMetaRow}>
              <Text style={styles.projectMeta}>45% Complete</Text>
              <Text style={styles.projectMeta}>7 members</Text>
              <Text style={styles.projectMeta}>Apr 15</Text>
            </View>
          </TouchableOpacity>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Team Overview</Text>
            <TouchableOpacity onPress={() => Alert.alert('Team Management', `Total: ${stats?.team_members || 0}\nActive Today: ${stats?.active_today || 0}\nOn Leave: ${stats?.on_leave || 0}`, [{ text: 'Close' }])}>
              <Text style={styles.sectionLink}>Manage</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.teamRow}>
            {[
              { label: 'Total Members', value: stats?.team_members || 0, icon: 'account-multiple', color: Colors.primary.main, bg: Colors.iconBg.primary },
              { label: 'On Leave', value: stats?.on_leave || 0, icon: 'beach', color: Colors.warning.main, bg: Colors.iconBg.warning },
              { label: 'Active Today', value: stats?.active_today || 0, icon: 'check-circle', color: Colors.success.main, bg: Colors.iconBg.success },
            ].map((item, i) => (
              <View key={i} style={styles.teamCard}>
                <View style={[styles.teamIconBox, { backgroundColor: item.bg }]}>
                  <MaterialCommunityIcons name={item.icon} size={18} color={item.color} />
                </View>
                <Text style={styles.teamValue}>{item.value}</Text>
                <Text style={styles.teamLabel}>{item.label}</Text>
              </View>
            ))}
          </View>

          <View style={[styles.sectionHeader, { marginTop: GlassTokens.spacing.sm }]}>
            <Text style={styles.sectionTitle}>Quick Actions</Text>
          </View>
          <View style={styles.actionsGrid}>
            {[
              { icon: 'plus-circle', label: 'Create', color: Colors.primary.main, bg: Colors.iconBg.primary, action: () => Alert.alert('Create Project', 'Enter name, budget, timeline', [{ text: 'Cancel' }, { text: 'Create', onPress: () => Alert.alert('Success', 'Project created!') }]) },
              { icon: 'folder-multiple', label: 'Projects', color: Colors.secondary.main, bg: Colors.iconBg.info, action: () => Alert.alert('Projects', `${stats?.total_projects || 0} total · ${stats?.active_projects || 0} active`, [{ text: 'Close' }]) },
              { icon: 'chart-bar', label: 'Reports', color: Colors.success.main, bg: Colors.iconBg.success, action: () => Alert.alert('Reports', 'Project Status · Budget · Timeline', [{ text: 'Download', onPress: () => Alert.alert('Success', 'Report downloaded!') }, { text: 'Close' }]) },
              { icon: 'account-multiple', label: 'Team', color: Colors.warning.main, bg: Colors.iconBg.warning, action: () => Alert.alert('Team', `${stats?.team_members || 0} members`, [{ text: 'Close' }]) },
            ].map((item, i) => (
              <TouchableOpacity key={i} style={styles.actionCard} onPress={item.action}>
                <View style={[styles.actionIconBox, { backgroundColor: item.bg }]}>
                  <MaterialCommunityIcons name={item.icon} size={22} color={item.color} />
                </View>
                <Text style={styles.actionLabel}>{item.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
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
  metricsRow: { flexDirection: 'row', gap: 10, marginBottom: 8 },
  metricCard: { flex: 1, backgroundColor: Colors.card.white, borderRadius: 14, padding: 14, alignItems: 'center', borderTopWidth: 3, shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  metricIconBox: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  metricValue: { fontSize: 22, fontWeight: '800', color: Colors.text.primary, marginBottom: 2 },
  metricLabel: { fontSize: 11, fontWeight: '600', color: Colors.text.secondary, textAlign: 'center' },
  metricSubtext: { fontSize: 9, color: Colors.text.tertiary, fontWeight: '500', marginTop: 2 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, marginTop: 16 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: Colors.text.primary },
  sectionLink: { fontSize: 12, fontWeight: '600', color: Colors.primary.main },
  projectCard: { backgroundColor: Colors.card.white, borderRadius: 14, padding: 16, marginBottom: 10, shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  projectTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 },
  projectInfo: { flex: 1, marginRight: 8 },
  projectName: { fontSize: 14, fontWeight: '700', color: Colors.text.primary, marginBottom: 2 },
  projectDesc: { fontSize: 12, color: Colors.text.secondary },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, borderWidth: 1 },
  badgeText: { fontSize: 10, fontWeight: '700' },
  progressBarOuter: { height: 5, backgroundColor: Colors.border.light, borderRadius: 3, marginBottom: 10, overflow: 'hidden' },
  progressBarInner: { height: '100%', borderRadius: 3 },
  projectMetaRow: { flexDirection: 'row', justifyContent: 'space-between' },
  projectMeta: { fontSize: 11, color: Colors.text.tertiary, fontWeight: '500' },
  teamRow: { flexDirection: 'row', gap: 10 },
  teamCard: { flex: 1, backgroundColor: Colors.card.white, borderRadius: 14, padding: 14, alignItems: 'center', shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  teamIconBox: { width: 32, height: 32, borderRadius: 16, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  teamValue: { fontSize: 18, fontWeight: '800', color: Colors.text.primary, marginBottom: 2 },
  teamLabel: { fontSize: 10, fontWeight: '600', color: Colors.text.secondary, textAlign: 'center' },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  actionCard: { width: (width - 32 - 10) / 2, backgroundColor: Colors.card.white, borderRadius: 14, padding: 16, alignItems: 'center', shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  actionIconBox: { width: 42, height: 42, borderRadius: 21, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  actionLabel: { fontSize: 12, fontWeight: '600', color: Colors.text.primary },
});

export default ManagerDashboard;
