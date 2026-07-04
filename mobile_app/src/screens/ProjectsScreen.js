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

export const ProjectsScreen = () => {
  const { colors, isDarkMode } = useTheme();
  const dynamicStyles = getDynamicStyles(colors);
  const [projects] = useState([
    {
      id: 1,
      name: 'Foundation Work - Phase 1',
      status: 'Active',
      progress: 75,
      team: 10,
      dueDate: 'Mar 30, 2026',
      budget: '₹2,50,000',
    },
    {
      id: 2,
      name: 'Structural Design - Phase 2',
      status: 'In Progress',
      progress: 45,
      team: 7,
      dueDate: 'Apr 15, 2026',
      budget: '₹3,50,000',
    },
    {
      id: 3,
      name: 'Interior Finishing - Phase 3',
      status: 'Planned',
      progress: 0,
      team: 5,
      dueDate: 'May 20, 2026',
      budget: '₹1,80,000',
    },
    {
      id: 4,
      name: 'Electrical Installation',
      status: 'Active',
      progress: 60,
      team: 8,
      dueDate: 'Apr 10, 2026',
      budget: '₹1,50,000',
    },
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return colors.primary;
      case 'In Progress':
        return colors.icon.warning;
      case 'Planned':
        return colors.text.secondary;
      case 'Completed':
        return colors.icon.success;
      default:
        return colors.text.tertiary;
    }
  };

  const renderProjectCard = ({ item }) => (
    <TouchableOpacity
      style={dynamicStyles.projectCard}
      onPress={() => Alert.alert(item.name, `Status: ${item.status}\nProgress: ${item.progress}%\nTeam: ${item.team} members\nBudget: ${item.budget}\n\nTap "View Details" to see more`, [
        { text: 'View Details', onPress: () => Alert.alert('Project Details', `Full details for ${item.name}\n\nAll project information, timeline, and team assignments`) },
        { text: 'Edit', onPress: () => Alert.alert('Edit Project', 'Opening project editor...') },
        { text: 'Close', onPress: () => {} }
      ])}
    >
      <View style={dynamicStyles.projectHeader}>
        <View style={dynamicStyles.projectInfo}>
          <Text style={dynamicStyles.projectName}>{item.name}</Text>
          <Text style={dynamicStyles.projectMeta}>{item.team} Team Members • {item.dueDate}</Text>
        </View>
        <View style={[dynamicStyles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={dynamicStyles.statusText}>{item.status}</Text>
        </View>
      </View>

      <View style={dynamicStyles.progressSection}>
        <View style={dynamicStyles.progressBar}>
          <View style={[dynamicStyles.progress, { width: `${item.progress}%`, backgroundColor: getStatusColor(item.status) }]} />
        </View>
        <Text style={dynamicStyles.progressText}>{item.progress}% Complete</Text>
      </View>

      <View style={dynamicStyles.projectFooter}>
        <View style={dynamicStyles.budgetBox}>
          <Text style={dynamicStyles.budgetLabel}>Budget</Text>
          <Text style={dynamicStyles.budgetValue}>{item.budget}</Text>
        </View>
        <TouchableOpacity style={dynamicStyles.detailsButton}>
          <MaterialCommunityIcons name="chevron-right" size={24} color={colors.primary} />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={dynamicStyles.container}>
      <ScrollView style={dynamicStyles.scrollView}>
        {/* Section Header */}
        <View style={dynamicStyles.header}>
          <Text style={dynamicStyles.headerTitle}>All Projects</Text>
          <Text style={dynamicStyles.headerSubtitle}>{projects.length} Active Projects</Text>
        </View>

        {/* Quick Stats */}
        <View style={dynamicStyles.statsContainer}>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="folder-multiple" size={24} color={colors.primary} />
            <Text style={dynamicStyles.statValue}>{projects.length}</Text>
            <Text style={dynamicStyles.statLabel}>Total</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="lightning-bolt" size={24} color={colors.icon.warning} />
            <Text style={dynamicStyles.statValue}>{projects.filter(p => p.status === 'Active').length}</Text>
            <Text style={dynamicStyles.statLabel}>Active</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="check-circle" size={24} color={colors.icon.success} />
            <Text style={dynamicStyles.statValue}>₹75L</Text>
            <Text style={dynamicStyles.statLabel}>Budget Used</Text>
          </View>
        </View>

        {/* Projects List */}
        <View style={dynamicStyles.section}>
          <FlatList
            data={projects}
            renderItem={renderProjectCard}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
          />
        </View>

        <View style={{ height: 20 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

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
    projectCard: {
      ...GlobalStyles.card,
      marginBottom: GlassTokens.spacing.md,
    },
    projectHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: GlassTokens.spacing.md,
    },
    projectInfo: {
      flex: 1,
    },
    projectName: {
      ...GlobalStyles.subtitle,
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.xs,
    },
    projectMeta: {
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
    progressSection: {
      marginBottom: GlassTokens.spacing.md,
    },
    progressBar: {
      height: 6,
      backgroundColor: colors.border.light,
      borderRadius: GlassTokens.radius.sm,
      marginBottom: GlassTokens.spacing.sm,
      overflow: 'hidden',
    },
    progress: {
      height: '100%',
      borderRadius: GlassTokens.radius.sm,
    },
    progressText: {
      ...GlobalStyles.caption,
    },
    projectFooter: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: GlassTokens.spacing.md,
      borderTopWidth: 1,
      borderTopColor: colors.border.light,
    },
    budgetBox: {
      flex: 1,
    },
    budgetLabel: {
      ...GlobalStyles.caption,
      marginBottom: GlassTokens.spacing.xs,
    },
    budgetValue: {
      ...GlobalStyles.title,
      color: colors.primary,
    },
    detailsButton: {
      width: 40,
      height: 40,
      justifyContent: 'center',
      alignItems: 'center',
    },
  });
};

const styles = StyleSheet.create({
  // Placeholder - will be replaced with getDynamicStyles
  container: { flex: 1 },
});
