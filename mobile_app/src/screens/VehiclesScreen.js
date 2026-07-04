import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { useTheme } from '../context/ThemeContext';
import { useVehicles } from '../context/VehicleContext';

const getDynamicStyles = (colors) => {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background.secondary,
    },
    scrollView: {
      flex: 1,
    },
    header: {
      paddingHorizontal: GlassTokens.spacing.lg,
      paddingVertical: GlassTokens.spacing.xl,
      borderBottomWidth: 1,
      borderBottomColor: colors.border.light,
    },
    headerTitle: {
      ...GlobalStyles.headerTitle,
      color: colors.text.primary,
    },
    headerSubtitle: {
      ...GlobalStyles.headerSubtitle,
    },
    statsContainer: {
      flexDirection: 'row',
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.lg,
      gap: GlassTokens.spacing.md,
    },
    statCard: {
      flex: 1,
      ...GlobalStyles.card,
      alignItems: 'center',
    },
    statValue: {
      ...GlobalStyles.title,
      color: colors.primary,
      marginTop: GlassTokens.spacing.sm,
    },
    statLabel: {
      ...GlobalStyles.caption,
      marginTop: GlassTokens.spacing.xs,
    },
    section: {
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.sm,
    },
    vehicleCard: {
      ...GlobalStyles.card,
      marginBottom: GlassTokens.spacing.md,
    },
    vehicleHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: GlassTokens.spacing.md,
    },
    vehicleInfo: {
      flex: 1,
    },
    vehicleName: {
      ...GlobalStyles.subtitle,
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.xs,
    },
    vehiclePlate: {
      ...GlobalStyles.caption,
    },
    statusBadge: {
      ...GlobalStyles.badge,
      marginLeft: GlassTokens.spacing.md,
    },
    statusText: {
      ...GlobalStyles.badgeText,
      color: '#ffffff',
    },
    vehicleStats: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.md,
      backgroundColor: colors.background.tertiary,
      borderRadius: GlassTokens.radius.md,
      marginBottom: GlassTokens.spacing.md,
    },
    statItem: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.sm,
    },
    statText: {
      ...GlobalStyles.caption,
    },
    statDivider: {
      width: 1,
      height: 20,
      backgroundColor: colors.border.light,
      marginHorizontal: GlassTokens.spacing.md,
    },
    documentsSection: {
      backgroundColor: colors.background.tertiary,
      borderRadius: GlassTokens.radius.md,
      padding: GlassTokens.spacing.md,
      marginBottom: GlassTokens.spacing.md,
    },
    documentsTitle: {
      ...GlobalStyles.subtitle,
      color: colors.primary,
      marginBottom: GlassTokens.spacing.md,
      fontWeight: '600',
    },
    documentRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: GlassTokens.spacing.sm,
      borderBottomWidth: 1,
      borderBottomColor: colors.border.light,
    },
    documentInfo: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.sm,
    },
    documentDetails: {
      flex: 1,
    },
    documentName: {
      ...GlobalStyles.body,
      fontWeight: '600',
    },
    documentExpiry: {
      ...GlobalStyles.caption,
      marginTop: GlassTokens.spacing.xs,
    },
    docStatusBadge: {
      paddingHorizontal: GlassTokens.spacing.sm,
      paddingVertical: GlassTokens.spacing.xs,
      borderRadius: GlassTokens.radius.sm,
    },
    docStatusText: {
      ...GlobalStyles.badgeText,
      color: '#ffffff',
      fontSize: 10,
    },
    actionButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.lg,
      backgroundColor: colors.primaryLight,
      borderRadius: GlassTokens.radius.md,
      gap: GlassTokens.spacing.sm,
    },
    actionButtonText: {
      ...GlobalStyles.buttonText,
      color: colors.primary,
      fontSize: 12,
      fontWeight: '600',
    },
    actionsSection: {
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.lg,
    },
    sectionTitle: {
      ...GlobalStyles.subtitle,
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.lg,
    },
    actionsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: GlassTokens.spacing.md,
    },
    quickActionCard: {
      width: '48%',
      ...GlobalStyles.card,
      alignItems: 'center',
    },
    quickActionLabel: {
      ...GlobalStyles.caption,
      marginTop: GlassTokens.spacing.sm,
      textAlign: 'center',
      fontWeight: '600',
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingVertical: GlassTokens.spacing.xl,
    },
    loadingText: {
      ...GlobalStyles.body,
      marginTop: GlassTokens.spacing.md,
    },
    errorContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingHorizontal: GlassTokens.spacing.xl,
      paddingVertical: GlassTokens.spacing.xl,
    },
    errorTitle: {
      ...GlobalStyles.title,
      marginTop: GlassTokens.spacing.lg,
      marginBottom: GlassTokens.spacing.md,
    },
    errorMessage: {
      ...GlobalStyles.body,
      textAlign: 'center',
      marginBottom: GlassTokens.spacing.xl,
    },
    retryButton: {
      ...GlobalStyles.buttonPrimary,
    },
    retryButtonText: {
      ...GlobalStyles.buttonText,
    },
  });
};

