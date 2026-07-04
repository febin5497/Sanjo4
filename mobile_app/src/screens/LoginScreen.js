import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet, Alert, ActivityIndicator, KeyboardAvoidingView, Platform, Image, Keyboard, TouchableWithoutFeedback } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Colors, GlassTokens, Gradients } from '../theme';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { API_BASE_URL } from '../services/api';
import { getActiveFestival } from '../utils/festival';

export const LoginScreen = () => {
  const { colors } = useTheme();
  const festival = getActiveFestival();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { sign } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }
    setIsLoading(true);
    try {
      const result = await sign(email, password);
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
              <View style={styles.topSection}>
                <View style={styles.logoContainer}>
                  <Image source={{ uri: `${API_BASE_URL}/static/logo.jpg?t=${Date.now()}` }} style={styles.logo} resizeMode="contain" />
                </View>
                <Text style={styles.appName}>BuildERP</Text>
                <Text style={styles.tagline}>Construction Management Platform</Text>
              </View>

              <View style={styles.card}>
                <Text style={styles.cardTitle}>Welcome Back</Text>
                <Text style={styles.cardSubtitle}>Sign in to your account</Text>

                {festival && (
                  <View style={[styles.festivalBanner, { backgroundColor: festival.colors[0] + '15', borderColor: festival.colors[0] + '40' }]}>
                    <MaterialCommunityIcons name={festival.icon} size={16} color={festival.colors[0]} />
                    <Text style={[styles.festivalText, { color: festival.colors[0] }]}>{festival.message}</Text>
                  </View>
                )}

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Email Address</Text>
                  <View style={styles.inputWrapper}>
                    <MaterialCommunityIcons name="email-outline" size={18} color={Colors.text.tertiary} style={styles.inputIcon} />
                    <TextInput
                      style={styles.input}
                      placeholder="Enter your email"
                      placeholderTextColor={Colors.text.tertiary}
                      value={email}
                      onChangeText={setEmail}
                      editable={!isLoading}
                      keyboardType="email-address"
                      autoCapitalize="none"
                      autoCorrect={false}
                    />
                  </View>
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Password</Text>
                  <View style={styles.inputWrapper}>
                    <MaterialCommunityIcons name="lock-outline" size={18} color={Colors.text.tertiary} style={styles.inputIcon} />
                    <TextInput
                      style={styles.input}
                      placeholder="Enter your password"
                      placeholderTextColor={Colors.text.tertiary}
                      value={password}
                      onChangeText={setPassword}
                      editable={!isLoading}
                      secureTextEntry
                      autoCapitalize="none"
                    />
                  </View>
                </View>

                <TouchableOpacity style={[styles.button, isLoading && { opacity: 0.7 }]} onPress={handleLogin} disabled={isLoading} activeOpacity={0.85}>
                  {isLoading ? (
                    <ActivityIndicator color="#ffffff" size="small" />
                  ) : (
                    <Text style={styles.buttonText}>Sign In</Text>
                  )}
                </TouchableOpacity>

                <View style={styles.footerRow}>
                  <MaterialCommunityIcons name="shield-check" size={14} color={Colors.text.tertiary} />
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
  topSection: { alignItems: 'center', marginBottom: 36 },
  logoContainer: { width: 72, height: 72, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.18)', justifyContent: 'center', alignItems: 'center', marginBottom: 14, borderWidth: 1, borderColor: 'rgba(255,255,255,0.25)' },
  logo: { width: 44, height: 44 },
  appName: { fontSize: 28, fontWeight: '800', color: '#ffffff', letterSpacing: -0.5, marginBottom: 4 },
  tagline: { fontSize: 13, color: 'rgba(255,255,255,0.7)', fontWeight: '500' },
  card: { width: '100%', maxWidth: 360, backgroundColor: 'rgba(255,255,255,0.95)', borderRadius: 20, padding: 28, shadowColor: '#000', shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.15, shadowRadius: 24, elevation: 12 },
  cardTitle: { fontSize: 20, fontWeight: '700', color: Colors.text.primary, marginBottom: 4 },
  cardSubtitle: { fontSize: 13, color: Colors.text.secondary, marginBottom: 24 },
  inputGroup: { marginBottom: 16 },
  inputLabel: { fontSize: 12, fontWeight: '600', color: Colors.text.secondary, marginBottom: 6, letterSpacing: 0.3 },
  inputWrapper: { flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.background.tertiary, borderRadius: 12, borderWidth: 1, borderColor: Colors.border.light, paddingHorizontal: 14 },
  inputIcon: { marginRight: 10 },
  input: { flex: 1, paddingVertical: 13, fontSize: 15, color: Colors.text.primary, fontWeight: '500' },
  button: { backgroundColor: Colors.primary.main, borderRadius: 12, paddingVertical: 15, alignItems: 'center', justifyContent: 'center', marginTop: 8, shadowColor: Colors.glow.indigo, shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.4, shadowRadius: 12, elevation: 6 },
  buttonText: { fontSize: 15, fontWeight: '700', color: '#ffffff', letterSpacing: 0.3 },
  festivalBanner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 8, paddingHorizontal: 14, borderRadius: 10, borderWidth: 1, marginBottom: 20, gap: 8 },
  festivalText: { fontSize: 12, fontWeight: '700', letterSpacing: 0.3 },
  footerRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 20, gap: 6 },
  footerText: { fontSize: 11, color: Colors.text.tertiary, fontWeight: '500' },
});
