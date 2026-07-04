import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../../api/api';
import { useToast } from '../../components/Toast';
import '../../styles/AttendancePhotoApprovals.css';
import { FaCheck, FaTimes, FaSpinner, FaCamera, FaCalendar, FaUser } from 'react-icons/fa';
export default function AttendancePhotoApprovals() {
  const location = useLocation();
  const { showSuccess, showError } = useToast();
  const [photos, setPhotos] = useState([]);
  const [allPhotos, setAllPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending');
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [stats, setStats] = useState({
    pending: 0,
    approved_today: 0,
    rejected_today: 0,
    total_processed: 0,
  });
  // Reset dropdown and filter state on page navigation
  useEffect(() => {
    setFilter('pending');
    setSelectedPhoto(null);
    setRejectionReason('');
  }, [location.pathname]);
  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      setFilter('pending');
      setSelectedPhoto(null);
      setRejectionReason('');
    };
  }, []);
  useEffect(() => {
    loadPendingPhotos();
  }, [filter]);
  const loadPendingPhotos = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/attendance/approvals/pending');
      // Handle paginated response from BaseResourceRouter
      // API can return: { data: [...] } or { pending: [...] } or [...]
      const photosData = response.data?.data || response.data?.pending || response.data || [];
      if (Array.isArray(photosData) && photosData.length > 0) {
        setPhotos(photosData);
        setAllPhotos(photosData);
        // Calculate statistics
        const today = new Date().toDateString();
        const pendingCount = photosData.filter((p) => p.approval_status === 'pending').length;
        const approvedToday = photosData.filter(
          (p) => p.approval_status === 'approved' && new Date(p.timestamp_submitted).toDateString() === today
        ).length;
        const rejectedToday = photosData.filter(
          (p) => p.approval_status === 'rejected' && new Date(p.timestamp_submitted).toDateString() === today
        ).length;
        const totalProcessed = approvedToday + rejectedToday;
        setStats({
          pending: pendingCount,
          approved_today: approvedToday,
          rejected_today: rejectedToday,
          total_processed: totalProcessed,
        });
      } else if (Array.isArray(photosData)) {
        setPhotos([]);
        setAllPhotos([]);
        setStats({
          pending: 0,
          approved_today: 0,
          rejected_today: 0,
          total_processed: 0,
        });
      } else {
        showError('Failed to load photos: unexpected response format');
      }
    } catch (error) {
      showError('Failed to load pending photos: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };
  const approvePhoto = async (photoId) => {
    try {
      const response = await api.post(`/api/attendance/approvals/${photoId}/approve`, {});
      if (response.data.success) {
        showSuccess('Photo approved successfully');
        loadPendingPhotos();
        setSelectedPhoto(null);
      }
    } catch (error) {
      showError('Failed to approve photo');
    }
  };
  const rejectPhoto = async (photoId) => {
    if (!rejectionReason.trim()) {
      showError('Please provide a rejection reason');
      return;
    }
    try {
      const response = await api.post(`/api/attendance/approvals/${photoId}/reject`, {
        rejection_reason: rejectionReason,
      });
      if (response.data.success) {
        showSuccess('Photo rejected successfully');
        loadPendingPhotos();
        setSelectedPhoto(null);
        setRejectionReason('');
      }
    } catch (error) {
      showError('Failed to reject photo');
    }
  };
  const getPhotoUrl = (photoId) => {
    const base = api.defaults.baseURL?.replace(/\/+$/, '') || '';
    const token = localStorage.getItem('token') || '';
    return `${base}/api/attendance/photos/${photoId}?token=${encodeURIComponent(token)}`;
  };
  if (loading) {
    return (
      <div className="approval-container">
        <div className="loading">
          <FaSpinner className="spinner" />
          <p>Loading pending photos...</p>
        </div>
      </div>
    );
  }
  return (
    <div className="approval-container">
      {/* Dashboard Section */}
      <div className="approval-dashboard">
        <div className="dashboard-grid">
          {/* Pending Approvals Card */}
          <div className="dashboard-card pending-card">
            <div className="card-icon">⏳</div>
            <div className="card-content">
              <div className="card-number">{stats.pending}</div>
              <div className="card-label">Pending Approvals</div>
              <div className="card-description">Waiting for review</div>
            </div>
          </div>
          {/* Approved Today Card */}
          <div className="dashboard-card approved-card">
            <div className="card-icon">✅</div>
            <div className="card-content">
              <div className="card-number">{stats.approved_today}</div>
              <div className="card-label">Approved Today</div>
              <div className="card-description">Successful approvals</div>
            </div>
          </div>
          {/* Rejected Today Card */}
          <div className="dashboard-card rejected-card">
            <div className="card-icon">❌</div>
            <div className="card-content">
              <div className="card-number">{stats.rejected_today}</div>
              <div className="card-label">Rejected Today</div>
              <div className="card-description">Need resubmission</div>
            </div>
          </div>
          {/* Total Processed Card */}
          <div className="dashboard-card processed-card">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <div className="card-number">{stats.total_processed}</div>
              <div className="card-label">Total Processed</div>
              <div className="card-description">Approved + Rejected</div>
            </div>
          </div>
        </div>
      </div>
      {photos.length === 0 ? (
        <div className="no-photos">
          <FaCamera size={48} />
          <p>No pending photos for approval</p>
        </div>
      ) : (
        <div className="photos-grid">
          {photos.map((photo) => (
            <div
              key={photo.id}
              className="photo-card"
              onClick={() => setSelectedPhoto(photo)}
            >
              <div className="photo-image">
                <img
                  src={getPhotoUrl(photo.id)}
                  alt="Attendance Photo"
                  onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/200?text=Photo';
                  }}
                />
                <div className="photo-badge">Pending</div>
              </div>
              <div className="photo-info">
                <p className="staff-name">
                  <FaUser size={14} /> {photo.staff_name || 'Unknown'}
                </p>
                <p className="timestamp">
                  <FaCalendar size={14} /> {new Date(photo.timestamp_captured).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
      {selectedPhoto && (
        <div className="modal-overlay" onClick={() => setSelectedPhoto(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedPhoto(null)}>
              ×
            </button>
            <div className="modal-header">
              <h2>Review Photo</h2>
              <p className="staff-info">
                {selectedPhoto.staff_name} • {new Date(selectedPhoto.timestamp_captured).toLocaleString()}
              </p>
            </div>
            <div className="modal-body">
              <div className="photo-display">
                <img
                  src={getPhotoUrl(selectedPhoto.id)}
                  alt="Attendance Photo"
                  onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/400?text=Photo';
                  }}
                />
              </div>
              <div className="details-sections">
                <div className="details-grid">
                  <div className="details-group">
                    <div className="details-group-title">🕐 Timestamp</div>
                    <div className="detail-row">
                      <span className="detail-label">Captured:</span>
                      <span>{new Date(selectedPhoto.timestamp_captured).toLocaleString()}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Submitted:</span>
                      <span>{new Date(selectedPhoto.timestamp_submitted).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="details-group">
                    <div className="details-group-title">👤 Staff Information</div>
                    <div className="detail-row">
                      <span className="detail-label">Staff ID:</span>
                      <span>{selectedPhoto.staff_id}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Name:</span>
                      <span>{selectedPhoto.staff_name}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Role:</span>
                      <span>{selectedPhoto.staff_role}</span>
                    </div>
                  </div>
                  <div className="details-group">
                    <div className="details-group-title">📍 Location</div>
                    {(selectedPhoto.latitude || selectedPhoto.longitude) ? (
                      <>
                        <div className="detail-row">
                          <span className="detail-label">Latitude:</span>
                          <span className="location-value">{selectedPhoto.latitude?.toFixed(6)}</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Longitude:</span>
                          <span className="location-value">{selectedPhoto.longitude?.toFixed(6)}</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Accuracy:</span>
                          <span className="location-value">{selectedPhoto.location_accuracy?.toFixed(2)}m</span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-label">Map:</span>
                          <span className="location-link">
                            <a
                              href={`https://maps.google.com/?q=${selectedPhoto.latitude},${selectedPhoto.longitude}`}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              View on Map 🗺️
                            </a>
                          </span>
                        </div>
                      </>
                    ) : (
                      <div className="detail-row">
                        <span className="detail-label">Location:</span>
                        <span className="text-muted">Not available</span>
                      </div>
                    )}
                  </div>
                  <div className="details-group">
                    <div className="details-group-title">⏳ Status Information</div>
                    <div className="detail-row">
                      <span className="detail-label">Approval Status:</span>
                      <span>
                        <span className={`status-badge ${selectedPhoto.approval_status === 'pending' ? 'pending' : selectedPhoto.approval_status === 'approved' ? 'approved' : 'rejected'}`}>{selectedPhoto.approval_status}</span>
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Approved By:</span>
                      <span>{selectedPhoto.approved_by ? `Staff ${selectedPhoto.approved_by}` : 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Approved At:</span>
                      <span>{selectedPhoto.approved_at ? new Date(selectedPhoto.approved_at).toLocaleString() : 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Rejected By:</span>
                      <span>{selectedPhoto.rejected_by ? `Staff ${selectedPhoto.rejected_by}` : 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Rejected At:</span>
                      <span>{selectedPhoto.rejected_at ? new Date(selectedPhoto.rejected_at).toLocaleString() : 'N/A'}</span>
                    </div>
                  </div>
                </div>
                <div className="rejection-section">
                  <div className="rejection-section-header">
                    <h4>📝 Rejection Details</h4>
                  </div>
                  <div className="rejection-form">
                    <label className="form-label">Rejection Reason *</label>
                    <textarea
                      className="form-textarea"
                      value={rejectionReason}
                      onChange={(e) => setRejectionReason(e.target.value)}
                      placeholder="Please provide a detailed reason for rejecting this attendance photo. Explain what was not acceptable and suggest how to correct it..."
                      rows={4}
                      required
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-reject"
                onClick={() => rejectPhoto(selectedPhoto.id)}
                disabled={loading}
              >
                <FaTimes /> Reject
              </button>
              <button
                className="btn btn-approve"
                onClick={() => approvePhoto(selectedPhoto.id)}
                disabled={loading}
              >
                <FaCheck /> Approve
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
