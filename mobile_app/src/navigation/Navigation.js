import React from 'react';
import { NavigationContainer, useNavigation } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, StyleSheet, Platform, TouchableOpacity, Alert } from 'react-native';
import { MaterialCommunityIcons, MaterialIcons } from '@expo/vector-icons';

import { LoginScreen } from '../screens/LoginScreen';
import { ChangePasswordScreen } from '../screens/ChangePasswordScreen';
import { DashboardScreen } from '../screens/DashboardScreen';
import { AttendanceScreen } from '../screens/AttendanceScreen';
import { ProfileScreen } from '../screens/ProfileScreen';
import { ProjectsScreen } from '../screens/ProjectsScreen';
import { TeamScreen } from '../screens/TeamScreen';
import { VehiclesScreen } from '../screens/VehiclesScreen';
import { ExpensesScreen } from '../screens/ExpensesScreen';
import { ApprovalsScreen } from '../screens/ApprovalsScreen';
import NotificationScreen from '../screens/NotificationScreen';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useNotifications } from '../context/NotificationContext';
import { Colors, GlassTokens } from '../theme';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Stack navigators for each tab
const DashboardStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="DashboardTab" component={DashboardScreen} />
  </Stack.Navigator>
);

const AttendanceStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="AttendanceTab" component={AttendanceScreen} />
  </Stack.Navigator>
);

const ProfileStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="ProfileTab" component={ProfileScreen} />
  </Stack.Navigator>
);

const ProjectsStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="ProjectsTab" component={ProjectsScreen} />
  </Stack.Navigator>
);

const TeamStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="TeamTab" component={TeamScreen} />
  </Stack.Navigator>
);

const VehiclesStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="VehiclesTab" component={VehiclesScreen} />
  </Stack.Navigator>
);

const ExpensesStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="ExpensesTab" component={ExpensesScreen} />
  </Stack.Navigator>
);

const ApprovalsStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="ApprovalsTab" component={ApprovalsScreen} />
  </Stack.Navigator>
);

const NotificationsStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="NotificationsTab" component={NotificationScreen} />
  </Stack.Navigator>
);

/**
 * Notification bell icon with unread badge
 */
const NotificationBell = ({ themeColors }) => {
  const { unreadCount } = useNotifications();
  const navigation = useNavigation();

  return (
    <TouchableOpacity
      onPress={() => navigation.navigate('Notifications')}
      style={tabBarStyles.bellContainer}
      activeOpacity={0.7}
    >
      <MaterialCommunityIcons
        name="bell-outline"
        size={24}
        color={themeColors.text.primary}
      />
      {unreadCount > 0 && (
        <View style={[tabBarStyles.badge, { backgroundColor: themeColors.icon.danger }]}>
          <Text style={tabBarStyles.badgeText}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

/**
 * Custom glass tab bar component with curved top and active indicators
 */
const GlassTabBar = ({ state, descriptors, navigation, themeColors }) => {
  const { signOut } = useAuth();
  const focusedOptions = descriptors[state.routes[state.index].key].options;

  if (focusedOptions.tabBarVisible === false) {
    return null;
  }

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: () => signOut() },
    ]);
  };

  return (
    <View style={tabBarStyles.containerOuter}>
      <View style={[tabBarStyles.gradient, { backgroundColor: themeColors.background.surface }]}>
        <View style={tabBarStyles.content}>
          {state.routes.map((route, index) => {
            const { options } = descriptors[route.key];
            const isFocused = state.index === index;
            const label = options.tabBarLabel || options.title || route.name;

            const onPress = () => {
              const event = navigation.emit({
                type: 'tabPress',
                target: route.key,
                canPreventDefault: true,
              });
              if (!isFocused && !event.defaultPrevented) {
                navigation.navigate(route.name);
              }
            };

            const onLongPress = () => {
              navigation.emit({
                type: 'tabLongPress',
                target: route.key,
              });
            };

            return (
              <View key={route.name} style={tabBarStyles.tabItem}>
                <View
                  style={[
                    tabBarStyles.tabButton,
                    isFocused && [
                      tabBarStyles.tabButtonActive,
                      { backgroundColor: themeColors.primary + '18' },
                      { borderColor: themeColors.primary + '30' },
                    ],
                  ]}
                >
                  <TouchableOpacity
                    accessibilityRole="button"
                    accessibilityStates={isFocused ? ['selected'] : []}
                    accessibilityLabel={options.tabBarAccessibilityLabel}
                    testID={options.tabBarTestID}
                    onPress={onPress}
                    onLongPress={onLongPress}
                    activeOpacity={0.7}
                    style={tabBarStyles.touchable}
                  >
                    <View style={tabBarStyles.iconWrapper}>
                      {options.tabBarIcon
                        ? options.tabBarIcon({
                            color: isFocused ? themeColors.primary : themeColors.icon.inactive,
                            size: isFocused ? 22 : 20,
                          })
                        : null}
                    </View>
                    <Text
                      style={[
                        tabBarStyles.label,
                        { color: isFocused ? themeColors.primary : themeColors.text.tertiary },
                        isFocused && tabBarStyles.labelActive,
                      ]}
                      numberOfLines={1}
                    >
                      {label}
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            );
          })}
          {/* Notification bell */}
          <View style={tabBarStyles.bellOuterContainer}>
            <NotificationBell themeColors={themeColors} />
          </View>
          {/* Logout button */}
          <View style={tabBarStyles.logoutContainer}>
            <TouchableOpacity onPress={handleLogout} activeOpacity={0.6} style={tabBarStyles.logoutButton}>
              <MaterialCommunityIcons name="logout" size={22} color={themeColors.icon.danger} />
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
};

const tabBarStyles = StyleSheet.create({
  containerOuter: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 16,
  },
  gradient: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    borderTopWidth: 1,
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.25)',
    overflow: 'hidden',
  },
  content: {
    flexDirection: 'row',
    paddingTop: 8,
    paddingBottom: Platform.OS === 'ios' ? 24 : 12,
    paddingHorizontal: 8,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
  },
  tabButton: {
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  tabButtonActive: {
    borderWidth: 1,
  },
  touchable: {
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 60,
  },
  iconWrapper: {
    marginBottom: 2,
  },
  label: {
    fontSize: 10,
    fontWeight: '600',
    textAlign: 'center',
  },
  labelActive: {
    fontWeight: '800',
    fontSize: 10.5,
  },
  logoutContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingLeft: 4,
    borderLeftWidth: 1,
    borderLeftColor: 'rgba(0,0,0,0.06)',
    marginLeft: 4,
  },
  logoutButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  bellOuterContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingLeft: 4,
    borderLeftWidth: 1,
    borderLeftColor: 'rgba(0,0,0,0.06)',
    marginLeft: 4,
  },
  bellContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badge: {
    position: 'absolute',
    top: -2,
    right: -4,
    minWidth: 18,
    height: 18,
    borderRadius: 9,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 4,
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
});

