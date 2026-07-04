import React, { useState, useEffect } from 'react';
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
import { useProject } from '../context/ProjectContext';
import { useAuth } from '../context/AuthContext';
import { ProjectSelector } from '../components/ProjectSelector';
import { Modal, TextInput } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import api from '../services/api';

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
    summarySection: {
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.md,
      flexDirection: 'row',
      gap: GlassTokens.spacing.md,
    },
    summaryCard: {
      flex: 1,
      ...GlobalStyles.card,
    },
    summaryLabel: {
      ...GlobalStyles.caption,
      marginBottom: GlassTokens.spacing.xs,
    },
    summaryValue: {
      ...GlobalStyles.body,
      fontWeight: '700',
      color: colors.primary,
    },
    statsContainer: {
      flexDirection: 'row',
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.sm,
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
    expenseCard: {
      ...GlobalStyles.card,
      marginBottom: GlassTokens.spacing.md,
    },
    expenseHeader: {
      flexDirection: 'row',
      alignItems: 'flex-start',
      marginBottom: GlassTokens.spacing.md,
    },
    categoryIcon: {
      width: 44,
      height: 44,
      borderRadius: GlassTokens.radius.md,
      justifyContent: 'center',
      alignItems: 'center',
      marginRight: GlassTokens.spacing.md,
    },
    categoryEmoji: {
      fontSize: 22,
    },
    expenseInfo: {
      flex: 1,
    },
    expenseDescription: {
      ...GlobalStyles.body,
      fontWeight: '700',
      color: colors.text.primary,
      marginBottom: GlassTokens.spacing.xs,
    },
    expenseCategory: {
      ...GlobalStyles.caption,
    },
    amountSection: {
      alignItems: 'flex-end',
      gap: GlassTokens.spacing.sm,
    },
    expenseAmount: {
      ...GlobalStyles.body,
      fontWeight: '700',
      color: colors.primary,
    },
    statusBadge: {
      paddingHorizontal: GlassTokens.spacing.sm,
      paddingVertical: GlassTokens.spacing.xs,
      borderRadius: GlassTokens.radius.sm,
    },
    statusText: {
      ...GlobalStyles.badgeText,
      color: colors.text.inverse,
      fontSize: 10,
    },
    expenseFooter: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: GlassTokens.spacing.md,
      borderTopWidth: 1,
      borderTopColor: colors.border.glass,
    },
    footerInfo: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.xs,
    },
    dateText: {
      ...GlobalStyles.caption,
    },
    receiptBadge: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.xs,
      paddingHorizontal: GlassTokens.spacing.sm,
      paddingVertical: GlassTokens.spacing.xs,
      backgroundColor: colors.primaryLight,
      borderRadius: GlassTokens.radius.sm,
    },
    receiptText: {
      ...GlobalStyles.caption,
      color: colors.primary,
      fontWeight: '600',
      fontSize: 10,
    },
    actionsSection: {
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.md,
    },
    actionButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      ...GlobalStyles.buttonPrimary,
      gap: GlassTokens.spacing.md,
    },
    actionButtonText: {
      ...GlobalStyles.buttonText,
    },
    modalContainer: {
      flex: 1,
      backgroundColor: colors.background.secondary,
    },
    modalHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: GlassTokens.spacing.lg,
      paddingVertical: GlassTokens.spacing.lg,
      borderBottomWidth: 1,
      borderBottomColor: colors.border.light,
    },
    modalTitle: {
      ...GlobalStyles.title,
      color: colors.primary,
    },
    modalContent: {
      flex: 1,
      paddingHorizontal: GlassTokens.spacing.lg,
      paddingVertical: GlassTokens.spacing.lg,
    },
    formGroup: {
      marginBottom: GlassTokens.spacing.xl,
    },
    label: {
      ...GlobalStyles.label,
      color: colors.primary,
    },
    input: {
      ...GlobalStyles.inputGlass,
    },
    dateInput: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.md,
      ...GlobalStyles.inputGlass,
    },
    categoryButtons: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: GlassTokens.spacing.sm,
    },
    categoryButton: {
      flex: 0.48,
      paddingVertical: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.md,
      borderRadius: GlassTokens.radius.md,
      borderWidth: 1,
      borderColor: colors.border.glass,
      alignItems: 'center',
      backgroundColor: colors.background.tertiary,
    },
    categoryButtonActive: {
      borderColor: 'transparent',
    },
    categoryButtonText: {
      ...GlobalStyles.body,
      fontWeight: '700',
      color: colors.text.primary,
      fontSize: 12,
    },
    receiptButton: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.lg,
      borderWidth: 2,
      borderColor: colors.primary,
      borderStyle: 'dashed',
      borderRadius: GlassTokens.radius.md,
      backgroundColor: colors.primaryLight,
    },
    receiptButtonText: {
      ...GlobalStyles.body,
      fontWeight: '700',
      color: colors.primary,
    },
    receiptPreview: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: GlassTokens.spacing.md,
      paddingVertical: GlassTokens.spacing.md,
      backgroundColor: colors.primaryLight,
      borderRadius: GlassTokens.radius.md,
      marginTop: GlassTokens.spacing.md,
      borderWidth: 1,
      borderColor: colors.primary,
    },
    receiptInfo: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: GlassTokens.spacing.md,
      flex: 1,
    },
    receiptFileName: {
      ...GlobalStyles.caption,
      color: colors.primary,
      fontWeight: '600',
      flex: 1,
    },
    modalActions: {
      flexDirection: 'row',
      gap: GlassTokens.spacing.md,
      paddingHorizontal: GlassTokens.spacing.lg,
      paddingVertical: GlassTokens.spacing.lg,
      borderTopWidth: 1,
      borderTopColor: colors.border.light,
    },
    modalButton: {
      flex: 1,
      paddingVertical: GlassTokens.spacing.md,
      borderRadius: GlassTokens.radius.md,
      alignItems: 'center',
    },
    cancelButton: {
      backgroundColor: colors.background.tertiary,
    },
    submitButton: {
      ...GlobalStyles.buttonPrimary,
    },
    cancelButtonText: {
      ...GlobalStyles.buttonText,
      color: colors.text.primary,
      fontSize: 14,
    },
    submitButtonText: {
      ...GlobalStyles.buttonText,
    },
  });
};

