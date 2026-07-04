# BuildERP Mobile App - Employee Portal

A React Native mobile application for construction workers and employees to manage attendance, view tasks, and access their profile information.

## 📋 Features

### ✅ Implemented Features

1. **Authentication**
   - Login with email and password
   - JWT token management (secure storage)
   - Automatic logout on token expiry

2. **Attendance Management**
   - Punch in/out with photo capture
   - Real-time status display
   - Attendance history (last 30 days)
   - Attendance statistics (Present, Absent, Half Days, Attendance %)

3. **Dashboard**
   - Quick stats display (Present, Absent, Attendance %, Half Days)
   - Assigned tasks list
   - Quick action buttons
   - Date display

4. **Profile Management**
   - Personal information (name, email, phone, joining date)
   - Salary information (basic, PF, ESI)
   - Employee ID
   - Logout functionality

### 🔄 API Integration

The app connects to your Flask backend using REST API:

- **Base URL**: `http://192.168.1.100:5000` (configurable in `src/services/api.js`)
- **Authentication**: Bearer token (JWT) in Authorization header
- **Request Format**: JSON with multipart/form-data for file uploads

## 🚀 Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- Expo CLI: `npm install -g expo-cli`
- Android Studio or Xcode (for native builds)
- Physical device or emulator

### Installation

1. **Navigate to the mobile app directory:**
   ```bash
   cd mobile_app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure the API endpoint:**
   - Open `src/services/api.js`
   - Change `API_BASE_URL` to your backend URL:
     ```javascript
     const API_BASE_URL = 'http://192.168.1.100:5000'; // Change this to your backend IP
     ```

### Running the App

#### Development (Expo)

1. **Start the development server:**
   ```bash
   npm start
   ```

2. **Run on Android:**
   ```bash
   npm run android
   ```

3. **Run on iOS:**
   ```bash
   npm run ios
   ```

4. **Run on Web:**
   ```bash
   npm run web
   ```

#### Production Build

**Android (APK):**
```bash
eas build --platform android
```

**iOS:**
```bash
eas build --platform ios
```

## 📱 App Structure

```
mobile_app/
├── src/
│   ├── screens/              # Screen components
│   │   ├── LoginScreen.js
│   │   ├── DashboardScreen.js
│   │   ├── AttendanceScreen.js
│   │   └── ProfileScreen.js
│   ├── services/             # API service layer
│   │   └── api.js
│   ├── context/              # Context providers
│   │   └── AuthContext.js
│   ├── navigation/           # Navigation setup
│   │   └── Navigation.js
│   └── styles/               # Shared styles
├── App.js                    # Main app component
├── app.json                  # Expo configuration
└── package.json
```

## 🔐 Security

### Token Management
- JWT tokens are stored securely using `expo-secure-store`
- Tokens are automatically added to all API requests
- Invalid/expired tokens trigger automatic logout

### Sensitive Data
- Passwords are never stored locally
- User data is cached locally during the session
- Clear local storage on logout

## 📡 API Endpoints Used

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Attendance
- `POST /api/attendance/punch-in` - Record punch in with photo
- `POST /api/attendance/punch-out` - Record punch out with photo
- `GET /api/attendance/list/{staffId}` - Get attendance history
- `GET /api/attendance/stats/{staffId}` - Get attendance statistics
- `GET /api/attendance/status/{staffId}` - Get current punch status

### Staff
- `GET /api/staff/{staffId}` - Get staff profile
- `PUT /api/staff/{staffId}` - Update staff profile

### Tasks
- `GET /api/tasks/assigned/{staffId}` - Get assigned tasks
- `PUT /api/tasks/{taskId}` - Update task status

## 🛠️ Configuration

### Backend URL Configuration

Edit `src/services/api.js`:

```javascript
// For localhost development
const API_BASE_URL = 'http://localhost:5000';

// For network testing (replace with your IP)
const API_BASE_URL = 'http://192.168.1.100:5000';

// For production
const API_BASE_URL = 'https://api.yourdomain.com';
```

### CORS Configuration

Ensure your Flask backend has CORS enabled:

```python
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## 📸 Camera Permissions

The app requires camera permissions for:
- Punch in/out photo capture

Make sure the following permissions are granted:
- **Android**: `CAMERA`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`
- **iOS**: `NSCameraUsageDescription`

These are automatically configured in `app.json`.

## 🔄 Data Flow

### Login Flow
```
1. User enters email and password
2. Credentials sent to /api/auth/login
3. Backend returns JWT token and user info
4. Token stored securely using expo-secure-store
5. User redirected to Dashboard
```

### Punch In Flow
```
1. User clicks "Punch In" button
2. Camera permission requested
3. Photo captured by camera
4. Photo + staff_id sent to /api/attendance/punch-in
5. Backend records punch in with photo
6. Current status updated
```

### Data Sync
- Dashboard and Attendance data are fetched on screen load
- Pull-to-refresh can be implemented for manual sync
- Offline support can be added with local storage

## 🐛 Troubleshooting

### API Connection Issues

**Problem**: "Cannot connect to backend"
**Solution**:
- Check backend is running: `python app.py`
- Verify API URL in `src/services/api.js`
- Check CORS configuration in Flask app
- Ensure device can reach backend (same network)

### Camera Not Working

**Problem**: "Camera permission denied"
**Solution**:
- Grant camera permission when prompted
- Check `app.json` for camera permissions
- Restart app after granting permission

### Token Expired

**Problem**: "401 Unauthorized" errors
**Solution**:
- User will be automatically logged out
- Re-login to get a new token
- Check token expiry in backend settings

### Image Upload Issues

**Problem**: "Failed to upload photo"
**Solution**:
- Check image size (should be < 5MB)
- Verify network connection
- Check backend `/uploads` directory permissions
- Check FormData is properly configured in api.js

## 📚 Development Tips

### Adding New Screens

1. Create screen in `src/screens/NewScreen.js`
2. Add navigation in `src/navigation/Navigation.js`
3. Import and register in Tab.Navigator

### Adding API Endpoints

1. Add function in `src/services/api.js`
2. Example:
   ```javascript
   export const newAPI = {
     getData: async (id) => {
       const response = await apiClient.get(`/api/endpoint/${id}`);
       return response.data;
     },
   };
   ```

### State Management

Currently uses:
- React Context (AuthContext) for authentication
- Local useState hooks for screen state
- Consider Redux/Zustand for complex state

## 📦 Dependencies

Key packages:
- `react-native` - Core framework
- `expo` - Development environment
- `axios` - HTTP client
- `@react-navigation/*` - Navigation
- `expo-secure-store` - Secure token storage
- `expo-camera` - Camera access
- `expo-image-picker` - Image picking

## 🚢 Deployment

### Android Play Store

1. Generate signing key
2. Build APK/AAB
3. Upload to Google Play Console
4. Configure release settings

### iOS App Store

1. Set up Apple Developer account
2. Create provisioning profiles
3. Build and sign IPA
4. Submit to App Store

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API endpoint documentation
3. Check backend logs for errors
4. Enable debug logging in api.js

## 📝 Notes

- The app uses Expo which simplifies development
- For production, consider EAS Build for easier deployment
- Implement proper error handling for production
- Add analytics and crash reporting
- Implement offline support for robust experience

## 🎯 Future Enhancements

- [ ] Offline attendance syncing
- [ ] Push notifications
- [ ] Leave request management
- [ ] Payslip viewing
- [ ] Biometric authentication
- [ ] QR code scanning for punch in
- [ ] Location tracking
- [ ] Document downloads
- [ ] In-app messaging
