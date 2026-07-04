import { useEffect, useState } from "react"
import api from "../../api/api"
import { useToast } from "../../components/Toast"
import { FaImage, FaUpload, FaSearch, FaFilter, FaTrash, FaCalendar, FaDownload, FaCheck } from "react-icons/fa"
export default function SitePhotos() {
  const { showSuccess, showError, showWarning } = useToast()
  const [photos, setPhotos] = useState([])
  const [file, setFile] = useState(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [sortBy, setSortBy] = useState("date")
  const [successMessage, setSuccessMessage] = useState("")
  const [uploading, setUploading] = useState(false)
  useEffect(() => {
    loadPhotos()
  }, [])
  const loadPhotos = async () => {
    try {
      const res = await api.get("/site-photos")
      setPhotos(res.data || [])
    } catch (error) {
    }
  }
  const uploadPhoto = async () => {
    if (!file) {
      showWarning("Please select a file first")
      return
    }
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append("file", file)
      await api.post("/site-photo", formData)
      setSuccessMessage("✓ Photo uploaded successfully!")
      setTimeout(() => setSuccessMessage(""), 3000)
      showSuccess("Photo uploaded successfully!")
      setFile(null)
      loadPhotos()
    } catch (error) {
      showError("Error uploading photo")
    } finally {
      setUploading(false)
    }
  }
  const handleDelete = async (photoId) => {
    if (confirm("Are you sure you want to delete this photo?")) {
      try {
        await api.delete(`/site-photos/${photoId}`)
        loadPhotos()
        showSuccess("Photo deleted successfully!")
      } catch (error) {
        showError("Error deleting photo")
      }
    }
  }
  // Filter and sort photos
  const filteredPhotos = photos.filter(p =>
    (p.name && p.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (p.description && p.description.toLowerCase().includes(searchTerm.toLowerCase()))
  ).sort((a, b) => {
    if (sortBy === "date") {
      return new Date(b.created_at || 0) - new Date(a.created_at || 0)
    }
    return (a.name || "").localeCompare(b.name || "")
  })
  const totalPhotos = photos.length
  const todayPhotos = photos.filter(p => {
    const photoDate = new Date(p.created_at).toDateString()
    return photoDate === new Date().toDateString()
  }).length
  return (
    <div className="p-6 theme-blue-white" style={{ background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)', minHeight: '100vh' }}>
      {/* Header with Action Button */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold flex items-center gap-3" style={{ color: '#0052CC' }}>
            <FaImage /> Site Progress Photos
          </h1>
          <p className="text-gray-600 mt-2">Document construction progress with photos and media</p>
        </div>
      </div>
      {/* Success Message */}
      {successMessage && (
        <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-800 rounded-lg flex items-center gap-2">
          <FaCheck /> {successMessage}
        </div>
      )}
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 transform hover:shadow-xl transition-shadow" style={{ borderLeftColor: '#0052CC' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-semibold uppercase">Total Photos</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{totalPhotos}</p>
            </div>
            <div className="text-5xl opacity-30" style={{ color: '#0052CC' }}>
              <FaImage />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 transform hover:shadow-xl transition-shadow" style={{ borderLeftColor: '#0052CC' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-semibold uppercase">Today's Photos</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{todayPhotos}</p>
            </div>
            <div className="text-5xl opacity-30" style={{ color: '#0052CC' }}>
              📸
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 transform hover:shadow-xl transition-shadow" style={{ borderLeftColor: '#0052CC' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-semibold uppercase">Storage Used</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{filteredPhotos.length} files</p>
            </div>
            <div className="text-5xl opacity-30" style={{ color: '#0052CC' }}>
              💾
            </div>
          </div>
        </div>
      </div>
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-bold mb-4" style={{ color: '#0052CC' }}>
          Upload New Photo
        </h2>
        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Select Photo</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 transition-all"
              style={{ focusBorderColor: '#0052CC', focusRingColor: '#e8f0fe' }}
            />
            {file && (
              <p className="text-sm text-gray-600 mt-2">Selected: {file.name}</p>
            )}
          </div>
          <button
            onClick={uploadPhoto}
            disabled={!file || uploading}
            className="flex items-center gap-2 px-6 py-2 text-white rounded-lg font-semibold hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: '#0052CC' }}
          >
            <FaUpload /> {uploading ? 'Uploading...' : 'Upload Photo'}
          </button>
        </div>
      </div>
      {/* Search and Filter Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4 items-end">
          {/* Search Bar */}
          <div className="flex-1">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Search Photos</label>
            <div className="relative">
              <FaSearch className="absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 transition-all"
                style={{ focusBorderColor: '#0052CC', focusRingColor: '#e8f0fe' }}
              />
            </div>
          </div>
          {/* Sort By */}
          <div className="w-full md:w-48">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <FaCalendar className="inline mr-2" /> Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 transition-all bg-white"
              style={{ focusBorderColor: '#0052CC', focusRingColor: '#e8f0fe' }}
            >
              <option value="date">Latest First</option>
              <option value="name">Name (A-Z)</option>
            </select>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-3">Showing {filteredPhotos.length} of {photos.length} photos</p>
      </div>
      {/* Photos Gallery */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4" style={{ color: '#0052CC' }}>
          Photo Gallery ({filteredPhotos.length})
        </h2>
        {filteredPhotos.length === 0 ? (
          <div className="text-center py-12">
            <FaImage className="text-5xl text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No photos found</p>
            <p className="text-gray-400 text-sm">Upload photos to start documenting your project</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPhotos.map(photo => (
              <div key={photo.id} className="rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow">
                {/* Photo Preview */}
                <div className="relative bg-gray-100 h-48 flex items-center justify-center">
                  {photo.file ? (
                    <img
                      src={`http://localhost:5000/uploads/${photo.file}`}
                      alt={photo.name || 'Site photo'}
                      className="w-full h-full object-cover"
                      onError={() => {
                      }}
                    />
                  ) : (
                    <FaImage className="text-4xl text-gray-300" />
                  )}
                </div>
                {/* Photo Details */}
                <div className="p-4">
                  <p className="font-semibold text-gray-900 truncate">{photo.name || 'Untitled'}</p>
                  {photo.description && (
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">{photo.description}</p>
                  )}
                  {photo.created_at && (
                    <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                      <FaCalendar style={{ color: '#0052CC' }} />
                      {new Date(photo.created_at).toLocaleDateString('en-IN')}
                    </p>
                  )}
                  {/* Actions */}
                  <div className="mt-3 flex gap-2">
                    {photo.file && (
                      <a
                        href={`http://localhost:5000/uploads/${photo.file}`}
                        download
                        className="flex-1 inline-flex items-center justify-center gap-1 px-3 py-2 bg-green-100 text-green-800 rounded-lg hover:bg-green-200 transition-colors font-semibold text-sm"
                      >
                        <FaDownload /> Download
                      </a>
                    )}
                    <button
                      onClick={() => handleDelete(photo.id)}
                      className="flex-1 inline-flex items-center justify-center gap-1 px-3 py-2 bg-red-100 text-red-800 rounded-lg hover:bg-red-200 transition-colors font-semibold text-sm"
                    >
                      <FaTrash /> Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      {/* Helpful Tips */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>💡 Tips:</strong> Upload high-quality photos to document construction progress. Use consistent naming conventions for easy identification. Photos are dated automatically.
        </p>
      </div>
    </div>
  )
}