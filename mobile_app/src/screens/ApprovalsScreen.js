import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { useTheme } from '../context/ThemeContext';

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
      paddingVertical: GlassTokens.spacing.md,
    },
    sectionTitle: {
      ...GlobalStyles.subtitle,
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.lg,
    },
    approvalCard: {
      ...GlobalStyles.card,
      marginBottom: GlassTokens.spacing.md,
    },
    approvalHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: GlassTokens.spacing.md,
    },
    approvalTypeSection: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.md,
    },
    typeIcon: {
      fontSize: 28,
    },
    approvalInfo: {
      flex: 1,
    },
    approvalType: {
      ...GlobalStyles.body,
      fontWeight: '700',
      color: colors.text.primary,
    },
    staffName: {
      ...GlobalStyles.caption,
      marginTop: GlassTokens.spacing.xs,
    },
    statusBadge: {
      ...GlobalStyles.badge,
      marginLeft: GlassTokens.spacing.md,
    },
    statusText: {
      ...GlobalStyles.badgeText,
      color: colors.text.inverse,
    },
    approvalDetails: {
      backgroundColor: colors.background.tertiary,
      borderRadius: GlassTokens.radius.md,
      padding: GlassTokens.spacing.md,
      marginBottom: GlassTokens.spacing.md,
      gap: GlassTokens.spacing.sm,
    },
    detailItem: {
      flexDirection: 'row',
      alignItems: 'flex-start',
      gap: GlassTokens.spacing.sm,
    },
    detailText: {
      ...GlobalStyles.caption,
      flex: 1,
    },
    actionButtons: {
      flexDirection: 'row',
      gap: GlassTokens.spacing.md,
    },
    button: {
      flex: 1,
      flexDirection: 'row',
      justifyContent: 'center',
      alignItems: 'center',
      paddingVertical: GlassTokens.spacing.md,
      borderRadius: GlassTokens.radius.md,
      gap: GlassTokens.spacing.sm,
    },
    approveButton: {
      ...GlobalStyles.buttonPrimary,
    },
    approveButtonText: {
      ...GlobalStyles.buttonText,
      fontSize: 12,
    },
    rejectButton: {
      backgroundColor: colors.icon.danger,
    },
    rejectButtonText: {
      ...GlobalStyles.buttonText,
      color: colors.text.inverse,
      fontSize: 12,
    },
    statusInfo: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: GlassTokens.spacing.md,
      borderRadius: GlassTokens.radius.md,
      gap: GlassTokens.spacing.sm,
    },
    statusInfoText: {
      ...GlobalStyles.body,
      fontWeight: '600',
      color: colors.text.inverse,
    },
    emptySection: {
      paddingVertical: GlassTokens.spacing.xxl,
      alignItems: 'center',
      justifyContent: 'center',
    },
    emptyTitle: {
      ...GlobalStyles.subtitle,
      color: colors.icon.success,
      marginTop: GlassTokens.spacing.lg,
    },
    emptyText: {
      ...GlobalStyles.body,
      color: colors.text.secondary,
      marginTop: GlassTokens.spacing.sm,
    },
  });
};

