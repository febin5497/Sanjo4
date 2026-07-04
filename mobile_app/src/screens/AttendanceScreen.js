import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  ScrollView,
  Modal,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as SecureStore from 'expo-secure-store';
import * as Location from 'expo-location';
import { CameraModal } from '../components/CameraModal';
import { attendanceAPI } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { useProject } from '../context/ProjectContext';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';

const { width } = Dimensions.get('window');

const getDynamicStyles = (colors) => {
  return StyleSheet.create({
    container: {
      ...GlobalStyles.container,
      backgroundColor: colors.background.primary,
    },
    scrollView: {
      flex: 1,
      backgroundColor: colors.background.primary,
    },
    titleSection: {
      paddingHorizontal: GlassTokens.spacing.lg,
      paddingTop: GlassTokens.spacing.md,
      paddingBottom: GlassTokens.spacing.md,
    },
    pageTitle: {
      ...GlobalStyles.headerTitle,
      color: colors.text.primary,
    },
    statusCard: {
      marginHorizontal: GlassTokens.spacing.lg,
      marginBottom: GlassTokens.spacing.xl,
      backgroundColor: colors.card.white,
      borderRadius: 24,
      borderWidth: 1.5,
      borderColor: colors.border.light,
      padding: GlassTokens.spacing.lg,
      shadowColor: colors.shadow.md,
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.12,
      shadowRadius: 16,
      elevation: 6,
    },
    statusIconRow: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.sm,
      marginBottom: GlassTokens.spacing.lg,
    },
    statusCardTitle: {
      fontSize: 14,
      fontWeight: '600',
      color: colors.text.secondary,
      textTransform: 'uppercase',
      letterSpacing: 0.5,
    },
    statusBadgeContainer: {
      paddingVertical: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.lg,
      borderRadius: 16,
      alignItems: 'center',
      justifyContent: 'center',
    },
    statusBadgePunchedIn: {
      backgroundColor: colors.icon.success,
      shadowColor: colors.glow.green,
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.25,
      shadowRadius: 12,
      elevation: 6,
      borderWidth: 1,
      borderColor: colors.icon.success,
    },
    statusBadgePunchedOut: {
      backgroundColor: colors.icon.danger,
      shadowColor: colors.glow.red,
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.25,
      shadowRadius: 12,
      elevation: 6,
      borderWidth: 1,
      borderColor: colors.icon.danger,
    },
    statusBadgeTextLarge: {
      fontSize: 18,
      fontWeight: '800',
      color: colors.text.inverse,
      letterSpacing: 1,
    },
    largeButtonContainer: {
      paddingHorizontal: GlassTokens.spacing.lg,
      marginBottom: GlassTokens.spacing.xl,
      alignItems: 'center',
    },
    largeButton: {
      width: '100%',
      paddingVertical: 18,
      paddingHorizontal: GlassTokens.spacing.lg,
      borderRadius: 18,
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 68,
    },
    largePunchInButton: {
      backgroundColor: colors.icon.success,
      shadowColor: colors.glow.green,
      shadowOffset: { width: 0, height: 12 },
      shadowOpacity: 0.35,
      shadowRadius: 20,
      elevation: 12,
      borderWidth: 1,
      borderColor: colors.icon.success,
    },
    largePunchOutButton: {
      backgroundColor: colors.icon.danger,
      shadowColor: colors.glow.red,
      shadowOffset: { width: 0, height: 12 },
      shadowOpacity: 0.35,
      shadowRadius: 20,
      elevation: 12,
      borderWidth: 1,
      borderColor: colors.icon.danger,
    },
    buttonDisabled: {
      opacity: 0.7,
    },
    largeButtonText: {
      fontSize: 18,
      fontWeight: '800',
      color: colors.text.inverse,
      letterSpacing: 1.5,
    },
    buttonSubtext: {
      fontSize: 11,
      color: 'rgba(255, 255, 255, 0.7)',
      marginTop: GlassTokens.spacing.xs,
      fontWeight: '500',
    },
    statsSection: {
      paddingHorizontal: GlassTokens.spacing.lg,
      marginBottom: GlassTokens.spacing.xl,
    },
    statsSectionTitle: {
      fontSize: 16,
      fontWeight: '700',
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.lg,
      letterSpacing: -0.3,
    },
    statsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: GlassTokens.spacing.md,
      justifyContent: 'space-between',
    },
    statCard: {
      width: (Dimensions.get('window').width - GlassTokens.spacing.lg * 2 - GlassTokens.spacing.md) / 2,
      backgroundColor: colors.card.white,
      borderRadius: 20,
      borderWidth: 1.5,
      borderColor: colors.border.light,
      paddingVertical: GlassTokens.spacing.lg,
      paddingHorizontal: GlassTokens.spacing.md,
      alignItems: 'center',
      justifyContent: 'center',
      shadowColor: colors.shadow.sm,
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.1,
      shadowRadius: 12,
      elevation: 4,
    },
    statIconBox: {
      width: 56,
      height: 56,
      borderRadius: GlassTokens.radius.lg,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colors.card.white,
      borderWidth: 1,
      borderColor: colors.border.light,
      marginBottom: GlassTokens.spacing.md,
    },
    statCardValue: {
      fontSize: 26,
      fontWeight: '800',
      color: colors.primary,
      marginBottom: GlassTokens.spacing.xs,
      letterSpacing: -0.5,
    },
    statCardLabel: {
      fontSize: 10,
      fontWeight: '700',
      color: colors.text.secondary,
      textTransform: 'uppercase',
      letterSpacing: 0.5,
    },
    locationBar: {
      marginHorizontal: GlassTokens.spacing.lg,
      marginBottom: GlassTokens.spacing.lg,
      paddingVertical: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.lg,
      backgroundColor: colors.primary,
      borderRadius: 16,
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.md,
      shadowColor: colors.glow.blue,
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.25,
      shadowRadius: 16,
      elevation: 8,
      borderWidth: 1,
      borderColor: colors.primaryLight,
    },
    locationBarText: {
      flex: 1,
      fontSize: 13,
      fontWeight: '600',
      color: colors.text.inverse,
      letterSpacing: 0.3,
    },
    spacer: {
      height: 30,
    },
  });
};

