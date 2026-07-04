/**
 * Theme Index
 * Central export point for all theme-related imports
 */

export { Colors, GlassTokens, Gradients, ColorSchemes } from './colors';
export { GlobalStyles } from './styles';

// Example usage in any screen:
// import { Colors, GlobalStyles, GlassTokens } from '../theme';
//
// const MyScreen = () => {
//   return (
//     <SafeAreaView style={GlobalStyles.container}>
//       <View style={GlobalStyles.glassCard}>
//         <Text style={GlobalStyles.title}>Hello</Text>
//       </View>
//     </SafeAreaView>
//   );
// };
