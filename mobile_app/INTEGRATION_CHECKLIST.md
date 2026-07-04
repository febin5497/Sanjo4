# 🔍 Mobile App Integration Checklist

## Before Starting

- [ ] Backend is running (`python app.py`)
- [ ] Backend has CORS configured
- [ ] You have test user credentials
- [ ] Device/emulator is set up

## Step 1: Configuration (5 mins)

- [ ] Edit `src/services/api.js`
- [ ] Update `API_BASE_URL` with correct IP
- [ ] Save the file
- [ ] Verify backend URL is reachable from device

## Step 2: Install & Start (10 mins)

```bash
cd mobile_app
npm install  # (if not already done)
npm start
```

- [ ] Terminal shows "Expo DevTools is running..."
- [ ] QR code displayed in terminal
- [ ] No error messages

## Step 3: Run the App (5 mins)

Choose your platform:

### Android
```bash
npm run android
```
- [ ] App launches on emulator/device
- [ ] BuildERP login screen displays
- [ ] No errors in console

### iOS (Mac only)
```bash
npm run ios
```
- [ ] App launches on simulator
- [ ] Login screen visible

### Web (Browser)
```bash
npm run web
```
- [ ] App opens in browser
- [ ] Login page displays

## Step 4: Test Login

- [ ] Enter valid email
- [ ] Enter correct password
- [ ] Click "Login"
- [ ] Check backend logs for request
- [ ] App should navigate to Dashboard

**If login fails:**
- [ ] Check backend is running
- [ ] Verify user exists in database
- [ ] Check API_BASE_URL is correct
- [ ] Check CORS settings
- [ ] Review backend error logs

## Step 5: Test Dashboard Screen

After successful login:

- [ ] Dashboard displays
- [ ] See 4 stat cards (Present, Absent, Attendance %, Half Days)
- [ ] View assigned tasks
- [ ] Quick action buttons visible
- [ ] Date displays correctly

**If dashboard is blank:**
- [ ] Check API endpoint exists: `/api/tasks/assigned/{staffId}`
- [ ] Check attendance data in database
- [ ] Verify staff record exists

## Step 6: Test Attendance Screen

Click "Attendance" tab:

- [ ] Attendance screen loads
- [ ] Current status shows (Punched In/Out)
- [ ] "Punch In" button is enabled (if not punched in)
- [ ] "Punch Out" button is disabled (if not punched in)
- [ ] Can see attendance history

### Test Punch In

- [ ] Click "Punch In" button
- [ ] Camera permission popup appears
- [ ] Camera app opens
- [ ] Take a photo
- [ ] See success message
- [ ] Status changes to "PUNCHED IN"
- [ ] Punch in time appears

**If punch in fails:**
- [ ] Check backend `/api/attendance/punch-in` endpoint exists
- [ ] Verify uploads directory has write permissions
- [ ] Check photo_path column in attendance_records table

### Test Punch Out

- [ ] Click "Punch Out" button
- [ ] Take a photo
- [ ] See success message
- [ ] Status changes to "PUNCHED OUT"
- [ ] Punch out time appears

## Step 7: Test Profile Screen

Click "Profile" tab:

- [ ] Profile screen loads
- [ ] User name displays correctly
- [ ] User role displays
- [ ] Personal information section shows
- [ ] Email, phone, joining date visible
- [ ] Salary information visible
- [ ] Logout button at bottom

### Test Logout

- [ ] Click "Logout" button
- [ ] Confirmation dialog appears
- [ ] Click "Logout" again
- [ ] Returned to login screen
- [ ] App shows login screen correctly

## Step 8: Verify API Calls

### Using Browser Network Tools

1. Open Expo DevTools (press 'd' on web, shake on device)
2. Go to Network tab
3. Perform actions and verify requests:

**Login Request:**
- [ ] Method: POST
- [ ] Endpoint: `/api/auth/login`
- [ ] Status: 200 OK
- [ ] Response includes token

