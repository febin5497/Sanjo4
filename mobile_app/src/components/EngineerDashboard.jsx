import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  ScrollView,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { useAuth } from '../context/AuthContext';
import { getActiveFestival } from '../utils/festival';

const { width } = Dimensions.get('window');

const EngineerDashboard = ({ userId }) => {
  const { state } = useAuth();
  const festival = getActiveFestival();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const getUserFirstName = () => {
    return state.user?.first_name || 'Engineer';
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getFormattedDate = () => {
    const now = new Date();
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    return now.toLocaleDateString('en-IN', options);
  };

  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setStats({
        recent_expenses: 12,
        total_expenses: 1250.50,
        pending_approvals: 3,
        projects: 4,
        completed_tasks: 18,
        pending_tasks: 5,
      });
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error loading stats:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadStats().finally(() => setRefreshing(false));
  }, [loadStats]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const metrics = [
    {
      key: 'recent_expenses',
      icon: 'receipt',
      value: `${stats?.recent_expenses || 0}`,
      label: 'Recent Expenses',
      subtext: 'This month',
      iconBg: Colors.iconBg.primary,
      iconColor: Colors.primary.main,
      borderColor: Colors.primary.main,
    },
    {
      key: 'total_expenses',
      icon: 'currency-inr',
      value: `₹${(stats?.total_expenses || 0).toFixed(2)}`,
      label: 'Total Expenses',
      subtext: 'This month',
      iconBg: Colors.iconBg.success,
      iconColor: Colors.success.main,
      borderColor: Colors.success.main,
    },
    {
      key: 'pending_approvals',
      icon: 'clock-check',
      value: `${stats?.pending_approvals || 0}`,
      label: 'Pending Approvals',
      subtext: 'Awaiting review',
      iconBg: Colors.iconBg.warning,
      iconColor: Colors.warning.main,
      borderColor: Colors.warning.main,
    },
  ];

  const projects = [
    {
      name: 'Foundation Work - Phase 1',
      description: 'Concrete foundation laying for main structure',
      status: 'Active',
      progress: 75,
      meta: 'Due: Mar 30, 2026',
      statusStyle: 'success',
    },
    {
      name: 'Structural Design - Phase 2',
      description: 'Steel structure installation and reinforcement',
      status: 'In Progress',
      progress: 45,
      meta: 'Due: Apr 15, 2026',
      statusStyle: 'warning',
    },
    {
      name: 'Electrical Wiring - Phase 3',
      description: 'Main conduit and panel installation',
      status: 'Active',
      progress: 30,
      meta: 'Due: May 10, 2026',
      statusStyle: 'success',
    },
    {
      name: 'Plumbing Layout - Phase 1',
      description: 'Underground pipeline and drainage setup',
      status: 'In Progress',
      progress: 60,
      meta: 'Due: Apr 05, 2026',
      statusStyle: 'warning',
    },
  ];

  const quickActions = [
    { icon: 'plus-circle', label: 'Add Expense', color: Colors.primary.main, bg: Colors.iconBg.primary },
    { icon: 'file-document', label: 'Reports', color: Colors.success.main, bg: Colors.iconBg.success },
    { icon: 'camera', label: 'Photos', color: Colors.warning.main, bg: Colors.iconBg.warning },
    { icon: 'folder-multiple', label: 'Projects', color: Colors.primary.main, bg: Colors.iconBg.primary },
  ];

  if (loading && !stats) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={Colors.primary.main} />
        <Text style={styles.loadingText}>Loading Engineer Dashboard...</Text>
      </View>
    );
  }

  if (error && !stats) {
    return (
      <View style={styles.centered}>
        <MaterialCommunityIcons name="alert-circle" size={48} color={Colors.error?.main || '#ef4444'} />
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadStats}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={Gradients.primary.colors}
        start={Gradients.primary.start}
        end={Gradients.primary.end}
        style={styles.headerGradient}
      >
        <View style={styles.headerTop}>
          <View style={styles.headerLeft}>
            <View style={styles.roleBadge}>
              <Text style={styles.roleBadgeText}>Site Engineer</Text>
            </View>
            <Text style={styles.headerGreeting}>{getGreeting()}, {getUserFirstName()}</Text>
            <Text style={styles.headerDate}>{getFormattedDate()}</Text>
          </View>
          <View style={styles.headerIcon}>
            <MaterialCommunityIcons name="hard-hat" size={28} color="#ffffff" />
          </View>
        </View>
        {festival && (
          <View style={styles.festivalBanner}>
            <MaterialCommunityIcons name={festival.icon} size={14} color="#ffffff" />
            <Text style={styles.festivalText}>{festival.message}</Text>
          </View>
        )}
      </LinearGradient>

      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.metricsRow}>
          {metrics.map((metric, index) => (
            <View key={index} style={[styles.metricCard, { borderTopColor: metric.borderColor }]}>
              <View style={[styles.metricIconCircle, { backgroundColor: metric.iconBg }]}>
                <MaterialCommunityIcons name={metric.icon} size={18} color={metric.iconColor} />
              </View>
              <Text style={styles.metricValue}>{metric.value}</Text>
              <Text style={styles.metricLabel}>{metric.label}</Text>
              <Text style={styles.metricSubtext}>{metric.subtext}</Text>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Active Projects</Text>
            <Text style={styles.sectionLink}>{stats?.projects || 0} total</Text>
          </View>
          {projects.map((project, index) => (
            <TouchableOpacity
              key={index}
              style={styles.projectCard}
              activeOpacity={0.7}
              onPress={() => Alert.alert(project.name, `Progress: ${project.progress}%\n${project.meta}`)}
            >
              <View style={styles.projectHeader}>
                <Text style={styles.projectName} numberOfLines={1}>{project.name}</Text>
                <View style={[
                  styles.statusBadge,
                  project.statusStyle === 'success' ? styles.statusActive : styles.statusInProgress,
                ]}>
                  <Text style={[
                    styles.statusText,
                    project.statusStyle === 'success' ? styles.statusTextActive : styles.statusTextWarning,
                  ]}>{project.status}</Text>
                </View>
              </View>
              <Text style={styles.projectDescription} numberOfLines={2}>{project.description}</Text>
              <View style={styles.progressContainer}>
                <View style={styles.progressTrack}>
                  <View style={[styles.progressBar, { width: `${project.progress}%` }]} />
                </View>
              </View>
              <View style={styles.projectMetaRow}>
                <Text style={styles.projectMetaText}>{project.progress}% complete</Text>
                <Text style={styles.projectMetaText}>{project.meta}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionGrid}>
            {quickActions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={styles.actionCard}
                activeOpacity={0.7}
                onPress={() => Alert.alert(action.label, `${action.label} action triggered`)}
              >
                <View style={[styles.actionIconCircle, { backgroundColor: action.bg }]}>
                  <MaterialCommunityIcons name={action.icon} size={22} color={action.color} />
                </View>
                <Text style={styles.actionLabel}>{action.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.footer} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background?.secondary || '#f5f7fa',
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background?.secondary || '#f5f7fa',
    padding: 24,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: Colors.text?.secondary || '#6b7280',
  },
  errorText: {
    marginTop: 12,
    fontSize: 14,
    color: Colors.text?.secondary || '#6b7280',
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: Colors.primary?.main || '#3b82f6',
  },
  retryText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  headerGradient: {
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: 16,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerLeft: {
    flex: 1,
    marginRight: 12,
  },
  roleBadge: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 14,
    paddingHorizontal: 12,
    paddingVertical: 4,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  roleBadgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#ffffff',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  headerGreeting: {
    fontSize: 22,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 4,
  },
  headerDate: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.8)',
    fontWeight: '500',
  },
  festivalBanner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 6, paddingHorizontal: 12, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.15)', marginTop: 12, gap: 6 },
  festivalText: { fontSize: 12, fontWeight: '600', color: '#ffffff' },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  metricsRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingTop: 20,
    gap: 10,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 14,
    borderTopWidth: 3,
    paddingTop: 16,
    paddingBottom: 14,
    paddingHorizontal: 8,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 3,
  },
  metricIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: '800',
    color: Colors.text?.primary || '#1f2937',
    marginBottom: 2,
  },
  metricLabel: {
    fontSize: 11,
    fontWeight: '500',
    color: Colors.text?.secondary || '#6b7280',
    textAlign: 'center',
    marginBottom: 2,
  },
  metricSubtext: {
    fontSize: 9,
    color: Colors.text?.tertiary || '#9ca3af',
    fontWeight: '500',
    textAlign: 'center',
  },
  section: {
    paddingHorizontal: 16,
    paddingTop: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: Colors.text?.primary || '#1f2937',
  },
  sectionLink: {
    fontSize: 13,
    color: Colors.primary?.main || '#3b82f6',
    fontWeight: '600',
  },
  projectCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 3,
  },
  projectHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  projectName: {
    fontSize: 14,
    fontWeight: '700',
    color: Colors.text?.primary || '#1f2937',
    flex: 1,
    marginRight: 8,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 14,
  },
  statusActive: {
    backgroundColor: Colors.success?.lighter || '#dcfce7',
  },
  statusInProgress: {
    backgroundColor: Colors.warning?.lighter || '#fef3c7',
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
  },
  statusTextActive: {
    color: Colors.success?.main || '#16a34a',
  },
  statusTextWarning: {
    color: Colors.warning?.main || '#d97706',
  },
  projectDescription: {
    fontSize: 12,
    color: Colors.text?.secondary || '#6b7280',
    marginBottom: 12,
    lineHeight: 17,
  },
  progressContainer: {
    marginBottom: 10,
  },
  progressTrack: {
    height: 5,
    backgroundColor: Colors.border?.light || '#e5e7eb',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: Colors.primary?.main || '#3b82f6',
    borderRadius: 3,
  },
  projectMetaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  projectMetaText: {
    fontSize: 11,
    color: Colors.text?.tertiary || '#9ca3af',
    fontWeight: '500',
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginTop: 14,
  },
  actionCard: {
    width: (width - 32 - 10) / 2,
    backgroundColor: '#ffffff',
    borderRadius: 14,
    paddingVertical: 20,
    paddingHorizontal: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 3,
  },
  actionIconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  actionLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: Colors.text?.primary || '#1f2937',
    textAlign: 'center',
  },
  footer: {
    height: 100,
  },
});

export default EngineerDashboard;
