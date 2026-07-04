import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Image,
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
    filterSection: {
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.md,
    },
    filterScroll: {
      flexDirection: 'row',
    },
    filterChip: {
      paddingHorizontal: GlassTokens.spacing.lg,
      paddingVertical: GlassTokens.spacing.sm,
      borderRadius: GlassTokens.radius.full,
      backgroundColor: colors.background.tertiary,
      marginRight: GlassTokens.spacing.md,
      borderWidth: 1,
      borderColor: colors.border.glass,
    },
    filterChipActive: {
      backgroundColor: colors.primaryLight,
      borderColor: colors.primary,
    },
    filterChipText: {
      ...GlobalStyles.caption,
      color: colors.text.secondary,
    },
    filterChipTextActive: {
      ...GlobalStyles.caption,
      color: colors.primary,
      fontWeight: '700',
    },
    section: {
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.sm,
    },
    memberCard: {
      ...GlobalStyles.card,
      marginBottom: GlassTokens.spacing.md,
    },
    memberHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: GlassTokens.spacing.md,
    },
    memberInfo: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'flex-start',
    },
    avatarSection: {
      width: 50,
      height: 50,
      borderRadius: 25,
      backgroundColor: colors.primaryLight,
      justifyContent: 'center',
      alignItems: 'center',
      marginRight: GlassTokens.spacing.lg,
    },
    avatarIcon: {
      fontSize: 28,
    },
    memberDetails: {
      flex: 1,
    },
    memberName: {
      ...GlobalStyles.subtitle,
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.xs,
      fontWeight: '700',
    },
    memberRole: {
      ...GlobalStyles.caption,
      color: colors.primary,
      marginBottom: GlassTokens.spacing.xs,
      fontWeight: '600',
    },
    memberDept: {
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
    memberStats: {
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
      flex: 1,
    },
    statDivider: {
      width: 1,
      height: 20,
      backgroundColor: colors.border.light,
      marginHorizontal: GlassTokens.spacing.md,
    },
    memberActions: {
      flexDirection: 'row',
      justifyContent: 'flex-end',
      gap: GlassTokens.spacing.sm,
      paddingTop: GlassTokens.spacing.md,
      borderTopWidth: 1,
      borderTopColor: colors.border.light,
    },
    actionButton: {
      width: 36,
      height: 36,
      borderRadius: GlassTokens.radius.sm,
      backgroundColor: colors.background.tertiary,
      justifyContent: 'center',
      alignItems: 'center',
    },
  });
};

