# 🎨 Screen Glassmorphism Update Checklist

## ✅ Completed Screens
- [x] **LoginScreen** - Updated with glassmorphism theme
- [x] **DashboardScreen** - Partially updated with theme imports
- [x] **AttendanceScreen** - Fully updated with glassmorphism

## 📋 Remaining Screens to Update

### 🔧 ExpensesScreen
**Status**: Partially updated (theme imports needed)

**Quick Update Steps**:
```javascript
// Add to imports:
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';

// Replace in StyleSheet.create():
// - container: backgroundColor: Colors.background.secondary
// - card: Use GlobalStyles.glassCard
// - button: Use GlobalStyles.buttonPrimary
// - input: Use GlobalStyles.inputGlass
// - text: Use GlobalStyles.title, GlobalStyles.subtitle, etc.
// - spacing: Use GlassTokens.spacing values
```

### 🚗 VehiclesScreen
**Status**: Not started

**Priority**: High (driver-focused)

**Key Changes**:
- Import: `import { Colors, GlobalStyles, GlassTokens } from '../theme';`
- Container: `backgroundColor: Colors.background.secondary`
- Card styling: `...GlobalStyles.glassCard`
- Button styling: `...GlobalStyles.buttonPrimary`

### 👤 ProfileScreen
**Status**: Not started

**Priority**: Medium

### 📁 ProjectsScreen
**Status**: Not started

**Priority**: Medium

### 👥 TeamScreen
**Status**: Not started

**Priority**: Low

### 🔔 NotificationScreen
**Status**: Not started

**Priority**: Low

### ✅ ApprovalsScreen
**Status**: Not started

**Priority**: Medium

---

## 🎨 Quick Update Template

For any screen, follow this pattern:

### Step 1: Add Theme Import
```javascript
import { Colors, GlobalStyles, GlassTokens, Gradients } from '../theme';
```

### Step 2: Update Container
```javascript
// OLD:
<SafeAreaView style={styles.container}>

// NEW:
<SafeAreaView style={[GlobalStyles.container, { backgroundColor: Colors.background.secondary }]}>
```

### Step 3: Update Cards
```javascript
// OLD:
<View style={styles.card}>

// NEW:
<View style={GlobalStyles.glassCard}>
```

### Step 4: Update Buttons
```javascript
// OLD:
<TouchableOpacity style={styles.button}>

// NEW:
<TouchableOpacity style={GlobalStyles.buttonPrimary}>
```

### Step 5: Update Text Styles
```javascript
// OLD:
<Text style={styles.title}>Title</Text>
<Text style={styles.subtitle}>Subtitle</Text>
<Text style={styles.body}>Body</Text>

// NEW:
<Text style={GlobalStyles.title}>Title</Text>
<Text style={GlobalStyles.subtitle}>Subtitle</Text>
<Text style={GlobalStyles.body}>Body</Text>
```

### Step 6: Update StyleSheet
Replace hardcoded values:

```javascript
// OLD:
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  card: {
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
});

// NEW:
const styles = StyleSheet.create({
  container: {
    ...GlobalStyles.container,
    backgroundColor: Colors.background.secondary,
  },
  card: {
    ...GlobalStyles.glassCard,
  },
});
```

### Step 7: Update Spacing
```javascript
// OLD:
marginHorizontal: 16,
marginVertical: 12,
paddingHorizontal: 12,

// NEW:
marginHorizontal: GlassTokens.spacing.lg,
marginVertical: GlassTokens.spacing.md,
paddingHorizontal: GlassTokens.spacing.md,
```

### Step 8: Update Colors
```javascript
// OLD:
color: '#1976D2',
backgroundColor: '#4CAF50',
borderColor: '#E0E0E0',

// NEW:
color: Colors.primary.main,
backgroundColor: Colors.success.main,
borderColor: Colors.border.light,
```

---

## 🎯 Priority Order for Updates

1. **HIGH** (Most visible):
   - [x] LoginScreen
   - [x] AttendanceScreen
   - [ ] VehiclesScreen
   - [ ] ProjectsScreen

2. **MEDIUM** (Important features):
   - [ ] ExpensesScreen
   - [ ] ProfileScreen
   - [ ] ApprovalsScreen

3. **LOW** (Secondary screens):
   - [ ] TeamScreen
   - [ ] NotificationScreen

---

## 📊 Color Scheme Mapping

When updating, use this mapping:

| Old Color | New Theme Value |
|-----------|-----------------|
| #1976D2 (Blue) | Colors.primary.main |
| #4CAF50 (Green) | Colors.success.main |
| #F57C00 (Orange) | Colors.warning.main |
| #D32F2F (Red) | Colors.danger.main |
| #ffffff (White) | Colors.background.primary |
| #f0f0f0 (Light Gray) | Colors.background.secondary |
| #1A1A1A (Dark Gray) | Colors.text.primary |
| #6B7280 (Medium Gray) | Colors.text.secondary |

---

## 🚀 Tips for Efficient Updates

1. **Search & Replace**: Use your editor's find/replace to update color values
2. **Batch Updates**: Update similar files together
3. **Test as You Go**: Check each screen in the app after updating
4. **Component Reuse**: Identify common patterns and create reusable components
5. **Documentation**: Keep notes of any custom styling needed

---

## 📱 Testing Checklist

After updating each screen, verify:

- [ ] All text is readable with new colors
- [ ] Buttons have proper shadow effect
- [ ] Glass cards have correct transparency
- [ ] Spacing looks balanced
- [ ] Icons are properly colored
- [ ] No layout issues or overlaps
- [ ] Responsive design maintained
- [ ] Animations/transitions still work

---

## 🎨 Additional Customizations

For screens that need extra flair:

### Add Gradient Headers
```javascript
<LinearGradient
  colors={Gradients.primary.colors}
  start={Gradients.primary.start}
  end={Gradients.primary.end}
  style={GlobalStyles.glassCard}
>
  {/* Content */}
</LinearGradient>
```

### Add Status Badges
```javascript
<View style={GlobalStyles.badgeSuccess}>
  <Text style={GlobalStyles.badgeText}>Active</Text>
</View>
```

### Add Loading States
```javascript
<View style={GlobalStyles.centered}>
  <ActivityIndicator size="large" color={Colors.primary.main} />
  <Text style={GlobalStyles.caption}>Loading...</Text>
</View>
```

---

**Last Updated**: March 29, 2026
**Theme Version**: 1.0.0
