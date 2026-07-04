import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from './src/context/AuthContext';
import { ProjectProvider } from './src/context/ProjectContext';
import { VehicleProvider } from './src/context/VehicleContext';
import { ThemeProvider } from './src/context/ThemeContext';
import RootNavigator from './src/navigation/Navigation';

export default function App() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AuthProvider>
          <ProjectProvider>
            <VehicleProvider>
              <RootNavigator />
            </VehicleProvider>
          </ProjectProvider>
        </AuthProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