export const VehiclesScreen = () => {
  const { colors, isDarkMode } = useTheme();
  const dynamicStyles = getDynamicStyles(colors);
  const { assignedVehicles, loadingVehicles, vehicleError } = useVehicles();

  // Use assigned vehicles from context, fallback to empty array
  const vehicles = assignedVehicles && assignedVehicles.length > 0
    ? assignedVehicles
    : [];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return colors.primary;
      case 'Maintenance':
        return colors.icon.warning;
      case 'Inactive':
        return colors.icon.danger;
      default:
        return colors.text.secondary;
    }
  };

  const getDocumentColor = (status) => {
    switch (status) {
      case 'Valid':
        return colors.icon.success;
      case 'Soon':
        return colors.icon.warning;
      case 'Expired':
        return colors.icon.danger;
      default:
        return colors.text.secondary;
    }
  };

  const renderVehicleCard = ({ item }) => (
    <View style={dynamicStyles.vehicleCard}>
      <View style={dynamicStyles.vehicleHeader}>
        <View style={dynamicStyles.vehicleInfo}>
          <Text style={dynamicStyles.vehicleName}>{item.name}</Text>
          <Text style={dynamicStyles.vehiclePlate}>{item.plate}</Text>
        </View>
        <View style={[dynamicStyles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={dynamicStyles.statusText}>{item.status}</Text>
        </View>
      </View>

      <View style={dynamicStyles.vehicleStats}>
        <View style={dynamicStyles.statItem}>
          <MaterialCommunityIcons name="speedometer" size={18} color={colors.primary} />
          <Text style={dynamicStyles.statText}>{item.mileage}</Text>
        </View>
        <View style={dynamicStyles.statDivider} />
        <View style={dynamicStyles.statItem}>
          <MaterialCommunityIcons name="gas-cylinder" size={18} color={colors.primary} />
          <Text style={dynamicStyles.statText}>{item.fuel}</Text>
        </View>
      </View>

      <View style={dynamicStyles.documentsSection}>
        <Text style={dynamicStyles.documentsTitle}>Documents</Text>
        {item.documents.map((doc, index) => (
          <View key={index} style={dynamicStyles.documentRow}>
            <View style={dynamicStyles.documentInfo}>
              <MaterialCommunityIcons name="file-document" size={16} color={colors.primary} />
              <View style={dynamicStyles.documentDetails}>
                <Text style={dynamicStyles.documentName}>{doc.name}</Text>
                <Text style={dynamicStyles.documentExpiry}>Expires: {doc.expiry}</Text>
              </View>
            </View>
            <View style={[dynamicStyles.docStatusBadge, { backgroundColor: getDocumentColor(doc.status) }]}>
              <Text style={dynamicStyles.docStatusText}>{doc.status}</Text>
            </View>
          </View>
        ))}
      </View>

      <TouchableOpacity
        style={dynamicStyles.actionButton}
        onPress={() => Alert.alert('Edit Vehicle', `Editing ${item.name}\n\nUpdate vehicle information, maintenance schedule, or insurance details`, [
          { text: 'Save Changes', onPress: () => Alert.alert('Success', 'Vehicle details updated!') },
          { text: 'Cancel', onPress: () => {} }
        ])}
      >
        <MaterialCommunityIcons name="pencil" size={18} color={colors.primary} />
        <Text style={dynamicStyles.actionButtonText}>Edit Details</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={dynamicStyles.container}>
      {loadingVehicles && (
        <View style={dynamicStyles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={dynamicStyles.loadingText}>Loading vehicles...</Text>
        </View>
      )}

      {vehicleError && (
        <View style={dynamicStyles.errorContainer}>
          <MaterialCommunityIcons name="alert-circle" size={48} color={colors.icon.danger} />
          <Text style={dynamicStyles.errorTitle}>Unable to Load Vehicles</Text>
          <Text style={dynamicStyles.errorMessage}>{vehicleError}</Text>
          <TouchableOpacity
            style={dynamicStyles.retryButton}
            onPress={() => {
              // Retry fetching vehicles
            }}
          >
            <Text style={dynamicStyles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      )}

      {!loadingVehicles && !vehicleError && (
        <ScrollView style={dynamicStyles.scrollView}>
          {/* Section Header */}
          <View style={dynamicStyles.header}>
            <Text style={dynamicStyles.headerTitle}>My Vehicles</Text>
            <Text style={dynamicStyles.headerSubtitle}>{vehicles.length} Vehicles Assigned</Text>
          </View>

        {/* Quick Stats */}
        <View style={dynamicStyles.statsContainer}>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="car" size={24} color={colors.primary} />
            <Text style={dynamicStyles.statValue}>{vehicles.length}</Text>
            <Text style={dynamicStyles.statLabel}>Total</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="check-circle" size={24} color={colors.icon.success} />
            <Text style={dynamicStyles.statValue}>{vehicles.filter(v => v.status === 'Active').length}</Text>
            <Text style={dynamicStyles.statLabel}>Active</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="wrench" size={24} color={colors.icon.warning} />
            <Text style={dynamicStyles.statValue}>{vehicles.filter(v => v.status === 'Maintenance').length}</Text>
            <Text style={dynamicStyles.statLabel}>Maintenance</Text>
          </View>
        </View>

        {/* Vehicles List */}
        <View style={dynamicStyles.section}>
          <FlatList
            data={vehicles}
            renderItem={renderVehicleCard}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
          />
        </View>

        {/* Quick Actions */}
        <View style={dynamicStyles.actionsSection}>
          <Text style={dynamicStyles.sectionTitle}>Quick Actions</Text>
          <View style={dynamicStyles.actionsGrid}>
            <TouchableOpacity
              style={dynamicStyles.quickActionCard}
              onPress={() => Alert.alert('Start Trip', 'Enter trip details:\n• Destination\n• Expected Duration\n• Mileage\n\nReady to start?', [
                { text: 'Start', onPress: () => Alert.alert('Success', 'Trip started! GPS tracking active') },
                { text: 'Cancel', onPress: () => {} }
              ])}
            >
              <MaterialCommunityIcons name="map-marker" size={28} color={colors.primary} />
              <Text style={dynamicStyles.quickActionLabel}>Start Trip</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={dynamicStyles.quickActionCard}
              onPress={() => Alert.alert('Fuel Log', 'Log fuel entry:\n• Liters: ___\n• Cost: ___\n• Mileage: ___', [
                { text: 'Save', onPress: () => Alert.alert('Success', 'Fuel entry recorded!') },
                { text: 'Cancel', onPress: () => {} }
              ])}
            >
              <MaterialCommunityIcons name="gas-cylinder" size={28} color={colors.primary} />
              <Text style={dynamicStyles.quickActionLabel}>Fuel Log</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={dynamicStyles.quickActionCard}
              onPress={() => Alert.alert('Maintenance', 'Schedule maintenance:\n• Service Type\n• Date\n• Details\n\nSubmit request?', [
                { text: 'Schedule', onPress: () => Alert.alert('Success', 'Maintenance scheduled!') },
                { text: 'Cancel', onPress: () => {} }
              ])}
            >
              <MaterialCommunityIcons name="wrench" size={28} color={colors.primary} />
              <Text style={dynamicStyles.quickActionLabel}>Maintenance</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={dynamicStyles.quickActionCard}
              onPress={() => Alert.alert('Documents', 'Vehicle Documents:\n✓ RC Certificate\n✓ Insurance\n✓ Pollution Check\n✓ Service Record', [
                { text: 'View All', onPress: () => Alert.alert('Documents', 'All documents displayed above') },
                { text: 'Download', onPress: () => Alert.alert('Success', 'Documents downloaded!') },
                { text: 'Close', onPress: () => {} }
              ])}
            >
              <MaterialCommunityIcons name="document" size={28} color={colors.primary} />
              <Text style={dynamicStyles.quickActionLabel}>Documents</Text>
            </TouchableOpacity>
          </View>
        </View>

          <View style={{ height: 20 }} />
        </ScrollView>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({});