/**
 * Get role-specific tabs based on user role
 * Different roles see different navigation options
 */
const getRoleBasedTabs = (userRole, themeColors) => {
  const commonOptions = {
    headerShown: false,
    tabBarShowLabel: false,
    tabBarStyle: { display: 'none' },
  };

  return {
    screenOptions: commonOptions,
    defaultRole: [
      // Dashboard tab (all roles)
      {
        name: 'Dashboard',
        component: DashboardStack,
        options: {
          title: 'Dashboard',
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="home" size={size} color={color} />
          ),
        },
      },
      // Attendance tab (all roles)
      {
        name: 'Attendance',
        component: AttendanceStack,
        options: {
          title: 'Attendance',
          tabBarLabel: 'Attendance',

          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="check-circle" size={size} color={color} />
          ),
        },
      },
      // Notifications tab (all roles)
      {
        name: 'Notifications',
        component: NotificationsStack,
        options: {
          title: 'Notifications',
          tabBarLabel: 'Notifications',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="bell" size={size} color={color} />
          ),
        },
      },
      // Profile tab (all roles)
      {
        name: 'Profile',
        component: ProfileStack,
        options: {
          title: 'Profile',
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" size={size} color={color} />
          ),
        },
      },
    ],
    driver: [
      {
        name: 'Dashboard',
        component: DashboardStack,
        options: {
          title: 'Dashboard',
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="home" size={size} color={color} />
          ),
        },
      },
      // Attendance tab for drivers
      {
        name: 'Attendance',
        component: AttendanceStack,
        options: {
          title: 'Attendance',
          tabBarLabel: 'Attendance',

          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="check-circle" size={size} color={color} />
          ),
        },
      },
      // Vehicles tab for drivers
      {
        name: 'Vehicles',
        component: VehiclesStack,
        options: {
          title: 'My Vehicles',
          tabBarLabel: 'Vehicles',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="car" size={size} color={color} />
          ),
        },
      },
      // Notifications tab for drivers
      {
        name: 'Notifications',
        component: NotificationsStack,
        options: {
          title: 'Notifications',
          tabBarLabel: 'Notifications',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="bell" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Profile',
        component: ProfileStack,
        options: {
          title: 'Profile',
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" size={size} color={color} />
          ),
        },
      },
    ],
    engineer: [
      {
        name: 'Dashboard',
        component: DashboardStack,
        options: {
          title: 'Dashboard',
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="home" size={size} color={color} />
          ),
        },
      },
      // Expenses tab for engineers
      {
        name: 'Expenses',
        component: ExpensesStack,
        options: {
          title: 'My Expenses',
          tabBarLabel: 'Expenses',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="wallet" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Attendance',
        component: AttendanceStack,
        options: {
          title: 'Attendance',
          tabBarLabel: 'Attendance',

          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="check-circle" size={size} color={color} />
          ),
        },
      },
      // Notifications tab for engineers
      {
        name: 'Notifications',
        component: NotificationsStack,
        options: {
          title: 'Notifications',
          tabBarLabel: 'Notifications',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="bell" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Profile',
        component: ProfileStack,
        options: {
          title: 'Profile',
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" size={size} color={color} />
          ),
        },
      },
    ],
    hr: [
      {
        name: 'Dashboard',
        component: DashboardStack,
        options: {
          title: 'Dashboard',
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="home" size={size} color={color} />
          ),
        },
      },
      // Approvals tab for HR
      {
        name: 'Approvals',
        component: ApprovalsStack,
        options: {
          title: 'Approvals',
          tabBarLabel: 'Approvals',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="checkbox-marked-circle" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Attendance',
        component: AttendanceStack,
        options: {
          title: 'Attendance',
          tabBarLabel: 'Attendance',

          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="clipboard-list" size={size} color={color} />
          ),
        },
      },
      // Notifications tab for HR
      {
        name: 'Notifications',
        component: NotificationsStack,
        options: {
          title: 'Notifications',
          tabBarLabel: 'Notifications',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="bell" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Profile',
        component: ProfileStack,
        options: {
          title: 'Profile',
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" size={size} color={color} />
          ),
        },
      },
    ],
    manager: [
      {
        name: 'Dashboard',
        component: DashboardStack,
        options: {
          title: 'Dashboard',
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="home" size={size} color={color} />
          ),
        },
      },
      // Projects tab for managers
      {
        name: 'Projects',
        component: ProjectsStack,
        options: {
          title: 'Projects',
          tabBarLabel: 'Projects',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="folder-multiple" size={size} color={color} />
          ),
        },
      },
      // Team tab for managers
      {
        name: 'Team',
        component: TeamStack,
        options: {
          title: 'Team',
          tabBarLabel: 'Team',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account-multiple" size={size} color={color} />
          ),
        },
      },
      // Notifications tab for managers
      {
        name: 'Notifications',
        component: NotificationsStack,
        options: {
          title: 'Notifications',
          tabBarLabel: 'Notifications',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="bell" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Profile',
        component: ProfileStack,
        options: {
          title: 'Profile',
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" size={size} color={color} />
          ),
        },
      },
    ],
    admin: [
      {
        name: 'Dashboard',
        component: DashboardStack,
        options: {
          title: 'Dashboard',
          tabBarLabel: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="home" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Projects',
        component: ProjectsStack,
        options: {
          title: 'Projects',
          tabBarLabel: 'Projects',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="folder-multiple" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Team',
        component: TeamStack,
        options: {
          title: 'Team',
          tabBarLabel: 'Team',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account-multiple" size={size} color={color} />
          ),
        },
      },
      // Notifications tab for admin
      {
        name: 'Notifications',
        component: NotificationsStack,
        options: {
          title: 'Notifications',
          tabBarLabel: 'Notifications',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="bell" size={size} color={color} />
          ),
        },
      },
      {
        name: 'Profile',
        component: ProfileStack,
        options: {
          title: 'Profile',
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="account" size={size} color={color} />
          ),
        },
      },
    ],
  };
};