export const TeamScreen = () => {
  const { colors, isDarkMode } = useTheme();
  const dynamicStyles = getDynamicStyles(colors);
  const [selectedDept, setSelectedDept] = useState('All');
  const [teamMembers] = useState([
    {
      id: 1,
      name: 'Rajesh Kumar',
      role: 'Site Engineer',
      department: 'Construction',
      status: 'Active',
      phone: '+91-9876543210',
      projects: 3,
    },
    {
      id: 2,
      name: 'Priya Singh',
      role: 'Project Manager',
      department: 'Management',
      status: 'Active',
      phone: '+91-9876543211',
      projects: 2,
    },
    {
      id: 3,
      name: 'Amit Patel',
      role: 'Supervisor',
      department: 'Construction',
      status: 'On Leave',
      phone: '+91-9876543212',
      projects: 1,
    },
    {
      id: 4,
      name: 'Neha Sharma',
      role: 'HR Manager',
      department: 'Administration',
      status: 'Active',
      phone: '+91-9876543213',
      projects: 5,
    },
    {
      id: 5,
      name: 'Vikram Reddy',
      role: 'Safety Officer',
      department: 'Safety',
      status: 'Active',
      phone: '+91-9876543214',
      projects: 4,
    },
  ]);

  const getStatusColor = (status) => {
    return status === 'Active' ? colors.icon.success : colors.icon.warning;
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'Project Manager':
        return '👨‍💼';
      case 'Site Engineer':
        return '👷';
      case 'Supervisor':
        return '🏗️';
      case 'HR Manager':
        return '👩‍💼';
      case 'Safety Officer':
        return '⚠️';
      default:
        return '👤';
    }
  };

  const renderTeamMember = ({ item }) => (
    <TouchableOpacity
      style={styles.memberCard}
      onPress={() => Alert.alert(item.name, `Role: ${item.role}\nDept: ${item.department}\nStatus: ${item.status}\nPhone: ${item.phone}\nProjects: ${item.projects}`, [
        { text: 'View Profile', onPress: () => Alert.alert('Profile', `Full profile information for ${item.name}`) },
        { text: 'Assign Project', onPress: () => Alert.alert('Assign', 'Select a project to assign...') },
        { text: 'Close', onPress: () => {} }
      ])}
    >
      <View style={styles.memberHeader}>
        <View style={styles.memberInfo}>
          <View style={styles.avatarSection}>
            <Text style={styles.avatarIcon}>{getRoleIcon(item.role)}</Text>
          </View>
          <View style={styles.memberDetails}>
            <Text style={styles.memberName}>{item.name}</Text>
            <Text style={styles.memberRole}>{item.role}</Text>
            <Text style={styles.memberDept}>{item.department}</Text>
          </View>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
      </View>

      <View style={dynamicStyles.memberStats}>
        <View style={dynamicStyles.statItem}>
          <MaterialCommunityIcons name="phone" size={16} color={colors.primary} />
          <Text style={dynamicStyles.statText}>{item.phone}</Text>
        </View>
        <View style={dynamicStyles.statDivider} />
        <View style={dynamicStyles.statItem}>
          <MaterialCommunityIcons name="briefcase" size={16} color={colors.primary} />
          <Text style={dynamicStyles.statText}>{item.projects} Projects</Text>
        </View>
      </View>

      <View style={dynamicStyles.memberActions}>
        <TouchableOpacity
          style={dynamicStyles.actionButton}
          onPress={() => Alert.alert('Send Message', `Send a message to ${item.name}?`, [
            { text: 'Send', onPress: () => Alert.alert('Success', 'Message sent!') },
            { text: 'Cancel', onPress: () => {} }
          ])}
        >
          <MaterialCommunityIcons name="message" size={20} color={colors.primary} />
        </TouchableOpacity>
        <TouchableOpacity
          style={dynamicStyles.actionButton}
          onPress={() => Alert.alert('Call', `Calling ${item.name}...\n${item.phone}`, [
            { text: 'Call Now', onPress: () => Alert.alert('Calling', 'Call initiated...') },
            { text: 'Close', onPress: () => {} }
          ])}
        >
          <MaterialCommunityIcons name="phone-outline" size={20} color={colors.primary} />
        </TouchableOpacity>
        <TouchableOpacity
          style={dynamicStyles.actionButton}
          onPress={() => Alert.alert('Send Email', `Email to ${item.name}?`, [
            { text: 'Compose', onPress: () => Alert.alert('Email', 'Opening email composer...') },
            { text: 'Close', onPress: () => {} }
          ])}
        >
          <MaterialCommunityIcons name="email-outline" size={20} color={colors.primary} />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={dynamicStyles.container}>
      <ScrollView style={dynamicStyles.scrollView}>
        {/* Section Header */}
        <View style={dynamicStyles.header}>
          <Text style={dynamicStyles.headerTitle}>Team Members</Text>
          <Text style={dynamicStyles.headerSubtitle}>{teamMembers.length} Total Members</Text>
        </View>

        {/* Quick Stats */}
        <View style={dynamicStyles.statsContainer}>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="account-multiple" size={24} color={colors.primary} />
            <Text style={dynamicStyles.statValue}>{teamMembers.length}</Text>
            <Text style={dynamicStyles.statLabel}>Total</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="check-circle" size={24} color={colors.icon.success} />
            <Text style={dynamicStyles.statValue}>{teamMembers.filter(m => m.status === 'Active').length}</Text>
            <Text style={dynamicStyles.statLabel}>Active</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="briefcase" size={24} color={colors.icon.warning} />
            <Text style={dynamicStyles.statValue}>5</Text>
            <Text style={dynamicStyles.statLabel}>Departments</Text>
          </View>
        </View>

        {/* Department Filter */}
        <View style={dynamicStyles.filterSection}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={dynamicStyles.filterScroll}>
            <TouchableOpacity style={[dynamicStyles.filterChip, dynamicStyles.filterChipActive]}>
              <Text style={dynamicStyles.filterChipTextActive}>All</Text>
            </TouchableOpacity>
            <TouchableOpacity style={dynamicStyles.filterChip}>
              <Text style={dynamicStyles.filterChipText}>Construction</Text>
            </TouchableOpacity>
            <TouchableOpacity style={dynamicStyles.filterChip}>
              <Text style={dynamicStyles.filterChipText}>Management</Text>
            </TouchableOpacity>
            <TouchableOpacity style={dynamicStyles.filterChip}>
              <Text style={dynamicStyles.filterChipText}>Safety</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>

        {/* Team Members List */}
        <View style={dynamicStyles.section}>
          <FlatList
            data={teamMembers}
            renderItem={renderTeamMember}
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
