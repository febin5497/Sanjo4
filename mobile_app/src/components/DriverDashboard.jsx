import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, RefreshControl, StyleSheet, Text, TouchableOpacity, Alert, ActivityIndicator, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { useAuth } from '../context/AuthContext';
import { getActiveFestival } from '../utils/festival';

const { width } = Dimensions.get('window');

const DriverDashboard = ({ userId }) => {
  const { state } = useAuth();
  const festival = getActiveFestival();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const getUserFirstName = () => state.user?.first_name || 'Driver';

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
        active_trips: 2, total_trips: 45, distance: 1280, fuel_efficiency: '14.5',
        vehicle: { name: 'Tata Ace', plate: 'MH 12 AB 1234', status: 'Active', next_service: 'Apr 10, 2026' },
        inspections: 3, accidents: 0, certificates: ['Driving License', 'Vehicle Insurance', 'Pollution Cert'],
      });
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard');
      setStats({ active_trips: 0, total_trips: 0, distance: 0, fuel_efficiency: '0', vehicle: { name: '-', plate: '-', status: 'N/A', next_service: '-' }, inspections: 0, accidents: 0, certificates: [] });
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
        <Text style={styles.loadingText}>Loading Driver Dashboard...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={Gradients.primary.colors} start={Gradients.primary.start} end={Gradients.primary.end} style={styles.headerGradient}>
        <View style={styles.headerRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.headerRole}>Driver</Text>
            <Text style={styles.headerGreeting}>{getGreeting()}, {getUserFirstName()}</Text>
            <Text style={styles.headerDate}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
          </View>
          <View style={styles.headerIconCircle}>
            <MaterialCommunityIcons name="car" size={28} color="#ffffff" />
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
          <View style={[styles.vehicleCard, { borderLeftColor: Colors.success.main }]}>
            <View style={styles.vehicleTop}>
              <View>
                <Text style={styles.vehicleName}>{stats?.vehicle?.name || '-'}</Text>
                <Text style={styles.vehiclePlate}>{stats?.vehicle?.plate || '-'}</Text>
              </View>
              <View style={[styles.badge, { backgroundColor: Colors.success.lightest, borderColor: Colors.success.lighter }]}>
                <Text style={[styles.badgeText, { color: Colors.success.main }]}>{stats?.vehicle?.status || 'N/A'}</Text>
              </View>
            </View>
            <View style={styles.vehicleMetaRow}>
              <MaterialCommunityIcons name="wrench" size={14} color={Colors.text.tertiary} />
              <Text style={styles.vehicleMeta}>Next service: {stats?.vehicle?.next_service || '-'}</Text>
            </View>
          </View>

          <View style={styles.metricsRow}>
            <View style={[styles.metricCard, { borderTopColor: Colors.primary.main }]}>
              <View style={[styles.metricIconBox, { backgroundColor: Colors.iconBg.primary }]}>
                <MaterialCommunityIcons name="map-marker-path" size={20} color={Colors.primary.main} />
              </View>
              <Text style={styles.metricValue}>{stats?.active_trips || 0}</Text>
              <Text style={styles.metricLabel}>Active Trips</Text>
            </View>
            <View style={[styles.metricCard, { borderTopColor: Colors.success.main }]}>
              <View style={[styles.metricIconBox, { backgroundColor: Colors.iconBg.success }]}>
                <MaterialCommunityIcons name="road-variant" size={20} color={Colors.success.main} />
              </View>
              <Text style={styles.metricValue}>{stats?.distance || 0}km</Text>
              <Text style={styles.metricLabel}>Total Distance</Text>
            </View>
            <View style={[styles.metricCard, { borderTopColor: Colors.warning.main }]}>
              <View style={[styles.metricIconBox, { backgroundColor: Colors.iconBg.warning }]}>
                <MaterialCommunityIcons name="gas-station" size={20} color={Colors.warning.main} />
              </View>
              <Text style={styles.metricValue}>{stats?.fuel_efficiency || '0'}km/l</Text>
              <Text style={styles.metricLabel}>Fuel Efficiency</Text>
            </View>
          </View>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Trip Statistics</Text>
          </View>
          <View style={styles.statsRow}>
            {[
              { label: 'Total Trips', value: stats?.total_trips || 0, icon: 'counter', color: Colors.primary.main, bg: Colors.iconBg.primary },
              { label: 'Inspections', value: stats?.inspections || 0, icon: 'clipboard-check', color: Colors.warning.main, bg: Colors.iconBg.warning },
              { label: 'Accidents', value: stats?.accidents || 0, icon: 'alert', color: Colors.danger.main, bg: Colors.iconBg.danger },
            ].map((item, i) => (
              <View key={i} style={styles.statCard}>
                <View style={[styles.statIconBox, { backgroundColor: item.bg }]}>
                  <MaterialCommunityIcons name={item.icon} size={18} color={item.color} />
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
              { icon: 'play-circle', label: 'Start Trip', color: Colors.success.main, bg: Colors.iconBg.success, action: () => Alert.alert('Start Trip', 'Enter destination & details', [{ text: 'Cancel' }, { text: 'Start', onPress: () => Alert.alert('Success', 'Trip started! GPS active') }]) },
              { icon: 'flag-checkered', label: 'End Trip', color: Colors.danger.main, bg: Colors.iconBg.danger, action: () => Alert.alert('End Trip', 'Confirm trip completion?', [{ text: 'Cancel' }, { text: 'End', onPress: () => Alert.alert('Success', 'Trip ended!') }]) },
              { icon: 'fuel', label: 'Fuel Log', color: Colors.warning.main, bg: Colors.iconBg.warning, action: () => Alert.alert('Fuel Log', 'Enter liters, cost & mileage', [{ text: 'Cancel' }, { text: 'Save', onPress: () => Alert.alert('Success', 'Fuel entry recorded!') }]) },
              { icon: 'file-document', label: 'Reports', color: Colors.primary.main, bg: Colors.iconBg.primary, action: () => Alert.alert('Reports', 'Trip logs · Fuel · Maintenance', [{ text: 'Download', onPress: () => Alert.alert('Success', 'Report downloaded!') }, { text: 'Close' }]) },
            ].map((item, i) => (
              <TouchableOpacity key={i} style={styles.actionCard} onPress={item.action}>
                <View style={[styles.actionIconBox, { backgroundColor: item.bg }]}>
                  <MaterialCommunityIcons name={item.icon} size={22} color={item.color} />
                </View>
                <Text style={styles.actionLabel}>{item.label}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {(stats?.certificates?.length || 0) > 0 && (
            <>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Certificates</Text>
              </View>
              <View style={styles.certSection}>
                {stats.certificates.map((cert, i) => (
                  <View key={i} style={styles.certRow}>
                    <MaterialCommunityIcons name="shield-check" size={16} color={Colors.success.main} />
                    <Text style={styles.certText}>{cert}</Text>
                  </View>
                ))}
              </View>
            </>
          )}
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
  vehicleCard: { backgroundColor: Colors.card.white, borderRadius: 14, padding: 16, marginBottom: 12, borderLeftWidth: 4, shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  vehicleTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 },
  vehicleName: { fontSize: 16, fontWeight: '700', color: Colors.text.primary, marginBottom: 2 },
  vehiclePlate: { fontSize: 13, color: Colors.text.secondary },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, borderWidth: 1 },
  badgeText: { fontSize: 10, fontWeight: '700' },
  vehicleMetaRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  vehicleMeta: { fontSize: 12, color: Colors.text.tertiary, fontWeight: '500' },
  metricsRow: { flexDirection: 'row', gap: 10, marginBottom: 8 },
  metricCard: { flex: 1, backgroundColor: Colors.card.white, borderRadius: 14, padding: 14, alignItems: 'center', borderTopWidth: 3, shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  metricIconBox: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  metricValue: { fontSize: 20, fontWeight: '800', color: Colors.text.primary, marginBottom: 2 },
  metricLabel: { fontSize: 11, fontWeight: '600', color: Colors.text.secondary, textAlign: 'center' },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, marginTop: 16 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: Colors.text.primary },
  statsRow: { flexDirection: 'row', gap: 10 },
  statCard: { flex: 1, backgroundColor: Colors.card.white, borderRadius: 14, padding: 14, alignItems: 'center', shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  statIconBox: { width: 32, height: 32, borderRadius: 16, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  statValue: { fontSize: 18, fontWeight: '800', color: Colors.text.primary, marginBottom: 2 },
  statLabel: { fontSize: 10, fontWeight: '600', color: Colors.text.secondary, textAlign: 'center' },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  actionCard: { width: (width - 32 - 10) / 2, backgroundColor: Colors.card.white, borderRadius: 14, padding: 16, alignItems: 'center', shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  actionIconBox: { width: 42, height: 42, borderRadius: 21, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  actionLabel: { fontSize: 12, fontWeight: '600', color: Colors.text.primary },
  certSection: { backgroundColor: Colors.card.white, borderRadius: 14, padding: 14, shadowColor: Colors.card.shadow, shadowOffset: { width: 0, height: 2 }, shadowOpacity: 1, shadowRadius: 8, elevation: 3 },
  certRow: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: Colors.border.light },
  certText: { fontSize: 13, color: Colors.text.primary, fontWeight: '500' },
});

export default DriverDashboard;