const RootNavigator = () => {
  const { state } = useAuth();
  const { colors } = useTheme();
  const userRole = state.user?.role?.toLowerCase();
  const tabConfig = getRoleBasedTabs(userRole, colors);

  // Get tabs for the user's role, fallback to default
  const tabs = tabConfig[userRole] || tabConfig.defaultRole;

  return (
    <NavigationContainer>
      {state.userToken == null ? (
        // Login screen for unauthenticated users
        <Stack.Navigator
          screenOptions={{
            headerShown: false,
            animationEnabled: false,
          }}
        >
          <Stack.Screen name="Login" component={LoginScreen} />
        </Stack.Navigator>
      ) : state.passwordChangeRequired ? (
        // Force password change before accessing the app
        <Stack.Navigator
          screenOptions={{
            headerShown: false,
            animationEnabled: false,
          }}
        >
          <Stack.Screen name="ChangePassword" component={ChangePasswordScreen} />
        </Stack.Navigator>
      ) : (
        // Authenticated app with role-based tabs
        <Tab.Navigator
          screenOptions={tabConfig.screenOptions}
          tabBar={(props) => <GlassTabBar {...props} themeColors={colors} />}
        >
          {tabs.map((tab) => (
            <Tab.Screen
              key={tab.name}
              name={tab.name}
              component={tab.component}
              options={tab.options}
            />
          ))}
        </Tab.Navigator>
      )}
    </NavigationContainer>
  );
};

export default RootNavigator;
