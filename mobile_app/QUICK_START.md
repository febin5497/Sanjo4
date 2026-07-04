# React Native Mobile App - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Configure Backend URL

Edit: `src/services/api.js` (line 4)

```javascript
// Change this line to your backend IP address
const API_BASE_URL = 'http://192.168.1.100:5000';
```

**Finding your IP:**
- Windows: Open Command Prompt and run `ipconfig` (look for IPv4 Address)
- Linux/Mac: Open Terminal and run `ifconfig`

### Step 2: Start Development Server

```bash
# In mobile_app directory
cd "C:\Users\roms0\OneDrive\Documents\construction_management_app\construction_management_app\mobile_app"

# Install dependencies (if not already done)
npm install

# Start the app
npm start
```

### Step 3: Run on Device/Emulator

**Android Emulator:**
```bash
npm run android
```

**Physical Android Device:**
1. Install Expo Go app from Google Play Store
2. Scan QR code from terminal

**iOS Simulator:**
```bash
npm run ios
```

**Web Browser (for testing):**
```bash
npm run web
```

---

## 📱 Test Credentials

Use the admin user credentials to test:

```
Email: admin@builderp.com
Password: admin123
```

Or any staff credentials created in your backend:
```
Email: staff1@builderp.com
Password: staff123
```

---

## ✅ Features to Test

### 1. **Login**
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials (should show error)
- [ ] Token should be stored securely

### 2. **Dashboard**
- [ ] View attendance statistics
- [ ] See assigned tasks
- [ ] Check quick stats (Present, Absent, Attendance %)

### 3. **Attendance**
- [ ] Punch In with photo capture
- [ ] Punch Out with photo capture
- [ ] View attendance history (last 30 days)
- [ ] View statistics

### 4. **Profile**
- [ ] View personal information
- [ ] View salary information
- [ ] Logout functionality

---

## 🔧 Common Issues & Fixes

### Cannot Connect to Backend

**Error:** `Cannot reach server`

**Fix:**
1. Check backend is running:
   ```bash
   python app.py  # in backend directory
   ```

2. Verify IP address is correct:
   - Run `ipconfig` to get your machine IP
   - Update API_BASE_URL in `src/services/api.js`

3. Check if on same network:
   - Phone/emulator must be on same WiFi as development machine
   - Or use `localhost` if running on same machine

### Camera Permission Denied

**Error:** `Camera access denied`

**Fix:**
- Tap "Allow" when camera permission is requested
- Or go to app settings and grant camera permission manually
- Restart the app

### Token Expiration

**Error:** `401 Unauthorized`

**Fix:**
- Log out and log back in
- You'll get a new token automatically

---

## 📁 Project Structure

```
mobile_app/
├── src/
│   ├── screens/          # App screens
│   │   ├── LoginScreen.js         ← Login page
│   │   ├── DashboardScreen.js    ← Dashboard with stats
│   │   ├── AttendanceScreen.js   ← Punch in/out
│   │   └── ProfileScreen.js      ← User profile
│   ├── services/         # API calls
│   │   └── api.js        ← Configure backend URL here
│   ├── context/          # App state
│   │   └── AuthContext.js
│   └── navigation/       # App navigation
│       └── Navigation.js
├── App.js                # Main app entry point
├── app.json              # Expo configuration
├── package.json          # Dependencies
└── MOBILE_APP_GUIDE.md  # Full documentation
```

---

## 🚀 Next Steps

### After Testing:

1. **Build for Production:**
   ```bash
   eas build --platform android
   eas build --platform ios
   ```

2. **Customize Branding:**
   - Update app icons in `assets/`
   - Update app name in `app.json`
   - Update colors in screen files

3. **Add Features:**
   - Offline support (SQLite)
   - Push notifications
   - QR code scanning
   - Location tracking

4. **Deploy:**
   - Google Play Store (Android)
   - Apple App Store (iOS)

---

## 💡 Tips

### Development Mode
- Hot reload works automatically
- Shake device to open menu
- Use browser DevTools for web version

### Network Debugging
Use Expo DevTools to inspect network requests:
```bash
# In Expo menu (press 'd' on web or shake on device)
→ Network tab
→ View all API requests and responses
```

### File Structure Notes
- Screens should handle their own data fetching
- API calls go through `src/services/api.js`
- All styles are inline (can be moved to CSS later)
- Authentication managed by `AuthContext.js`

---

## ❓ FAQ

**Q: Can I test without a phone?**
A: Yes! Use Android Emulator or iOS Simulator, or `npm run web`

**Q: Where are tokens stored?**
A: Securely in device storage using `expo-secure-store`

**Q: How do I change API endpoint?**
A: Edit `src/services/api.js` line 4

**Q: What happens when token expires?**
A: User is automatically logged out and sent to login screen

**Q: Can I add more screens?**
A: Yes! Copy a screen file, add to Navigation.js

---

## 📞 Getting Help

1. Check backend logs:
   ```bash
   # In backend directory
   python app.py
   ```

2. Check Expo console for errors (terminal)

3. Enable debug logging in `src/services/api.js`:
   ```javascript
   console.log('API Response:', response);
   ```

4. Check this guide's MOBILE_APP_GUIDE.md for full documentation

---

## ✨ You're All Set!

Your mobile app is ready to develop! 🎉

**Start the app:** `npm start`
**Run on Android:** `npm run android`

Happy coding! 🚀