**Attendance Request:**
- [ ] Method: GET
- [ ] Endpoint: `/api/attendance/list/{staffId}`
- [ ] Status: 200 OK
- [ ] Response includes attendance records

**Stats Request:**
- [ ] Method: GET
- [ ] Endpoint: `/api/attendance/stats/{staffId}`
- [ ] Status: 200 OK
- [ ] Response includes statistics

## Step 9: Verify Database Changes

After punching in/out, check database:

```bash
# In backend directory
python
>>> import sqlite3
>>> conn = sqlite3.connect('construction_management/data.db')
>>> c = conn.cursor()
>>> c.execute('SELECT * FROM attendance_records ORDER BY id DESC LIMIT 5')
>>> for row in c.fetchall(): print(row)
```

- [ ] New punch_in record created
- [ ] punch_in_time recorded correctly
- [ ] Photo saved/reference stored
- [ ] punch_out record created (if punched out)

## Step 10: Test Error Scenarios

### Network Disconnected
- [ ] Disconnect WiFi/data
- [ ] Try to login
- [ ] Should show error: "Network error"
- [ ] Reconnect and try again
- [ ] Login succeeds

### Invalid Credentials
- [ ] Enter wrong password
- [ ] Click login
- [ ] Should show error: "Invalid credentials"
- [ ] Can retry

### Expired Token (Optional)
- [ ] Login successfully
- [ ] Navigate to attendance
- [ ] Manually delete token from secure store
- [ ] Try punch in
- [ ] Should redirect to login

## Step 11: Performance Testing

- [ ] App loads within 2-3 seconds
- [ ] Screens navigate smoothly
- [ ] Photo upload takes < 5 seconds
- [ ] No freezing or lag
- [ ] Memory usage reasonable

## Step 12: Cross-Device Testing

Test on multiple devices (if available):

- [ ] Android emulator
- [ ] Physical Android device
- [ ] iOS simulator (if on Mac)
- [ ] Web browser
- [ ] Different screen sizes

## Step 13: Documentation Verification

- [ ] README.md is clear
- [ ] QUICK_START.md works for new users
- [ ] API configuration is documented
- [ ] Screen descriptions are accurate
- [ ] All features are documented

## Integration Test Summary

### All Tests Passed? ✅

If all checks pass:
1. App is fully integrated with backend
2. All CRUD operations working
3. Error handling is robust
4. Ready for production build

### Some Tests Failed? ⚠️

Review the failed test section:
1. Check error message
2. Verify API endpoint exists
3. Check database has data
4. Review logs for details
5. Fix backend or app as needed

## Next Steps After Integration

1. **Customize:**
   - [ ] Update app colors and branding
   - [ ] Change app name and logo
   - [ ] Update app icon in assets/

2. **Enhance:**
   - [ ] Add offline support
   - [ ] Add push notifications
   - [ ] Add more screens

3. **Deploy:**
   - [ ] Create production build
   - [ ] Test on real devices
   - [ ] Deploy to app stores

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Cannot connect to backend | Check API_BASE_URL, verify backend is running |
| Camera not working | Grant camera permission, restart app |
| Login fails | Check credentials, verify user in database |
| Blank attendance history | Verify punch records exist in database |
| Token errors | Logout and login again |
| Slow performance | Check network, reduce data, restart app |

## Support Resources

- **QUICK_START.md** - Quick setup guide
- **MOBILE_APP_GUIDE.md** - Complete documentation
- **Backend logs** - Check for API errors
- **Browser console** - Check for app errors
- **Expo DevTools** - Network and performance debugging

---

## Final Checklist

- [ ] All 13 integration steps completed
- [ ] No critical errors
- [ ] All features working
- [ ] Documentation reviewed
- [ ] Ready for deployment
- [ ] User testing planned

**Status:** Ready for Production ✅

---

**Date:** March 20, 2026
**Version:** 1.0.0
**Framework:** React Native + Expo
