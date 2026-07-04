import React, { useRef, useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet, Alert } from 'react-native';
import { CameraView } from 'expo-camera';
import { MaterialIcons } from '@expo/vector-icons';

export const CameraModal = ({ onCapture, onCancel }) => {
  const cameraRef = useRef(null);
  const [isReady, setIsReady] = useState(false);

  const takePicture = async () => {
    if (cameraRef.current && isReady) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          skipProcessing: false,
        });
        onCapture(photo.uri);
      } catch (error) {
        console.log('Camera capture error:', error);
        Alert.alert('Error', 'Failed to capture photo');
      }
    }
  };

  return (
    <View style={styles.container}>
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing="front" // FORCE FRONT CAMERA ONLY
        onCameraReady={() => setIsReady(true)}
      >
        <View style={styles.controls}>
          {/* Cancel Button */}
          <TouchableOpacity
            style={styles.cancelButton}
            onPress={onCancel}
          >
            <MaterialIcons name="close" size={24} color="#fff" />
          </TouchableOpacity>

          {/* Capture Button */}
          <TouchableOpacity
            style={[styles.captureButton, !isReady && styles.disabledButton]}
            onPress={takePicture}
            disabled={!isReady}
          >
            <View style={styles.captureButtonInner} />
          </TouchableOpacity>

          {/* Info Text */}
          <View style={styles.infoBox} />
        </View>
      </CameraView>

      <View style={styles.instructions}>
        <Text style={styles.instructionText}>Front Camera - Selfie Mode</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  controls: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  cancelButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(255, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  disabledButton: {
    opacity: 0.5,
  },
  captureButtonInner: {
    width: 55,
    height: 55,
    borderRadius: 27.5,
    backgroundColor: '#0052CC',
  },
  infoBox: {
    width: 50,
  },
  instructions: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  instructionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
});