export const ExpensesScreen = () => {
  const { colors, isDarkMode } = useTheme();
  const dynamicStyles = getDynamicStyles(colors);
  const { selectedProject } = useProject();
  const { state: authState } = useAuth();
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    description: '',
    amount: '',
    receipt: false,
    receiptUri: null,
    receiptName: '',
    expenseDate: new Date().toISOString().split('T')[0], // Today's date
  });
  const [expenses] = useState([
    {
      id: 1,
      category: 'Materials',
      description: 'Cement & Sand Purchase',
      amount: 15000,
      date: '2026-03-20',
      status: 'Approved',
      receipt: true,
    },
    {
      id: 2,
      category: 'Labor',
      description: 'Daily Wages',
      amount: 8500,
      date: '2026-03-19',
      status: 'Pending',
      receipt: true,
    },
    {
      id: 3,
      category: 'Transport',
      description: 'Material Transportation',
      amount: 3500,
      date: '2026-03-18',
      status: 'Approved',
      receipt: false,
    },
    {
      id: 4,
      category: 'Tools',
      description: 'Power Tools Rental',
      amount: 5000,
      date: '2026-03-17',
      status: 'Rejected',
      receipt: true,
    },
    {
      id: 5,
      category: 'Safety',
      description: 'Safety Equipment',
      amount: 2500,
      date: '2026-03-16',
      status: 'Approved',
      receipt: true,
    },
  ]);

  const getCategoryColor = (category) => {
    const categoryColors = {
      Materials: colors.primary,
      Labor: colors.icon.success,
      Transport: colors.icon.warning,
      Tools: colors.icon.danger,
      Safety: colors.secondary,
    };
    return categoryColors[category] || colors.text.secondary;
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

  const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);
  const approvedExpenses = expenses.filter(e => e.status === 'Approved').reduce((sum, exp) => sum + exp.amount, 0);
  const pendingExpenses = expenses.filter(e => e.status === 'Pending').reduce((sum, exp) => sum + exp.amount, 0);

  const handleAddExpense = async () => {
    if (!formData.category || !formData.description || !formData.amount) {
      Alert.alert('Missing Fields', 'Please fill in all required fields');
      return;
    }

    if (!selectedProject?.id) {
      Alert.alert('Missing Project', 'Please select a project first');
      return;
    }

    try {
      // Prepare expense data
      const expenseData = {
        staff_id: authState.user?.id,
        project_id: selectedProject.id,
        category: formData.category,
        description: formData.description,
        amount: parseFloat(formData.amount),
        expense_date: formData.expenseDate,
        status: 'Pending',
        receipt_url: formData.receiptUri || null, // Store URI for now (can be uploaded separately)
      };

      // Submit to backend (use mobile-specific endpoint)
      const response = await api.post('/api/staff/expenses/mobile', expenseData);

      if (response.data?.success) {
        Alert.alert('Success', 'Expense submitted for approval!');
        setShowAddModal(false);
        setFormData({
          category: '',
          description: '',
          amount: '',
          receipt: false,
          receiptUri: null,
          receiptName: '',
          expenseDate: new Date().toISOString().split('T')[0],
        });
      } else {
        Alert.alert('Error', response.data?.message || 'Failed to submit expense');
      }
    } catch (error) {
      console.error('Error submitting expense:', error);
      Alert.alert('Error', error.message || 'Failed to submit expense');
    }
  };

  const handleCloseModal = () => {
    setShowAddModal(false);
    setFormData({
      category: '',
      description: '',
      amount: '',
      receipt: false,
      receiptUri: null,
      receiptName: '',
      expenseDate: new Date().toISOString().split('T')[0],
    });
  };

  const handlePickReceipt = async () => {
    try {
      // Request permission
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'We need permission to access your photos');
        return;
      }

      // Pick image
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: [ImagePicker.MediaType.IMAGE],
        allowsEditing: false,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets?.length > 0) {
        const asset = result.assets[0];
        const fileName = asset.uri.split('/').pop();
        setFormData({
          ...formData,
          receipt: true,
          receiptUri: asset.uri,
          receiptName: fileName,
        });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick receipt image');
      console.error('Receipt picker error:', error);
    }
  };

  const renderExpenseCard = ({ item }) => (
    <TouchableOpacity
      style={dynamicStyles.expenseCard}
      onPress={() => Alert.alert(item.description, `Category: ${item.category}\nAmount: ₹${item.amount}\nDate: ${new Date(item.date).toLocaleDateString()}\nStatus: ${item.status}\nReceipt: ${item.receipt ? 'Attached' : 'Not attached'}`, [
        { text: 'View Details', onPress: () => Alert.alert('Expense Details', 'Full details and approval history') },
        { text: 'Edit', onPress: () => Alert.alert('Edit', item.status === 'Approved' ? 'Cannot edit approved expense' : 'Editing expense...') },
        { text: 'Close', onPress: () => {} }
      ])}
    >
      <View style={dynamicStyles.expenseHeader}>
        <View style={[dynamicStyles.categoryIcon, { backgroundColor: getCategoryColor(item.category) }]}>
          <Text style={dynamicStyles.categoryEmoji}>
            {item.category === 'Materials' && '📦'}
            {item.category === 'Labor' && '👷'}
            {item.category === 'Transport' && '🚚'}
            {item.category === 'Tools' && '🔧'}
            {item.category === 'Safety' && '⚠️'}
          </Text>
        </View>
        <View style={dynamicStyles.expenseInfo}>
          <Text style={dynamicStyles.expenseDescription}>{item.description}</Text>
          <Text style={dynamicStyles.expenseCategory}>{item.category}</Text>
        </View>
        <View style={dynamicStyles.amountSection}>
          <Text style={dynamicStyles.expenseAmount}>₹{item.amount.toLocaleString()}</Text>
          <View style={[dynamicStyles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
            <Text style={dynamicStyles.statusText}>{item.status}</Text>
          </View>
        </View>
      </View>

      <View style={dynamicStyles.expenseFooter}>
        <View style={dynamicStyles.footerInfo}>
          <MaterialCommunityIcons name="calendar" size={14} color={colors.text.secondary} />
          <Text style={dynamicStyles.dateText}>{new Date(item.date).toLocaleDateString()}</Text>
        </View>
        {item.receipt && (
          <View style={dynamicStyles.receiptBadge}>
            <MaterialCommunityIcons name="file-check" size={14} color={colors.primary} />
            <Text style={dynamicStyles.receiptText}>Receipt</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={dynamicStyles.container}>
      <ScrollView style={dynamicStyles.scrollView}>
        {/* Project Selector for Engineers */}
        <ProjectSelector />

        {/* Section Header */}
        <View style={dynamicStyles.header}>
          <Text style={dynamicStyles.headerTitle}>My Expenses</Text>
          <Text style={dynamicStyles.headerSubtitle}>
            {selectedProject && `${selectedProject.name} • `}
            {expenses.length} Expenses This Month
          </Text>
        </View>

        {/* Summary Stats */}
        <View style={dynamicStyles.summarySection}>
          <View style={dynamicStyles.summaryCard}>
            <Text style={dynamicStyles.summaryLabel}>Total Expenses</Text>
            <Text style={dynamicStyles.summaryValue}>₹{totalExpenses.toLocaleString()}</Text>
          </View>
          <View style={dynamicStyles.summaryCard}>
            <Text style={dynamicStyles.summaryLabel}>Approved</Text>
            <Text style={[dynamicStyles.summaryValue, { color: colors.icon.success }]}>₹{approvedExpenses.toLocaleString()}</Text>
          </View>
          <View style={dynamicStyles.summaryCard}>
            <Text style={dynamicStyles.summaryLabel}>Pending</Text>
            <Text style={[dynamicStyles.summaryValue, { color: colors.icon.warning }]}>₹{pendingExpenses.toLocaleString()}</Text>
          </View>
        </View>

        {/* Quick Stats */}
        <View style={dynamicStyles.statsContainer}>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="receipt" size={24} color={colors.primary} />
            <Text style={dynamicStyles.statValue}>{expenses.length}</Text>
            <Text style={dynamicStyles.statLabel}>Total</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="check-circle" size={24} color={colors.icon.success} />
            <Text style={dynamicStyles.statValue}>{expenses.filter(e => e.status === 'Approved').length}</Text>
            <Text style={dynamicStyles.statLabel}>Approved</Text>
          </View>
          <View style={dynamicStyles.statCard}>
            <MaterialCommunityIcons name="clock-outline" size={24} color={colors.icon.warning} />
            <Text style={dynamicStyles.statValue}>{expenses.filter(e => e.status === 'Pending').length}</Text>
            <Text style={dynamicStyles.statLabel}>Pending</Text>
          </View>
        </View>

        {/* Expenses List */}
        <View style={dynamicStyles.section}>
          <Text style={dynamicStyles.sectionTitle}>Recent Expenses</Text>
          <FlatList
            data={expenses}
            renderItem={renderExpenseCard}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
          />
        </View>

        {/* Quick Actions */}
        <View style={dynamicStyles.actionsSection}>
          <TouchableOpacity
            style={dynamicStyles.actionButton}
            onPress={() => setShowAddModal(true)}
          >
            <MaterialCommunityIcons name="plus-circle" size={24} color={colors.text.inverse} />
            <Text style={dynamicStyles.actionButtonText}>Add New Expense</Text>
          </TouchableOpacity>
        </View>

        <View style={{ height: 20 }} />
      </ScrollView>

      {/* Add Expense Modal */}
      <Modal
        visible={showAddModal}
        animationType="slide"
        transparent={true}
        onRequestClose={handleCloseModal}
      >
        <SafeAreaView style={dynamicStyles.modalContainer}>
          <View style={dynamicStyles.modalHeader}>
            <TouchableOpacity onPress={handleCloseModal}>
              <MaterialCommunityIcons name="close" size={28} color={colors.primary} />
            </TouchableOpacity>
            <Text style={dynamicStyles.modalTitle}>Add New Expense</Text>
            <View style={{ width: 28 }} />
          </View>

          <ScrollView style={dynamicStyles.modalContent}>
            {/* Category Selector */}
            <View style={dynamicStyles.formGroup}>
              <Text style={dynamicStyles.label}>Category</Text>
              <View style={dynamicStyles.categoryButtons}>
                {['Materials', 'Labor', 'Transport', 'Tools', 'Safety'].map((cat) => (
                  <TouchableOpacity
                    key={cat}
                    style={[
                      dynamicStyles.categoryButton,
                      formData.category === cat && dynamicStyles.categoryButtonActive,
                      { backgroundColor: formData.category === cat ? getCategoryColor(cat) : colors.background.secondary }
                    ]}
                    onPress={() => setFormData({ ...formData, category: cat })}
                  >
                    <Text
                      style={[
                        dynamicStyles.categoryButtonText,
                        formData.category === cat && { color: colors.text.inverse }
                      ]}
                    >
                      {cat}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Description */}
            <View style={dynamicStyles.formGroup}>
              <Text style={dynamicStyles.label}>Description</Text>
              <TextInput
                style={dynamicStyles.input}
                placeholder="Enter expense description"
                value={formData.description}
                onChangeText={(text) => setFormData({ ...formData, description: text })}
              />
            </View>

            {/* Amount */}
            <View style={dynamicStyles.formGroup}>
              <Text style={dynamicStyles.label}>Amount (₹)</Text>
              <TextInput
                style={dynamicStyles.input}
                placeholder="Enter amount"
                value={formData.amount}
                onChangeText={(text) => setFormData({ ...formData, amount: text })}
                keyboardType="decimal-pad"
              />
            </View>

            {/* Expense Date */}
            <View style={dynamicStyles.formGroup}>
              <Text style={dynamicStyles.label}>Date</Text>
              <View style={dynamicStyles.dateInput}>
                <MaterialCommunityIcons name="calendar" size={18} color={colors.primary} />
                <Text style={dynamicStyles.dateText}>{formData.expenseDate}</Text>
              </View>
            </View>

            {/* Receipt Upload */}
            <View style={dynamicStyles.formGroup}>
              <Text style={dynamicStyles.label}>Receipt (Optional)</Text>
              <TouchableOpacity
                style={dynamicStyles.receiptButton}
                onPress={handlePickReceipt}
              >
                <MaterialCommunityIcons name="image-plus" size={24} color={colors.primary} />
                <Text style={dynamicStyles.receiptButtonText}>
                  {formData.receiptUri ? 'Change Receipt' : 'Attach Receipt'}
                </Text>
              </TouchableOpacity>

              {formData.receiptUri && (
                <View style={dynamicStyles.receiptPreview}>
                  <View style={dynamicStyles.receiptInfo}>
                    <MaterialCommunityIcons name="file-image" size={20} color={colors.primary} />
                    <Text style={dynamicStyles.receiptFileName}>{formData.receiptName}</Text>
                  </View>
                  <TouchableOpacity
                    onPress={() => setFormData({
                      ...formData,
                      receipt: false,
                      receiptUri: null,
                      receiptName: ''
                    })}
                  >
                    <MaterialCommunityIcons name="close" size={20} color={colors.icon.danger} />
                  </TouchableOpacity>
                </View>
              )}
            </View>
          </ScrollView>

          {/* Action Buttons */}
          <View style={dynamicStyles.modalActions}>
            <TouchableOpacity
              style={[dynamicStyles.modalButton, dynamicStyles.cancelButton]}
              onPress={handleCloseModal}
            >
              <Text style={dynamicStyles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[dynamicStyles.modalButton, dynamicStyles.submitButton]}
              onPress={handleAddExpense}
            >
              <Text style={dynamicStyles.submitButtonText}>Submit</Text>
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({});
