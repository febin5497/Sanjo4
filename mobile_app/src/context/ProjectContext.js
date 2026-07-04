import React, { createContext, useContext, useState, useEffect } from 'react';
import * as SecureStore from 'expo-secure-store';
import api, { API_BASE_URL } from '../services/api';
import { useAuth } from './AuthContext';

const ProjectContext = createContext();

export const ProjectProvider = ({ children }) => {
  const { state } = useAuth();
  const [assignedProjects, setAssignedProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [projectError, setProjectError] = useState(null);

  // Fetch assigned projects for the current user
  useEffect(() => {
    if (state.user?.id) {
      fetchAssignedProjects();
    }
  }, [state.user?.id]);

  // Update selected project when ID changes
  useEffect(() => {
    if (selectedProjectId && assignedProjects.length > 0) {
      const project = assignedProjects.find(p => p.id === selectedProjectId);
      setSelectedProject(project || null);
    }
  }, [selectedProjectId, assignedProjects]);

  const fetchAssignedProjects = async () => {
    try {
      setLoadingProjects(true);
      setProjectError(null);

      const staffId = state.user?.staff_id || state.user?.id;
      console.log('ProjectContext - Staff ID:', staffId);
      console.log('ProjectContext - User Data:', state.user);

      if (!staffId) {
        console.warn('No staff ID available');
        setAssignedProjects([]);
        setLoadingProjects(false);
        return;
      }

      console.log(`Fetching projects for staff ID: ${staffId}`);

      // Fetch projects assigned to this staff member
      const token = state.userToken || await SecureStore.getItemAsync('auth_token');
      const response = await api.get(`/api/staff/${staffId}/projects`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      console.log('Projects response:', response.data);

      const projects = response.data?.data || response.data?.projects || [];
      setAssignedProjects(Array.isArray(projects) ? projects : []);

      // Auto-select first project if available
      if (projects.length > 0 && !selectedProjectId) {
        setSelectedProjectId(projects[0].id);
      }
    } catch (error) {
      console.error('Error fetching assigned projects:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      setProjectError(error.message || 'Failed to load assigned projects');
      setAssignedProjects([]);
    } finally {
      setLoadingProjects(false);
    }
  };

  const selectProject = (projectId) => {
    const project = assignedProjects.find(p => p.id === projectId);
    if (project) {
      setSelectedProjectId(projectId);
      setSelectedProject(project);
      // Persist selected project
      SecureStore.setItemAsync('selectedProjectId', String(projectId));
    }
  };

  const value = {
    assignedProjects,
    selectedProjectId,
    selectedProject,
    loadingProjects,
    projectError,
    selectProject,
    fetchAssignedProjects,
    hasMultipleProjects: assignedProjects.length > 1,
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within ProjectProvider');
  }
  return context;
};