export const AttendanceScreen = () => {
  const { colors, isDarkMode } = useTheme();
  const { selectedProject } = useProject();
  const dynamicStyles = getDynamicStyles(colors);
  const [staffId, setStaffId] = useState(null);
  const [currentStatus, setCurrentStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [attendanceHistory, setAttendanceHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [showCamera, setShowCamera] = useState(false);
  const [cameraCallback, setCameraCallback] = useState(null);

  // Get punched in status - user is punched in if punch_out is enabled (approved punch_in exists)
  const isPunchedIn = currentStatus?.punch_out_enabled === true;

  // Get pending approval status from nested punch_in object
  const hasPendingApproval = currentStatus?.punch_in?.status === 'pending';

  console.log('Attendance Status:', { isPunchedIn, hasPendingApproval, punch_in_status: currentStatus?.punch_in?.status });

  useEffect(() => {
    bootstrapAsync();
  }, []);

  const bootstrapAsync = async () => {
    try {
      const staffId = await SecureStore.getItemAsync('staff_id');
      console.log('Retrieved staff_id from storage:', staffId);
      if (staffId) {
        const numId = parseInt(staffId);
        console.log('Parsed staff_id:', numId);
        setStaffId(numId);
        await fetchCurrentStatus(numId);
        await fetchAttendanceHistory(numId);
        await fetchStats(numId);
      } else {
        console.log('No staff_id found in storage');
      }
    } catch (error) {
      console.log('Error bootstrapping:', error);
    }
  };

  const fetchCurrentStatus = async (id) => {
    try {
      const response = await attendanceAPI.getCurrentStatus(id);
      console.log('Current Status Response:', JSON.stringify(response, null, 2));
      if (response && response.success) {
        // The response contains punch_in status, not is_punched_in
        setCurrentStatus(response);
        console.log('Updated currentStatus with pending check:', response.punch_in?.status === 'pending');
      } else {
        setCurrentStatus({
          punch_in: null,
          punch_out_enabled: false,
        });
      }
    } catch (error) {
      console.log('Error fetching status:', error);
      setCurrentStatus({
        punch_in: null,
        punch_out_enabled: false,
      });
    }
  };

  const fetchAttendanceHistory = async (id) => {
    try {
      const today = new Date();
      const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

      const response = await attendanceAPI.getAttendanceHistory(
        id,
        thirtyDaysAgo.toISOString().split('T')[0],
        today.toISOString().split('T')[0]
      );

      if (response && response.success && Array.isArray(response.data)) {
        setAttendanceHistory(response.data);
      } else {
        setAttendanceHistory([]);
      }
    } catch (error) {
      console.log('Error fetching history:', error);
      setAttendanceHistory([]);
    }
  };

  const fetchStats = async (id) => {
    try {
      console.log('Fetching stats for staff_id:', id);

      // Don't pass dates, let the backend use defaults
      const response = await attendanceAPI.getAttendanceStats(id, null, null);

      if (response && response.success && response.data) {
        setStats(response.data);
      } else {
        setStats({
          present_days: 0,
          absent_days: 0,
          half_days: 0,
          night_shifts: 0,
          total_overtime_hours: 0,
          attendance_percentage: 0,
        });
      }
    } catch (error) {
      console.log('Error fetching stats:', error);
      setStats({
        present_days: 0,
        absent_days: 0,
        half_days: 0,
        night_shifts: 0,
        total_overtime_hours: 0,
        attendance_percentage: 0,
      });
    }
  };

  const pickImage = async (callback) => {
    try {
      // Request camera permission
      const { status: cameraStatus } = await requestCameraPermissions();
      if (cameraStatus !== 'granted') {
        Alert.alert('Permission', 'Camera permission is required');
        return null;
      }

      // Request location permission
      const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
      if (locationStatus !== 'granted') {
        Alert.alert('Permission', 'Location permission is required for attendance tracking');
        return null;
      }

      // Get current location
      let locationData = null;
      try {
        const location = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
        });
        locationData = {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          accuracy: location.coords.accuracy,
        };
        console.log('Location captured:', locationData);
      } catch (locationError) {
        console.log('Location error:', locationError);
      }

      // Store the callback and location data for when camera captures
      setCameraCallback(() => (photoUri) => {
        callback({
          uri: photoUri,
          location: locationData,
        });
      });

      // Show camera modal
      setShowCamera(true);
    } catch (error) {
      console.log('Camera setup error:', error);
      Alert.alert('Error', 'Failed to setup camera: ' + error.message);
      return null;
    }
  };

  const requestCameraPermissions = async () => {
    try {
      const { Camera } = require('expo-camera');
      const { status } = await Camera.requestCameraPermissionsAsync();
      return { status };
    } catch (error) {
      console.log('Camera permission error:', error);
      return { status: 'denied' };
    }
  };

  const handleCameraCapture = (photoUri) => {
    setShowCamera(false);
    if (cameraCallback) {
      cameraCallback(photoUri);
    }
  };

  const handlePunchIn = async () => {
    // Prevent multiple submissions
    if (isLoading) {
      console.log('Punch in already in progress, ignoring duplicate click');
      return;
    }

    if (!staffId) {
      Alert.alert('Error', 'Staff ID not found');
      return;
    }

    if (isPunchedIn) {
      Alert.alert('Already Punched In', 'You are already punched in. Please punch out first.');
      return;
    }

    // Check if there's a pending photo approval
    if (hasPendingApproval) {
      Alert.alert(
        'Pending Approval',
        'Your photo is waiting for approval. Please wait for it to be approved or rejected before submitting another punch in.'
      );
      return;
    }

    // Check if photo was rejected - allow resubmit
    if (currentStatus?.punch_in?.status === 'rejected') {
      Alert.alert('Photo Rejected', 'Your previous photo was rejected. You can resubmit a new punch in now.');
    }

    setIsLoading(true);

    // Use callback to handle photo after capture
    pickImage(async (photoData) => {
      try {
        if (!photoData) {
          Alert.alert('Note', 'A selfie photo (front camera) is required for punch in');
          setIsLoading(false);
          return;
        }

        const response = await attendanceAPI.punchIn(staffId, photoData.uri, photoData.location, selectedProject?.id);

        if (response.data?.success || response.success) {
          Alert.alert('Success', 'Punched in successfully with location tracking');
          await fetchCurrentStatus(staffId);
        } else {
          Alert.alert('Error', response.data?.message || response.message || 'Punch in failed');
        }
      } catch (error) {
        const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || 'An error occurred';
        console.log('Error Details:', { message: errorMsg, status: error.response?.status });
        Alert.alert('Error', errorMsg);
      } finally {
        setIsLoading(false);
      }
    });
  };

  const handlePunchOut = async () => {
    // Prevent multiple submissions
    if (isLoading) {
      console.log('Punch out already in progress, ignoring duplicate click');
      return;
    }

    if (!staffId) {
      Alert.alert('Error', 'Staff ID not found');
      return;
    }

    if (!isPunchedIn) {
      Alert.alert('Not Punched In', 'You need to punch in first before you can punch out.');
      return;
    }

    setIsLoading(true);

    try {
      console.log('Punch Out - Staff ID:', staffId);
      const response = await attendanceAPI.punchOut(staffId);

      if (response.data?.success || response.success) {
        Alert.alert('Success', 'Punched out successfully');
        await fetchCurrentStatus(staffId);
      } else {
        Alert.alert('Error', response.data?.message || response.message || 'Punch out failed');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || 'An error occurred';
      console.log('Punch Out Error:', errorMsg);
      Alert.alert('Error', errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={dynamicStyles.container}>
      <ScrollView style={dynamicStyles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Page Title - Attendance */}
        <View style={dynamicStyles.titleSection}>
          <Text style={dynamicStyles.pageTitle}>Attendance</Text>
        </View>

        {/* Current Status Card - Exactly like mockup */}
        <View style={dynamicStyles.statusCard}>
          <View style={dynamicStyles.statusIconRow}>
            <MaterialIcons name="schedule" size={20} color={colors.primary} />
            <Text style={dynamicStyles.statusCardTitle}>Current Status</Text>
          </View>

          <View style={[dynamicStyles.statusBadgeContainer, isPunchedIn ? dynamicStyles.statusBadgePunchedIn : dynamicStyles.statusBadgePunchedOut]}>
            <Text style={dynamicStyles.statusBadgeTextLarge}>
              {isPunchedIn ? 'PUNCHED IN' : 'PUNCHED OUT'}
            </Text>
          </View>
        </View>

        {/* Large Punch Button - Exactly like mockup (3D effect) */}
        <View style={dynamicStyles.largeButtonContainer}>
          {!isPunchedIn ? (
            <>
              <TouchableOpacity
                style={[
                  dynamicStyles.largeButton,
                  dynamicStyles.largePunchInButton,
                  (isLoading || hasPendingApproval) && dynamicStyles.buttonDisabled,
                ]}
                onPress={handlePunchIn}
                disabled={isLoading || hasPendingApproval}
                activeOpacity={0.8}
              >
                {isLoading ? (
                  <ActivityIndicator color="#fff" size={40} />
                ) : (
                  <>
                    <Text style={dynamicStyles.largeButtonText}>Punch In</Text>
                    {hasPendingApproval && (
                      <Text style={dynamicStyles.buttonSubtext}>⏳ Waiting for approval</Text>
                    )}
                  </>
                )}
              </TouchableOpacity>
            </>
          ) : (
            <TouchableOpacity
              style={[dynamicStyles.largeButton, dynamicStyles.largePunchOutButton, isLoading && dynamicStyles.buttonDisabled]}
              onPress={handlePunchOut}
              disabled={isLoading}
              activeOpacity={0.8}
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" size={40} />
              ) : (
                <Text style={dynamicStyles.largeButtonText}>Punch Out</Text>
              )}
            </TouchableOpacity>
          )}
        </View>

        {/* Statistics Section - 2x2 Grid exactly like mockup */}
        {stats && (
          <View style={dynamicStyles.statsSection}>
            <Text style={dynamicStyles.statsSectionTitle}>Statistics (30 Days)</Text>
            <View style={dynamicStyles.statsGrid}>
              {/* Present */}
              <View style={dynamicStyles.statCard}>
                <View style={dynamicStyles.statIconBox}>
                  <MaterialIcons name="check" size={28} color={colors.icon.success} />
                </View>
                <Text style={dynamicStyles.statCardValue}>{stats.present_days}</Text>
                <Text style={dynamicStyles.statCardLabel}>PRESENT</Text>
              </View>

              {/* Absent */}
              <View style={dynamicStyles.statCard}>
                <View style={dynamicStyles.statIconBox}>
                  <MaterialIcons name="close" size={28} color={colors.icon.danger} />
                </View>
                <Text style={dynamicStyles.statCardValue}>{stats.absent_days}</Text>
                <Text style={dynamicStyles.statCardLabel}>ABSENT</Text>
              </View>

              {/* Half Day */}
              <View style={dynamicStyles.statCard}>
                <View style={dynamicStyles.statIconBox}>
                  <MaterialIcons name="schedule" size={28} color={colors.icon.warning} />
                </View>
                <Text style={dynamicStyles.statCardValue}>{stats.half_days}</Text>
                <Text style={dynamicStyles.statCardLabel}>HALF DAY</Text>
              </View>

              {/* Attendance % */}
              <View style={dynamicStyles.statCard}>
                <View style={dynamicStyles.statIconBox}>
                  <MaterialIcons name="event" size={28} color={colors.primary} />
                </View>
                <Text style={dynamicStyles.statCardValue}>{stats.attendance_percentage}%</Text>
                <Text style={dynamicStyles.statCardLabel}>ATTENDANCE %</Text>
              </View>
            </View>
          </View>
        )}

        {/* Location Display */}
        <View style={dynamicStyles.locationBar}>
          <MaterialIcons name="location-on" size={18} color="#fff" />
          <Text style={dynamicStyles.locationBarText}>Technopark, Trivandrum</Text>
          <MaterialIcons name="chevron-right" size={18} color="#fff" />
        </View>

        <View style={dynamicStyles.spacer} />
      </ScrollView>

      {/* Front Camera Modal */}
      <Modal
        visible={showCamera}
        animationType="slide"
        transparent={false}
      >
        <CameraModal
          onCapture={handleCameraCapture}
          onCancel={() => {
            setShowCamera(false);
            setIsLoading(false);
          }}
        />
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({});
