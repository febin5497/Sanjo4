# Mobile App Role-Based Access Control Implementation

## Overview
Implement role-based filtering to show only assigned projects/vehicles to users.

## Components Created

### 1. **ProjectContext** (`src/context/ProjectContext.js`)
- Manages assigned projects for site engineers
- Provides project selector functionality
- Fetches projects from `/api/staff/{staffId}/projects`
- Stores selected project in context

**Usage:**
```javascript
const { assignedProjects, selectedProject, selectProject } = useProject();
```

### 2. **VehicleContext** (`src/context/VehicleContext.js`)
- Manages assigned vehicles for drivers
- Fetches vehicles from `/api/staff/{staffId}/vehicles`
- Only loads for drivers

**Usage:**
```javascript
const { assignedVehicles, loadingVehicles } = useVehicles();
```

### 3. **ProjectSelector** (`src/components/ProjectSelector.js`)
- Dropdown component for site engineers with multiple projects
- Auto-hides if only one project assigned
- Modal-based selector with project details

**Usage:**
```javascript
import { ProjectSelector } from '../components/ProjectSelector';

<ProjectSelector />
```

## Integration Steps

### Step 1: Update App.js (Root Provider Wrapping)
```javascript
import { ProjectProvider } from './context/ProjectContext';
import { VehicleProvider } from './context/VehicleContext';

export default function App() {
  return (
    <AuthProvider>
      <ProjectProvider>
        <VehicleProvider>
          <RootNavigator />
        </VehicleProvider>
      </ProjectProvider>
    </AuthProvider>
  );
}
```

### Step 2: Update ExpensesScreen (Site Engineers)
```javascript
import { useProject } from '../context/ProjectContext';
import { ProjectSelector } from '../components/ProjectSelector';

export const ExpensesScreen = () => {
  const { selectedProject } = useProject();

  useEffect(() => {
    if (selectedProject?.id) {
      // Load expenses for selected project only
      fetchExpenses(selectedProject.id);
    }
  }, [selectedProject?.id]);

  return (
    <View>
      <ProjectSelector />
      {/* Show expenses for selectedProject */}
    </View>
  );
};
```

### Step 3: Update VehiclesScreen (Drivers)
```javascript
import { useVehicles } from '../context/VehicleContext';

export const VehiclesScreen = () => {
  const { assignedVehicles, loadingVehicles } = useVehicles();

  return (
    <View>
      {loadingVehicles ? (
        <ActivityIndicator />
      ) : (
        // Show only assigned vehicles
        <FlatList data={assignedVehicles} ... />
      )}
    </View>
  );
};
```

### Step 4: Update ProjectsScreen (All Roles)
```javascript
import { useProject } from '../context/ProjectContext';

export const ProjectsScreen = () => {
  const { assignedProjects, loadingProjects } = useProject();

  // Show only assigned projects (filtered by staff role)
  return (
    <View>
      <FlatList data={assignedProjects} ... />
    </View>
  );
};
```

## Backend API Requirements

### Endpoint 1: Get Assigned Projects
```
GET /api/staff/{staffId}/projects
Response: {
  "data": [
    {
      "id": 1,
      "name": "Construction Site A",
      "status": "active",
      "location": "...",
      ...
    }
  ]
}
```

### Endpoint 2: Get Assigned Vehicles
```
GET /api/staff/{staffId}/vehicles
Response: {
  "data": [
    {
      "id": 1,
      "plate_number": "ABC-123",
      "model": "...",
      "status": "active",
      ...
    }
  ]
}
```

## User Experience Flow

### Site Engineer with Multiple Projects
1. Open App → Sees Expenses tab
2. Opens Expenses → ProjectSelector dropdown appears
3. Selects Project A → Expenses filtered to Project A
4. Can switch projects anytime via dropdown
5. Selection persists (saved in SecureStore)

### Site Engineer with Single Project
1. Open App → Sees Expenses tab
2. Opens Expenses → No ProjectSelector (auto-hidden)
3. Expenses shown for their only project

### Driver
1. Open App → Sees Vehicles tab
2. Opens Vehicles → Only assigned vehicles displayed
3. Can view vehicle details
4. No projects visible (not a manager)

### Default Staff (Non-Driver, Non-Engineer)
1. Open App → Sees Dashboard, Attendance, Profile
2. Dashboard shows their assigned projects (if any)
3. No project selector needed

## Features Implemented

✅ Role-based project filtering
✅ Role-based vehicle filtering
✅ Project selector with modal UI
✅ Automatic project selection (first project)
✅ Project selection persistence
✅ Error handling for missing data
✅ Loading states
✅ Context-based state management

## Testing Checklist

- [ ] Login as Driver → Only Vehicles visible
- [ ] Login as Site Engineer (1 project) → No ProjectSelector
- [ ] Login as Site Engineer (2+ projects) → ProjectSelector visible
- [ ] Select different project → Data updates
- [ ] Reload app → Selected project persists
- [ ] Login as Manager → All projects visible
- [ ] Login as HR → No projects/vehicles visible

## Notes

- Dropdown only shows if `hasMultipleProjects` is true
- Projects are fetched when user logs in
- Vehicles only fetched for drivers
- All contexts use lazy loading with error handling
- Selection persists in SecureStore for offline support
