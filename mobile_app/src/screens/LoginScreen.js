import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet, Alert, ActivityIndicator, KeyboardAvoidingView, Platform, Image, Keyboard, TouchableWithoutFeedback, Dimensions } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Colors, GlassTokens, Gradients } from '../theme';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { API_BASE_URL } from '../services/api';
import { getActiveFestival } from '../utils/festival';

const { width } = Dimensions.get('window');

export const LoginScreen = () => {
  const { colors } = useTheme();
  const festival = getActiveFestival();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { sign } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter Staff ID and password');
      return;
    }
    setIsLoading(true);
    try {
      const result = await sign(email.trim(), password);
      if (!result.success) Alert.alert('Login Failed', result.error);
    } catch (error) {
      Alert.alert('Error', 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={styles.root}>
        <LinearGradient colors={Gradients.primary.colors} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.gradient}>
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.flex}>
            <View style={styles.inner}>
              {/* Top branding */}
              <View style={styles.topSection}>
                <View style={styles.logoRing}>
                  <Image source={{ uri: `${API_BASE_URL}/static/logo.jpg?t=${Date.now()}` }} style={styles.logo} resizeMode="contain" />
                </View>
                <Text style={styles.appName}>BuildERP</Text>
                <Text style={styles.tagline}>Construction Management Platform</Text>
              </View>

              {/* Login Card */}
              <View style={styles.card}>
                {/* Card header accent */}
                <View style={styles.cardAccent} />

                <View style={styles.cardBody}>
                  {/* Welcome text */}
                  <View style={styles.welcomeRow}>
                    <View>
                      <Text style={styles.cardTitle}>Welcome Back</Text>
                      <Text style={styles.cardSubtitle}>Sign in to continue</Text>
                    </View>
                    <View style={styles.welcomeIcon}>
                      <MaterialCommunityIcons name="hand-wave" size={28} color={Colors.primary.main} />
                    </View>
                  </View>

                  {festival && (
                    <View style={[styles.festivalBanner, { backgroundColor: festival.colors[0] + '12', borderColor: festival.colors[0] + '30' }]}>
                      <MaterialCommunityIcons name={festival.icon} size={14} color={festival.colors[0]} />
                      <Text style={[styles.festivalText, { color: festival.colors[0] }]}>{festival.message}</Text>
                    </View>
                  )}

                  {/* Staff ID Input */}
                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Staff ID</Text>
                    <View style={styles.inputWrapper}>
                      <View style={styles.inputIconBox}>
                        <MaterialCommunityIcons name="account" size={16} color={Colors.primary.main} />
                      </View>
                      <TextInput
                        style={styles.input}
                        placeholder="STF-2026-001"
                        placeholderTextColor="#b0b8c8"
                        value={email}
                        onChangeText={setEmail}
                        editable={!isLoading}
                        autoCapitalize="characters"
                        autoCorrect={false}
                      />
                    </View>
                  </View>

                  {/* Password Input */}
                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Password</Text>
                    <View style={styles.inputWrapper}>
                      <View style={styles.inputIconBox}>
                        <MaterialCommunityIcons name="lock" size={16} color={Colors.primary.main} />
                      </View>
                      <TextInput
                        style={styles.input}
                        placeholder="Enter password"
                        placeholderTextColor="#b0b8c8"
                        value={password}
                        onChangeText={setPassword}
                        editable={!isLoading}
                        secureTextEntry={!showPassword}
                        autoCapitalize="none"
                      />
                      <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
                        <MaterialCommunityIcons
                          name={showPassword ? 'eye-off' : 'eye'}
                          size={18}
                          color="#9ca3af"
                        />
                      </TouchableOpacity>
                    </View>
                  </View>

                  {/* Login Button */}
                  <TouchableOpacity
                    style={[styles.loginBtn, isLoading && { opacity: 0.7 }]}
                    onPress={handleLogin}
                    disabled={isLoading}
                    activeOpacity={0.85}
                  >
                    <LinearGradient
                      colors={[Colors.primary.main, Colors.primary.dark || '#0047b3']}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 0 }}
                      style={styles.loginBtnGradient}
                    >
                      {isLoading ? (
                        <ActivityIndicator color="#ffffff" size="small" />
                      ) : (
                        <>
                          <Text style={styles.loginBtnText}>Sign In</Text>
                          <MaterialCommunityIcons name="arrow-right" size={18} color="#ffffff" />
                        </>
                      )}
                    </LinearGradient>
                  </TouchableOpacity>
                </View>

                {/* Card footer */}
                <View style={styles.cardFooter}>
                  <MaterialCommunityIcons name="shield-check" size={13} color="#6b7280" />
                  <Text style={styles.footerText}>Secured with enterprise-grade encryption</Text>
                </View>
              </View>
            </View>
          </KeyboardAvoidingView>
        </LinearGradient>
      </View>
    </TouchableWithoutFeedback>
  );
};

const styles = StyleSheet.create({
  root: { flex: 1 },
  flex: { flex: 1 },
  gradient: { flex: 1 },
  inner: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 24 },

  /* Top branding */
  topSection: { alignItems: 'center', marginBottom: 32 },
  logoRing: {
    width: 68,
    height: 68,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 14,
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.25)',
  },
  logo: { width: 40, height: 40 },
  appName: { fontSize: 26, fontWeight: '800', color: '#ffffff', letterSpacing: -0.5, marginBottom: 4 },
  tagline: { fontSize: 12, color: 'rgba(255,255,255,0.65)', fontWeight: '500' },

  /* Card */
  card: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: '#ffffff',
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.12,
    shadowRadius: 32,
    elevation: 14,
  },
  cardAccent: {
    height: 4,
    backgroundColor: Colors.primary.main,
  },
  cardBody: {
    padding: 24,
    paddingTop: 20,
  },

  /* Welcome row */
  welcomeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  welcomeIcon: {
    width: 44,
    height: 44,
    borderRadius: 14,
    backgroundColor: Colors.primary.main + '12',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardTitle: { fontSize: 20, fontWeight: '700', color: '#111827', marginBottom: 2 },
  cardSubtitle: { fontSize: 13, color: '#6b7280', fontWeight: '400' },

  /* Festival banner */
  festivalBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 10,
    borderWidth: 1,
    marginBottom: 20,
    gap: 6,
  },
  festivalText: { fontSize: 11, fontWeight: '600', letterSpacing: 0.2 },

  /* Inputs */
  inputGroup: { marginBottom: 14 },
  inputLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#374151',
    marginBottom: 6,
    letterSpacing: 0.4,
    textTransform: 'uppercase',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: '#e5e7eb',
    paddingHorizontal: 4,
  },
  inputIconBox: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: Colors.primary.main + '10',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  input: {
    flex: 1,
    paddingVertical: 14,
    fontSize: 15,
    color: '#111827',
    fontWeight: '500',
    letterSpacing: 0.3,
  },
  eyeBtn: { paddingHorizontal: 10, paddingVertical: 8 },

  /* Button */
  loginBtn: {
    marginTop: 8,
    borderRadius: 14,
    overflow: 'hidden',
    shadowColor: Colors.primary.main,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 12,
    elevation: 6,
  },
  loginBtnGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 15,
    gap: 8,
  },
  loginBtnText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#ffffff',
    letterSpacing: 0.3,
  },

  /* Footer */
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
    gap: 6,
  },
  footerText: { fontSize: 10, color: '#9ca3af', fontWeight: '500' },
});
