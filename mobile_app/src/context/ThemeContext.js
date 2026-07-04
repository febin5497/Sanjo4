import React, { createContext, useContext, useState, useEffect } from 'react';
import { useColorScheme, AppState } from 'react-native';
import { ColorSchemes } from '../theme/colors';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const systemColorScheme = useColorScheme(); // 'light' or 'dark'
  const [isDarkMode, setIsDarkMode] = useState(systemColorScheme === 'dark');
  const [appState, setAppState] = useState(AppState.currentState);

  // Listen for app state changes to re-detect theme
  useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => {
      subscription.remove();
    };
  }, []);

  const handleAppStateChange = (nextAppState) => {
    setAppState(nextAppState);
    // Re-detect system theme when app comes to foreground
    if (nextAppState === 'active' && systemColorScheme !== null) {
      setIsDarkMode(systemColorScheme === 'dark');
    }
  };

  useEffect(() => {
    if (systemColorScheme !== null && systemColorScheme !== undefined) {
      setIsDarkMode(systemColorScheme === 'dark');
    }
  }, [systemColorScheme]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  // Default to light mode with proper fallback
  const colors = (ColorSchemes && (isDarkMode ? ColorSchemes.dark : ColorSchemes.light)) || ColorSchemes?.light || {};

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
