const { readFileSync } = require('fs');
const path = require('path');

function parseEnv(filePath) {
  try {
    const content = readFileSync(filePath, 'utf8');
    const env = {};
    content.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const eqIdx = trimmed.indexOf('=');
        if (eqIdx > 0) {
          const key = trimmed.slice(0, eqIdx).trim();
          const val = trimmed.slice(eqIdx + 1).trim();
          env[key] = val;
        }
      }
    });
    return env;
  } catch {
    return {};
  }
}

module.exports = () => {
  const env = parseEnv(path.resolve(__dirname, '.env'));
  return {
    ...require('./app.json'),
    extra: {
      apiBaseUrl: env.API_BASE_URL || 'http://localhost:5000',
      appName: env.APP_NAME || 'BuildERP Employee Portal',
      appVersion: env.APP_VERSION || '1.0.0',
      enableLogging: env.ENABLE_LOGGING === 'true',
      apiTimeout: parseInt(env.API_TIMEOUT || '15000', 10),
      enableOfflineSupport: env.ENABLE_OFFLINE_SUPPORT === 'true',
      enablePushNotifications: env.ENABLE_PUSH_NOTIFICATIONS === 'true',
      enableLocationTracking: env.ENABLE_LOCATION_TRACKING === 'true',
    },
  };
};
