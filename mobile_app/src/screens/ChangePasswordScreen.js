import React, { useState } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Keyboard,
  TouchableWithoutFeedback,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Colors, Gradients } from '../theme';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export const ChangePasswordScreen = () => {
  const { colors } = useTheme();
  const { changePassword, signOut } = useAuth();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const passwordRules = {
    length: newPassword.length >= 8,
    uppercase: /[A-Z]/.test(newPassword),
    digit: /[0-9]/.test(newPassword),
  };

  const allValid = passwordRules.length && passwordRules.uppercase && passwordRules.digit;

  const handleChangePassword = async () => {
    if (!newPassword) {
      Alert.alert('Error', 'Please enter a new password');
      return;
    }
    if (!allValid) {
      Alert.alert('Error', 'Password does not meet requirements');
      return;
    }
    if (newPassword !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    setIsLoading(true);
    try {
      const result = await changePassword('Erp@123', newPassword);
      if (result.success) {
        Alert.alert('Success', 'Password changed successfully!', [
          { text: 'OK' },
        ]);
      } else {
        Alert.alert('Error', result.error || 'Failed to change password');
      }
    } catch (error) {
      Alert.alert('Error', 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={styles.root}>
        <LinearGradient
          colors={Gradients.primary.colors}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.gradient}
        >
          <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.flex}
          >
            <View style={styles.inner}>
              <View style={styles.topSection}>
                <View style={styles.iconContainer}>
                  <MaterialCommunityIcons name="shield-lock-outline" size={40} color="#ffffff" />
                </View>
                <Text style={styles.title}>Change Your Password</Text>
                <Text style={styles.subtitle}>
                  This is your first login. Please set a new password to continue.
                </Text>
              </View>

              <View style={styles.card}>
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>New Password</Text>
                  <View style={styles.inputWrapper}>
                    <MaterialCommunityIcons name="lock-outline" size={18} color={Colors.text.tertiary} style={styles.inputIcon} />
                    <TextInput
                      style={styles.input}
                      placeholder="Enter new password"
                      placeholderTextColor={Colors.text.tertiary}
                      value={newPassword}
                      onChangeText={setNewPassword}
                      editable={!isLoading}
                      secureTextEntry={!showNew}
                      autoCapitalize="none"
                    />
                    <TouchableOpacity onPress={() => setShowNew(!showNew)} style={styles.eyeBtn}>
                      <MaterialCommunityIcons
                        name={showNew ? 'eye-off-outline' : 'eye-outline'}
                        size={18}
                        color={Colors.text.tertiary}
                      />
                    </TouchableOpacity>
                  </View>
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Confirm Password</Text>
                  <View style={styles.inputWrapper}>
                    <MaterialCommunityIcons name="lock-check-outline" size={18} color={Colors.text.tertiary} style={styles.inputIcon} />
                    <TextInput
                      style={styles.input}
                      placeholder="Confirm new password"
                      placeholderTextColor={Colors.text.tertiary}
                      value={confirmPassword}
                      onChangeText={setConfirmPassword}
                      editable={!isLoading}
                      secureTextEntry={!showConfirm}
                      autoCapitalize="none"
                    />
                    <TouchableOpacity onPress={() => setShowConfirm(!showConfirm)} style={styles.eyeBtn}>
                      <MaterialCommunityIcons
                        name={showConfirm ? 'eye-off-outline' : 'eye-outline'}
                        size={18}
                        color={Colors.text.tertiary}
                      />
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Password Rules */}
                <View style={styles.rulesBox}>
                  <Text style={styles.rulesTitle}>Password must contain:</Text>
                  <RuleRow valid={passwordRules.length} label="At least 8 characters" />
                  <RuleRow valid={passwordRules.uppercase} label="One uppercase letter" />
                  <RuleRow valid={passwordRules.digit} label="One digit" />
                </View>

                <TouchableOpacity
                  style={[styles.button, (!allValid || isLoading) && { opacity: 0.6 }]}
                  onPress={handleChangePassword}
                  disabled={!allValid || isLoading}
                  activeOpacity={0.85}
                >
                  {isLoading ? (
                    <ActivityIndicator color="#ffffff" size="small" />
                  ) : (
                    <Text style={styles.buttonText}>Update Password</Text>
                  )}
                </TouchableOpacity>

                <TouchableOpacity style={styles.logoutBtn} onPress={signOut} disabled={isLoading}>
                  <Text style={styles.logoutText}>Logout instead</Text>
                </TouchableOpacity>
              </View>
            </View>
          </KeyboardAvoidingView>
        </LinearGradient>
      </View>
    </TouchableWithoutFeedback>
  );
};

const RuleRow = ({ valid, label }) => (
  <View style={styles.ruleRow}>
    <MaterialCommunityIcons
      name={valid ? 'check-circle' : 'circle-outline'}
      size={16}
      color={valid ? '#22c55e' : Colors.text.tertiary}
    />
    <Text style={[styles.ruleText, valid && { color: '#22c55e' }]}>{label}</Text>
  </View>
);

const styles = StyleSheet.create({
  root: { flex: 1 },
  flex: { flex: 1 },
  gradient: { flex: 1 },
  inner: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 24 },
  topSection: { alignItems: 'center', marginBottom: 32 },
  iconContainer: {
    width: 72,
    height: 72,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.18)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.25)',
  },
  title: { fontSize: 24, fontWeight: '800', color: '#ffffff', letterSpacing: -0.5, marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 14, color: 'rgba(255,255,255,0.75)', fontWeight: '500', textAlign: 'center', lineHeight: 20 },
  card: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: 'rgba(255,255,255,0.95)',
    borderRadius: 20,
    padding: 28,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 24,
    elevation: 12,
  },
  inputGroup: { marginBottom: 16 },
  inputLabel: { fontSize: 12, fontWeight: '600', color: Colors.text.secondary, marginBottom: 6, letterSpacing: 0.3 },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.background.tertiary,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border.light,
    paddingHorizontal: 14,
  },
  inputIcon: { marginRight: 10 },
  input: { flex: 1, paddingVertical: 13, fontSize: 15, color: Colors.text.primary, fontWeight: '500' },
  eyeBtn: { padding: 4 },
  rulesBox: {
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    padding: 14,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  rulesTitle: { fontSize: 12, fontWeight: '600', color: Colors.text.secondary, marginBottom: 8 },
  ruleRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 4 },
  ruleText: { fontSize: 13, color: Colors.text.tertiary, fontWeight: '500' },
  button: {
    backgroundColor: Colors.primary.main,
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: Colors.glow?.indigo || '#6366f1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 6,
  },
  buttonText: { fontSize: 15, fontWeight: '700', color: '#ffffff', letterSpacing: 0.3 },
  logoutBtn: { marginTop: 16, alignItems: 'center' },
  logoutText: { fontSize: 13, color: Colors.text.tertiary, fontWeight: '600', textDecorationLine: 'underline' },
});
