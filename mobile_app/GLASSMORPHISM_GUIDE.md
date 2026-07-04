# 🎨 Glassmorphism UI Theme Guide

## Overview
A modern, attractive Glassmorphism design system for the Construction Management Mobile App with vibrant color gradients and premium glass effects.

## 📁 Theme Files Location
- `src/theme/colors.js` - Color palette and design tokens
- `src/theme/styles.js` - Reusable style definitions
- `src/theme/index.js` - Centralized exports

## 🎯 Color Palette

### Primary Colors
- **Primary Blue**: `#0369a1` (main) → `#0ea5e9` (light)
- **Secondary Purple**: `#8b5cf6` (main) → `#a78bfa` (light)
- **Success Green**: `#10b981` (main) → `#34d399` (light)
- **Warning Gold**: `#f59e0b` (main) → `#fbbf24` (light)
- **Danger Red**: `#ef4444` (main) → `#f87171` (light)

### Special Accent Colors
- Cyan: `#06b6d4`
- Teal: `#14b8a6`
- Indigo: `#6366f1`
- Pink: `#ec4899`

## 💡 Key Features

### 1. Glass Effect
Frosted glass backgrounds with transparency:
```javascript
backgroundColor: Colors.glass.light,        // 25% white glass
borderColor: Colors.border.glass,           // Glass border
shadowRadius: 16,                           // Soft shadow
```

### 2. Gradient Support
Pre-defined color gradients:
```javascript
// Primary gradient
Gradients.primary.colors = ['#0ea5e9', '#0369a1']

// Success gradient
Gradients.success.colors = ['#34d399', '#10b981']

// Gold gradient
Gradients.gold.colors = ['#fbbf24', '#f59e0b']
```

### 3. Flexible Sizing
Consistent spacing and radius tokens:
```javascript
GlassTokens.spacing = {
  xs: 4,    sm: 8,    md: 12,   lg: 16,   xl: 24,   xxl: 32
}

GlassTokens.radius = {
  xs: 4,    sm: 8,    md: 12,   lg: 16,   xl: 20,   full: 999
}
```

## 📱 Usage Examples

### Basic Import
```javascript
import { Colors, GlobalStyles, GlassTokens } from '../theme';
```

### Glass Card
```javascript
<View style={GlobalStyles.glassCard}>
  <Text style={GlobalStyles.title}>Hello World</Text>
</View>
```

### Primary Button
```javascript
<TouchableOpacity style={GlobalStyles.buttonPrimary}>
  <Text style={GlobalStyles.buttonText}>Continue</Text>
</TouchableOpacity>
```

### Glass Input
```javascript
<TextInput
  style={GlobalStyles.inputGlass}
  placeholder="Enter text..."
  placeholderTextColor={Colors.text.tertiary}
/>
```

### Badge
```javascript
<View style={GlobalStyles.badgeSuccess}>
  <Text style={GlobalStyles.badgeText}>Active</Text>
</View>
```

## 🎨 Component Patterns

### Header Section
```javascript
<View style={GlobalStyles.section}>
  <Text style={GlobalStyles.headerTitle}>Dashboard</Text>
  <Text style={GlobalStyles.headerSubtitle}>Welcome back</Text>
</View>
```

### List Item with Glass Effect
```javascript
<View style={GlobalStyles.glassCard}>
  <View style={GlobalStyles.rowSpaceBetween}>
    <Text style={GlobalStyles.body}>Item Name</Text>
    <Text style={GlobalStyles.caption}>Details</Text>
  </View>
</View>
```

### Form Section
```javascript
<View style={GlobalStyles.section}>
  <Text style={GlobalStyles.label}>Full Name</Text>
  <TextInput
    style={GlobalStyles.inputGlass}
    placeholder="Enter your name"
    placeholderTextColor={Colors.text.tertiary}
  />
</View>
```

### Action Button with Shadow
```javascript
<TouchableOpacity style={GlobalStyles.buttonPrimary}>
  <Text style={GlobalStyles.buttonText}>Save Changes</Text>
</TouchableOpacity>
```

## 🌈 Color Usage Guidelines

