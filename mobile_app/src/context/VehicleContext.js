import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from './AuthContext';

const VehicleContext = createContext();

export const VehicleProvider = ({ children }) => {
  const { state } = useAuth();
  const [assignedVehicles, setAssignedVehicles] = useState([]);
  const [loadingVehicles, setLoadingVehicles] = useState(true);
  const [vehicleError, setVehicleError] = useState(null);

  // Fetch assigned vehicles for the current driver
  useEffect(() => {
    if (state.user?.id && state.user?.role?.toLowerCase() === 'driver') {
      fetchAssignedVehicles();
    }
  }, [state.user?.id, state.user?.role]);

  const fetchAssignedVehicles = async () => {
    try {
      setLoadingVehicles(true);
      setVehicleError(null);

      const staffId = state.user?.id;
      if (!staffId) {
        console.warn('No staff ID available');
        setAssignedVehicles([]);
        return;
      }

      // Fetch vehicles assigned to this driver
      const response = await api.get(`/api/staff/${staffId}/vehicles`);

      const vehicles = response.data?.data || response.data?.vehicles || [];
      setAssignedVehicles(Array.isArray(vehicles) ? vehicles : []);
    } catch (error) {
      console.error('Error fetching assigned vehicles:', error);
      setVehicleError(error.message || 'Failed to load assigned vehicles');
      setAssignedVehicles([]);
    } finally {
      setLoadingVehicles(false);
    }
  };

  const value = {
    assignedVehicles,
    loadingVehicles,
    vehicleError,
    fetchAssignedVehicles,
  };

  return (
    <VehicleContext.Provider value={value}>
      {children}
    </VehicleContext.Provider>
  );
};

export const useVehicles = () => {
  const context = useContext(VehicleContext);
  if (!context) {
    throw new Error('useVehicles must be used within VehicleProvider');
  }
  return context;
};
