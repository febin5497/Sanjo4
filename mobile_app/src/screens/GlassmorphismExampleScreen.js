/**
 * Glassmorphism Example Screen
 *
 * This screen demonstrates how to use the new glassmorphism theme
 * to create beautiful, modern UI components.
 *
 * Copy patterns from this screen to apply to other screens.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  TextInput,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
import { useTheme } from '../context/ThemeContext';

const GlassmorphismExampleScreen = () => {
  const { colors } = useTheme();
  const [searchText, setSearchText] = useState('');
  const [selectedBadge, setSelectedBadge] = useState('all');

  return (
    <SafeAreaView style={[GlobalStyles.container, { backgroundColor: colors.background.primary }]}>
      <ScrollView showsVerticalScrollIndicator={false} style={{ backgroundColor: colors.background.primary }}>
        {/* ========== HEADER SECTION ========== */}
        <LinearGradient
          colors={Gradients.success.colors}
          start={Gradients.success.start}
          end={Gradients.success.end}
          style={styles.headerGradient}
        >
          <View style={GlobalStyles.section}>
            <Text style={[GlobalStyles.headerTitle, { color: colors.text.inverse }]}>
              Glassmorphism
            </Text>
            <Text style={[GlobalStyles.headerSubtitle, { color: colors.text.inverse }]}>
              Modern UI Components
            </Text>
          </View>
        </LinearGradient>

        {/* ========== SEARCH INPUT ========== */}
        <View style={GlobalStyles.section}>
          <Text style={GlobalStyles.label}>Search</Text>
          <TextInput
            style={[GlobalStyles.inputGlass, { marginTop: GlassTokens.spacing.sm }]}
            placeholder="Search components..."
            value={searchText}
            onChangeText={setSearchText}
            placeholderTextColor={Colors.text.tertiary}
          />
        </View>

        {/* ========== GLASS CARDS SECTION ========== */}
        <View style={GlobalStyles.section}>
          <Text style={[GlobalStyles.subtitle, { marginBottom: GlassTokens.spacing.lg }]}>
            Glass Cards
          </Text>

          {/* Standard Glass Card */}
          <View style={GlobalStyles.glassCard}>
            <Text style={GlobalStyles.subtitle}>Standard Glass Card</Text>
            <Text style={[GlobalStyles.body, { marginTop: GlassTokens.spacing.sm }]}>
              This is a frosted glass card with subtle transparency and blur effect.
            </Text>
            <View style={[GlobalStyles.row, { marginTop: GlassTokens.spacing.md }]}>
              <Text style={GlobalStyles.caption}>Elegant</Text>
              <Text style={[GlobalStyles.caption, { marginLeft: GlassTokens.spacing.lg }]}>
                Modern
              </Text>
            </View>
          </View>

          {/* Large Glass Card */}
          <View style={GlobalStyles.glassCardLarge}>
            <Text style={GlobalStyles.subtitle}>Large Glass Card</Text>
            <Text style={[GlobalStyles.body, { marginTop: GlassTokens.spacing.md }]}>
              With more padding and space for detailed content. Perfect for featured items or important information.
            </Text>
          </View>

          {/* Frosted Card */}
          <View style={GlobalStyles.frostedCard}>
            <Text style={GlobalStyles.subtitle}>Frosted Glass Card</Text>
            <Text style={[GlobalStyles.body, { marginTop: GlassTokens.spacing.sm }]}>
              Enhanced blur effect with stronger glass appearance for premium feel.
            </Text>
          </View>
        </View>

        {/* ========== GRADIENT CARDS SECTION ========== */}
        <View style={GlobalStyles.section}>
          <Text style={[GlobalStyles.subtitle, { marginBottom: GlassTokens.spacing.lg }]}>
            Gradient Cards
          </Text>

          {/* Primary Gradient */}
          <LinearGradient
            colors={Gradients.primary.colors}
            start={Gradients.primary.start}
            end={Gradients.primary.end}
            style={[GlobalStyles.glassCard, { backgroundColor: 'transparent' }]}
          >
            <Text style={[GlobalStyles.subtitle, { color: '#ffffff' }]}>Primary Gradient</Text>
            <Text style={[GlobalStyles.body, { color: 'rgba(255,255,255,0.9)', marginTop: GlassTokens.spacing.sm }]}>
              Beautiful blue gradient for primary actions
            </Text>
          </LinearGradient>

          {/* Success Gradient */}
          <LinearGradient
            colors={Gradients.success.colors}
            start={Gradients.success.start}
            end={Gradients.success.end}
            style={[GlobalStyles.glassCard, { backgroundColor: 'transparent', marginTop: GlassTokens.spacing.md }]}
          >
            <Text style={[GlobalStyles.subtitle, { color: '#ffffff' }]}>Success Gradient</Text>
            <Text style={[GlobalStyles.body, { color: 'rgba(255,255,255,0.9)', marginTop: GlassTokens.spacing.sm }]}>
              Vibrant green for positive actions
            </Text>
          </LinearGradient>

          {/* Teal Gradient */}
          <LinearGradient
            colors={Gradients.teal.colors}
            start={Gradients.teal.start}
            end={Gradients.teal.end}
            style={[GlobalStyles.glassCard, { backgroundColor: 'transparent', marginTop: GlassTokens.spacing.md }]}
          >
            <Text style={[GlobalStyles.subtitle, { color: '#ffffff' }]}>Teal Gradient</Text>
            <Text style={[GlobalStyles.body, { color: 'rgba(255,255,255,0.9)', marginTop: GlassTokens.spacing.sm }]}>
              Elegant teal for modern features
            </Text>
          </LinearGradient>

          {/* Warning Gradient */}
          <LinearGradient
            colors={Gradients.warning.colors}
            start={Gradients.warning.start}
            end={Gradients.warning.end}
            style={[GlobalStyles.glassCard, { backgroundColor: 'transparent', marginTop: GlassTokens.spacing.md }]}
          >
            <Text style={[GlobalStyles.subtitle, { color: '#ffffff' }]}>Warning Gradient</Text>
            <Text style={[GlobalStyles.body, { color: 'rgba(255,255,255,0.9)', marginTop: GlassTokens.spacing.sm }]}>
              Warm amber for warnings and highlights
            </Text>
          </LinearGradient>
        </View>

        {/* ========== BUTTONS SECTION ========== */}
        <View style={GlobalStyles.section}>
          <Text style={[GlobalStyles.subtitle, { marginBottom: GlassTokens.spacing.lg }]}>
            Buttons
          </Text>

          <TouchableOpacity style={GlobalStyles.buttonPrimary}>
            <Text style={GlobalStyles.buttonText}>Primary Button</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[GlobalStyles.buttonSecondary, { marginTop: GlassTokens.spacing.md }]}>
            <Text style={GlobalStyles.buttonText}>Secondary Button</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[GlobalStyles.buttonGlass, { marginTop: GlassTokens.spacing.md }]}>
            <Text style={GlobalStyles.buttonTextSecondary}>Glass Button</Text>
          </TouchableOpacity>

          <View style={[GlobalStyles.row, { marginTop: GlassTokens.spacing.md, gap: GlassTokens.spacing.md }]}>
            <TouchableOpacity style={[GlobalStyles.buttonSmall, GlobalStyles.buttonPrimary, { flex: 1 }]}>
              <Text style={GlobalStyles.buttonText}>Save</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[GlobalStyles.buttonSmall, GlobalStyles.buttonGlass, { flex: 1 }]}>
              <Text style={GlobalStyles.buttonTextSecondary}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* ========== BADGES SECTION ========== */}
        <View style={GlobalStyles.section}>
          <Text style={[GlobalStyles.subtitle, { marginBottom: GlassTokens.spacing.lg }]}>
            Status Badges
          </Text>

          <View style={[GlobalStyles.row, { flexWrap: 'wrap', gap: GlassTokens.spacing.sm }]}>
            <TouchableOpacity
              style={GlobalStyles.badgePrimary}
              onPress={() => setSelectedBadge('all')}
            >
              <Text style={GlobalStyles.badgeText}>Primary</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={GlobalStyles.badgeSuccess}
              onPress={() => setSelectedBadge('success')}
            >
              <Text style={GlobalStyles.badgeText}>Active</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={GlobalStyles.badgeWarning}
              onPress={() => setSelectedBadge('warning')}
            >
              <Text style={GlobalStyles.badgeText}>Pending</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={GlobalStyles.badgeDanger}
              onPress={() => setSelectedBadge('danger')}
            >
              <Text style={GlobalStyles.badgeText}>Critical</Text>
            </TouchableOpacity>
          </View>

          <Text style={[GlobalStyles.caption, { marginTop: GlassTokens.spacing.lg }]}>
            Selected: {selectedBadge}
          </Text>
        </View>

        {/* ========== LIST ITEMS SECTION ========== */}
        <View style={GlobalStyles.section}>
          <Text style={[GlobalStyles.subtitle, { marginBottom: GlassTokens.spacing.lg }]}>
            List Items
          </Text>

          {[1, 2, 3].map((item) => (
            <View key={item} style={GlobalStyles.glassCard}>
              <View style={GlobalStyles.rowSpaceBetween}>
                <View style={{ flex: 1 }}>
                  <Text style={GlobalStyles.subtitle}>Item {item}</Text>
                  <Text style={[GlobalStyles.caption, { marginTop: GlassTokens.spacing.xs }]}>
                    Description of item {item}
                  </Text>
                </View>
                <View style={GlobalStyles.badgeSuccess}>
                  <Text style={GlobalStyles.badgeText}>Active</Text>
                </View>
              </View>
            </View>
          ))}
        </View>

        {/* ========== COLOR PALETTE SECTION ========== */}
        <View style={GlobalStyles.section}>
          <Text style={[GlobalStyles.subtitle, { marginBottom: GlassTokens.spacing.lg }]}>
            Color Palette
          </Text>

          <View style={[GlobalStyles.row, { flexWrap: 'wrap', gap: GlassTokens.spacing.sm }]}>
            <View style={styles.colorBox}>
              <View style={[styles.colorDot, { backgroundColor: Colors.primary.main }]} />
              <Text style={GlobalStyles.caption}>Primary</Text>
            </View>

            <View style={styles.colorBox}>
              <View style={[styles.colorDot, { backgroundColor: Colors.secondary.main }]} />
              <Text style={GlobalStyles.caption}>Secondary</Text>
            </View>

            <View style={styles.colorBox}>
              <View style={[styles.colorDot, { backgroundColor: Colors.success.main }]} />
              <Text style={GlobalStyles.caption}>Success</Text>
            </View>

            <View style={styles.colorBox}>
              <View style={[styles.colorDot, { backgroundColor: Colors.warning.main }]} />
              <Text style={GlobalStyles.caption}>Warning</Text>
            </View>

            <View style={styles.colorBox}>
              <View style={[styles.colorDot, { backgroundColor: Colors.danger.main }]} />
              <Text style={GlobalStyles.caption}>Danger</Text>
            </View>

            <View style={styles.colorBox}>
              <View style={[styles.colorDot, { backgroundColor: Colors.accent.cyan }]} />
              <Text style={GlobalStyles.caption}>Cyan</Text>
            </View>
          </View>
        </View>

        {/* ========== FOOTER SPACING ========== */}
        <View style={{ height: GlassTokens.spacing.xxl }} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  headerGradient: {
    borderBottomLeftRadius: GlassTokens.radius.xl,
    borderBottomRightRadius: GlassTokens.radius.xl,
    overflow: 'hidden',
  },
  colorBox: {
    alignItems: 'center',
    marginBottom: GlassTokens.spacing.md,
  },
  colorDot: {
    width: 40,
    height: 40,
    borderRadius: GlassTokens.radius.md,
    marginBottom: GlassTokens.spacing.xs,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
});

export default GlassmorphismExampleScreen;