export const ApprovalsScreen = () => {
  const { colors, isDarkMode } = useTheme();
  const dynamicStyles = getDynamicStyles(colors);
  const [approvals, setApprovals] = useState([
    {
      id: 1,
      type: 'Leave Request',
      staffName: 'Rajesh Kumar',
      date: '2026-03-20',
      reason: 'Sick Leave - 2 Days',
      status: 'Pending',
      startDate: '2026-03-21',
      endDate: '2026-03-22',
    },
    {
      id: 2,
      type: 'Expense Claim',
      staffName: 'Priya Singh',
      date: '2026-03-19',
      reason: 'Materials Purchase - ₹15,000',
      status: 'Pending',
      amount: 15000,
    },
    {
      id: 3,
      type: 'Overtime',
      staffName: 'Amit Patel',
      date: '2026-03-18',
      reason: 'Extra 4 hours - Emergency Work',
      status: 'Pending',
      hours: 4,
    },
    {
      id: 4,
      type: 'Leave Request',
      staffName: 'Neha Sharma',
      date: '2026-03-17',
      reason: 'Annual Leave - 5 Days',
      status: 'Approved',
      startDate: '2026-04-01',
      endDate: '2026-04-05',
    },
    {
      id: 5,
      type: 'Expense Claim',
      staffName: 'Vikram Reddy',
      date: '2026-03-16',
      reason: 'Safety Equipment - ₹5,000',
      status: 'Rejected',
      amount: 5000,
    },
  ]);

  const getTypeIcon = (type) => {
    switch (type) {
      case 'Leave Request':
        return '🏖️';
      case 'Expense Claim':
        return '💰';
      case 'Overtime':
        return '⏰';
      case 'Salary Adjustment':
        return '💵';
      default:
        return '📋';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Approved':
        return colors.icon.success;
      case 'Pending':
        return colors.icon.warning;
      case 'Rejected':
        return colors.icon.danger;
      default:
        return colors.text.secondary;
    }
  };

  const handleApprove = (id) => {
    Alert.alert('Approve Request', 'Are you sure you want to approve this request?', [
      { text: 'Cancel', onPress: () => {} },
      {
        text: 'Approve',
        onPress: () => {
          setApprovals(
            approvals.map(item =>
              item.id === id ? { ...item, status: 'Approved' } : item
            )
          );
          Alert.alert('Success', 'Request approved successfully');
        },
      },
    ]);
  };

  const handleReject = (id) => {
    Alert.alert('Reject Request', 'Are you sure you want to reject this request?', [
      { text: 'Cancel', onPress: () => {} },
      {
        text: 'Reject',
        onPress: () => {
          setApprovals(
            approvals.map(item =>
              item.id === id ? { ...item, status: 'Rejected' } : item
            )
          );
          Alert.alert('Success', 'Request rejected');
        },
      },
    ]);
  };

  const pendingCount = approvals.filter(a => a.status === 'Pending').length;
  const approvedCount = approvals.filter(a => a.status === 'Approved').length;
  const rejectedCount = approvals.filter(a => a.status === 'Rejected').length;

  const renderApprovalCard = ({ item }) => (
    <View style={dynamicStyles.approvalCard}>
      <View style={dynamicStyles.approvalHeader}>
        <View style={dynamicStyles.approvalTypeSection}>
          <Text style={dynamicStyles.typeIcon}>{getTypeIcon(item.type)}</Text>
          <View style={dynamicStyles.approvalInfo}>
            <Text style={dynamicStyles.approvalType}>{item.type}</Text>
            <Text style={dynamicStyles.staffName}>{item.staffName}</Text>
          </View>
        </View>
        <View style={[dynamicStyles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={dynamicStyles.statusText}>{item.status}</Text>
        </View>
      </View>

      <View style={dynamicStyles.approvalDetails}>
        <View style={dynamicStyles.detailItem}>
          <MaterialCommunityIcons name="calendar" size={14} color={colors.text.secondary} />
          <Text style={dynamicStyles.detailText}>Requested: {new Date(item.date).toLocaleDateString()}</Text>
        </View>
        <View style={dynamicStyles.detailItem}>
          <MaterialCommunityIcons name="note-text" size={14} color={colors.text.secondary} />
          <Text style={dynamicStyles.detailText}>{item.reason}</Text>
        </View>
      </View>

      {item.status === 'Pending' && (
        <View style={dynamicStyles.actionButtons}>
          <TouchableOpacity
            style={[dynamicStyles.button, dynamicStyles.rejectButton]}
            onPress={() => handleReject(item.id)}
          >
            <MaterialCommunityIcons name="close" size={16} color={colors.icon.danger} />
            <Text style={dynamicStyles.rejectButtonText}>Reject</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[dynamicStyles.button, dynamicStyles.approveButton]}
            onPress={() => handleApprove(item.id)}
          >
            <MaterialCommunityIcons name="check" size={16} color={colors.text.inverse} />
            <Text style={dynamicStyles.approveButtonText}>Approve</Text>
          </TouchableOpacity>
        </View>
      )}

      {item.status !== 'Pending' && (
        <View style={[dynamicStyles.statusInfo, { backgroundColor: getStatusColor(item.status) }]}>
          <MaterialCommunityIcons
            name={item.status === 'Approved' ? 'check-circle' : 'close-circle'}
            size={16}
            color={colors.text.inverse}
          />
          <Text style={dynamicStyles.statusInfoText}>
            {item.status === 'Approved' ? 'Approved' : 'Rejected'} by HR
          </Text>
        </View>
      )}
    </View>
  );

  const pendingApprovals = approvals.filter(a => a.status === 'Pending');

  return (
    <SafeAreaView style={dynamicStyles.container}>
      <ScrollView style={dynamicStyles.scrollView}>
        {/* Section Header */}
        <View style={dynamicStyles.header}>
          <Text style={dynamicStyles.headerTitle}>Approvals</Text>
          <Text style={dynamicStyles.headerSubtitle}>{pendingCount} Pending Requests</Text>
        </View>

        {/* Quick Stats */}
        <View style={dynamicStyles.statsContainer}>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="clock-outline" size={24} color={colors.icon.warning} />
            <Text style={dynamicStyles.statValue}>{pendingCount}</Text>
            <Text style={dynamicStyles.statLabel}>Pending</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="check-circle" size={24} color={colors.icon.success} />
            <Text style={dynamicStyles.statValue}>{approvedCount}</Text>
            <Text style={dynamicStyles.statLabel}>Approved</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="close-circle" size={24} color={colors.icon.danger} />
            <Text style={dynamicStyles.statValue}>{rejectedCount}</Text>
            <Text style={dynamicStyles.statLabel}>Rejected</Text>
          </View>
        </View>

        {/* Pending Approvals */}
        {pendingApprovals.length > 0 ? (
          <View style={dynamicStyles.section}>
            <Text style={dynamicStyles.sectionTitle}>Pending Approvals</Text>
            <FlatList
              data={pendingApprovals}
              renderItem={renderApprovalCard}
              keyExtractor={(item) => item.id.toString()}
              scrollEnabled={false}
            />
          </View>
        ) : (
          <View style={dynamicStyles.emptySection}>
            <MaterialCommunityIcons name="check-circle" size={48} color={colors.icon.success} />
            <Text style={dynamicStyles.emptyTitle}>All Caught Up!</Text>
            <Text style={dynamicStyles.emptyText}>No pending approvals at the moment</Text>
          </View>
        )}

        {/* All Approvals */}
        <View style={dynamicStyles.section}>
          <Text style={dynamicStyles.sectionTitle}>All Requests</Text>
          <FlatList
            data={approvals}
            renderItem={renderApprovalCard}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
          />
        </View>

        <View style={{ height: 20 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({});