### Text Colors
- **Primary Text**: `Colors.text.primary` - Main headings, important content
- **Secondary Text**: `Colors.text.secondary` - Descriptions, labels
- **Tertiary Text**: `Colors.text.tertiary` - Hints, disabled text

### Status Colors
- **Online**: `Colors.status.online` (Green)
- **Offline**: `Colors.status.offline` (Gray)
- **Pending**: `Colors.status.pending` (Amber)
- **Error**: `Colors.status.error` (Red)
- **Info**: `Colors.status.info` (Blue)

### Background Colors
- **Primary**: `Colors.background.primary` (White)
- **Secondary**: `Colors.background.secondary` (Light Blue)
- **Tertiary**: `Colors.background.tertiary` (Light Slate)

## 🎭 Screen Migration Examples

### Before (Old Style)
```javascript
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
```

### After (Glassmorphism)
```javascript
import { GlobalStyles, Colors } from '../theme';

// Use directly in components
<View style={GlobalStyles.glassCard}>
  <Text style={GlobalStyles.title}>Card Title</Text>
</View>
```

## 🔄 Updating Existing Screens

### Step 1: Import Theme
```javascript
import { Colors, GlobalStyles, GlassTokens } from '../theme';
```

### Step 2: Replace Container
```javascript
// Old
<View style={styles.container}>

// New
<SafeAreaView style={GlobalStyles.container}>
```

### Step 3: Replace Cards
```javascript
// Old
<View style={styles.card}>

// New
<View style={GlobalStyles.glassCard}>
```

### Step 4: Replace Text Styles
```javascript
// Old
<Text style={styles.heading}>Title</Text>

// New
<Text style={GlobalStyles.title}>Title</Text>
```

### Step 5: Replace Buttons
```javascript
// Old
<TouchableOpacity style={styles.button}>
  <Text>Click</Text>
</TouchableOpacity>

// New
<TouchableOpacity style={GlobalStyles.buttonPrimary}>
  <Text style={GlobalStyles.buttonText}>Click</Text>
</TouchableOpacity>
```

## 📊 Screens to Update

Priority order for implementing glassmorphism:

1. ✅ **DashboardScreen** (main entry point)
2. **LoginScreen** (first impression)
3. **AttendanceScreen** (frequent use)
4. **ExpensesScreen** (important feature)
5. **VehiclesScreen** (driver-focused)
6. **ProfileScreen** (user info)
7. **ProjectsScreen** (engineer-focused)
8. **TeamScreen** (collaboration)
9. **NotificationScreen** (alerts)
10. **ApprovalsScreen** (admin feature)

## 🎨 Advanced Features

### Custom Gradients
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

### Conditional Styling
```javascript
<View
  style={[
    GlobalStyles.badge,
    status === 'active' ? GlobalStyles.badgeSuccess : GlobalStyles.badgeDanger
  ]}
>
  <Text style={GlobalStyles.badgeText}>
    {status.toUpperCase()}
  </Text>
</View>
```

### Dynamic Colors
```javascript
<View
  style={{
    backgroundColor: isActive ? Colors.success.main : Colors.danger.main,
    padding: GlassTokens.spacing.lg,
  }}
>
  {/* Content */}
</View>
```

## 🚀 Performance Tips

1. **Memoize Styles**: Use `useMemo` for complex style calculations
2. **Avoid Inline Objects**: Define styles separately when possible
3. **Use Color Constants**: Avoid hardcoding hex values
4. **Batch Updates**: Group related style changes

## 📝 Naming Conventions

- `Glass*` - For frosted glass effect components
- `button*` - For button variations
- `text*` / `body` / `caption` - For text styles
- `badge*` - For status indicators
- `card*` - For card containers

## 🤝 Contributing

When adding new screens or components:

1. Import theme files
2. Use GlobalStyles for base styles
3. Use Colors for custom colors
4. Use GlassTokens for spacing/radius
5. Document any custom styles
6. Test on both light and dark backgrounds

## 📱 Device Support

Optimized for:
- iOS 13+
- Android 9+
- All screen sizes (320px - 768px width)
- Light mode (Dark mode support coming soon)

---

**Theme Version**: 1.0.0
**Last Updated**: March 2026
**Maintained By**: Construction Management Team
