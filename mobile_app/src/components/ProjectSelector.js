import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import { useProject } from '../context/ProjectContext';
import { useTheme } from '../context/ThemeContext';

export const ProjectSelector = () => {
  const { colors } = useTheme();
  const {
    assignedProjects,
    selectedProject,
    selectProject,
    loadingProjects,
    hasMultipleProjects,
  } = useProject();

  const [modalVisible, setModalVisible] = React.useState(false);

  // Show selector for all site engineers (even with single project)
  if (assignedProjects.length === 0) {
    return null; // Don't show if no projects
  }

  if (loadingProjects) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="small" color="#0052CC" />
      </View>
    );
  }

  const handleSelectProject = (projectId) => {
    selectProject(projectId);
    setModalVisible(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Project</Text>
      <TouchableOpacity
        style={styles.selector}
        onPress={() => setModalVisible(true)}
      >
        <Text style={styles.selectedText}>
          {selectedProject?.name || 'Select Project'}
        </Text>
        <Text style={styles.arrow}>▼</Text>
      </TouchableOpacity>

      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Select Project</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            <FlatList
              data={assignedProjects}
              keyExtractor={(item) => item.id.toString()}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.projectItem,
                    selectedProject?.id === item.id && styles.projectItemActive,
                  ]}
                  onPress={() => handleSelectProject(item.id)}
                >
                  <View style={styles.projectInfo}>
                    <Text
                      style={[
                        styles.projectName,
                        selectedProject?.id === item.id && styles.projectNameActive,
                      ]}
                    >
                      {item.name}
                    </Text>
                    <Text style={styles.projectStatus}>{item.status}</Text>
                  </View>
                  {selectedProject?.id === item.id && (
                    <Text style={styles.checkmark}>✓</Text>
                  )}
                </TouchableOpacity>
              )}
            />
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
    paddingHorizontal: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  selector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
  },
  selectedText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    flex: 1,
  },
  arrow: {
    fontSize: 12,
    color: '#0052CC',
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
  },
  closeButton: {
    fontSize: 24,
    color: '#999',
    fontWeight: '300',
  },
  projectItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  projectItemActive: {
    backgroundColor: '#f0f7ff',
  },
  projectInfo: {
    flex: 1,
  },
  projectName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  projectNameActive: {
    color: '#0052CC',
  },
  projectStatus: {
    fontSize: 12,
    color: '#999',
    textTransform: 'capitalize',
  },
  checkmark: {
    fontSize: 18,
    color: '#4CAF50',
    fontWeight: 'bold',
  },
});
