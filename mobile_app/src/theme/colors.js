/**
 * MODERN COLOR THEME v3.0
 * Clean, professional indigo/blue theme with warm neutrals
 * Modern card-based design with subtle shadows
 */

export const Colors = {
  // PRIMARY - Deep Indigo
  primary: {
    main: '#4F46E5',
    light: '#818CF8',
    lighter: '#C7D2FE',
    lightest: '#EEF2FF',
    dark: '#3730A3',
    darker: '#312E81',
    gradient: ['#6366F1', '#4F46E5'],
  },

  // SECONDARY - Sky Blue
  secondary: {
    main: '#0EA5E9',
    light: '#38BDF8',
    lighter: '#BAE6FD',
    dark: '#0284C7',
    gradient: ['#38BDF8', '#0EA5E9'],
  },

  // SUCCESS - Emerald
  success: {
    main: '#10B981',
    light: '#34D399',
    lighter: '#A7F3D0',
    lightest: '#ECFDF5',
    dark: '#059669',
    gradient: ['#34D399', '#10B981'],
  },

  // WARNING - Amber
  warning: {
    main: '#F59E0B',
    light: '#FBBF24',
    lighter: '#FDE68A',
    lightest: '#FFFBEB',
    dark: '#D97706',
    gradient: ['#FBBF24', '#F59E0B'],
  },

  // DANGER - Rose
  danger: {
    main: '#EF4444',
    light: '#F87171',
    lighter: '#FECACA',
    lightest: '#FEF2F2',
    dark: '#DC2626',
    gradient: ['#F87171', '#EF4444'],
  },

  // INFORMATION - Blue
  info: {
    main: '#3B82F6',
    light: '#60A5FA',
    lighter: '#BFDBFE',
    dark: '#2563EB',
  },

  // NEUTRAL SCALE - Warm Slate
  neutral: {
    950: '#0F172A',
    900: '#1E293B',
    800: '#334155',
    700: '#475569',
    600: '#64748B',
    500: '#94A3B8',
    400: '#CBD5E1',
    300: '#E2E8F0',
    200: '#F1F5F9',
    100: '#F8FAFC',
    50: '#FAFAFA',
  },

  // BACKGROUNDS
  background: {
    primary: '#F1F5F9',
    secondary: '#FFFFFF',
    tertiary: '#F8FAFC',
    dark: '#0F172A',
    card: '#FFFFFF',
    elevated: '#FFFFFF',
  },

  // TEXT COLORS
  text: {
    primary: '#1E293B',
    secondary: '#64748B',
    tertiary: '#94A3B8',
    inverse: '#FFFFFF',
    muted: '#CBD5E1',
  },

  // CARD SYSTEM - Clean white cards with shadows
  card: {
    white: '#FFFFFF',
    shadow: 'rgba(15, 23, 42, 0.08)',
    shadowLg: 'rgba(15, 23, 42, 0.12)',
    border: '#E2E8F0',
    borderLight: '#F1F5F9',
  },

  // SHADOW SYSTEM
  shadow: {
    xs: 'rgba(15, 23, 42, 0.04)',
    sm: 'rgba(15, 23, 42, 0.06)',
    md: 'rgba(15, 23, 42, 0.08)',
    lg: 'rgba(15, 23, 42, 0.12)',
    xl: 'rgba(15, 23, 42, 0.16)',
  },

  // GLOW EFFECTS
  glow: {
    indigo: 'rgba(79, 70, 229, 0.25)',
    blue: 'rgba(59, 130, 246, 0.25)',
    green: 'rgba(16, 185, 129, 0.20)',
    red: 'rgba(239, 68, 68, 0.20)',
    amber: 'rgba(245, 158, 11, 0.20)',
  },

  // BORDERS & DIVIDERS
  border: {
    light: '#E2E8F0',
    medium: '#CBD5E1',
    dark: '#94A3B8',
    focus: '#4F46E5',
  },

  // ICON BACKGROUNDS
  iconBg: {
    primary: '#EEF2FF',
    success: '#ECFDF5',
    warning: '#FFFBEB',
    danger: '#FEF2F2',
    info: '#EFF6FF',
    secondary: '#F0F9FF',
  },

  // STATUS INDICATORS
  status: {
    online: '#10B981',
    offline: '#94A3B8',
    pending: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  },
};

/**
 * Modern Design Tokens
 */
export const GlassTokens = {
  radius: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    full: 999,
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
  },
};

/**
 * Gradient Presets
 */
export const Gradients = {
  primary: {
    colors: ['#6366F1', '#4F46E5'],
    start: { x: 0, y: 0 },
    end: { x: 1, y: 1 },
  },
  secondary: {
    colors: ['#38BDF8', '#0EA5E9'],
    start: { x: 0, y: 0 },
    end: { x: 1, y: 1 },
  },
  success: {
    colors: ['#34D399', '#10B981'],
    start: { x: 0, y: 0 },
    end: { x: 1, y: 1 },
  },
  warning: {
    colors: ['#FBBF24', '#F59E0B'],
    start: { x: 0, y: 0 },
    end: { x: 1, y: 1 },
  },
  danger: {
    colors: ['#F87171', '#EF4444'],
    start: { x: 0, y: 0 },
    end: { x: 1, y: 1 },
  },
};

/**
 * Color Schemes - Light & Dark Mode
 */
export const ColorSchemes = {
  light: {
    primary: '#4F46E5',
    secondary: '#0EA5E9',
    background: {
      primary: '#F1F5F9',
      secondary: '#FFFFFF',
      tertiary: '#F8FAFC',
      surface: '#FFFFFF',
    },
    text: {
      primary: '#1E293B',
      secondary: '#64748B',
      tertiary: '#94A3B8',
      inverse: '#FFFFFF',
    },
    card: {
      white: '#FFFFFF',
      shadow: 'rgba(15, 23, 42, 0.08)',
      border: '#E2E8F0',
    },
    icon: {
      active: '#4F46E5',
      inactive: '#94A3B8',
      success: '#10B981',
      warning: '#F59E0B',
      danger: '#EF4444',
    },
    iconBg: {
      primary: '#EEF2FF',
      success: '#ECFDF5',
      warning: '#FFFBEB',
      danger: '#FEF2F2',
    },
    shadow: {
      sm: '#00000010',
      lg: '#00000020',
      xl: '#00000025',
    },
    glow: {
      blue: 'rgba(79, 70, 229, 0.3)',
    },
    border: {
      light: '#E2E8F0',
    },
    success: {
      main: '#10B981',
      lighter: '#ECFDF5',
    },
    warning: {
      main: '#F59E0B',
      lighter: '#FFFBEB',
    },
    danger: {
      main: '#EF4444',
      lighter: '#FEF2F2',
    },
    primaryLight: '#EEF2FF',
  },
  dark: {
    primary: '#818CF8',
    secondary: '#38BDF8',
    background: {
      primary: '#0F172A',
      secondary: '#1E293B',
      tertiary: '#334155',
      surface: '#1E293B',
    },
    text: {
      primary: '#F1F5F9',
      secondary: '#CBD5E1',
      tertiary: '#94A3B8',
      inverse: '#0F172A',
    },
    card: {
      white: '#1E293B',
      shadow: 'rgba(0, 0, 0, 0.3)',
      border: '#334155',
    },
    icon: {
      active: '#818CF8',
      inactive: '#64748B',
      success: '#34D399',
      warning: '#FBBF24',
      danger: '#F87171',
    },
    iconBg: {
      primary: '#312E81',
      success: '#064E3B',
      warning: '#78350F',
      danger: '#7F1D1D',
    },
    shadow: {
      sm: '#00000030',
      lg: '#00000060',
      xl: '#00000080',
    },
    glow: {
      blue: 'rgba(129, 140, 248, 0.4)',
    },
    border: {
      light: '#334155',
    },
    success: {
      main: '#34D399',
      lighter: '#064E3B',
    },
    warning: {
      main: '#FBBF24',
      lighter: '#78350F',
    },
    danger: {
      main: '#F87171',
      lighter: '#7F1D1D',
    },
    primaryLight: '#312E81',
  },
};
