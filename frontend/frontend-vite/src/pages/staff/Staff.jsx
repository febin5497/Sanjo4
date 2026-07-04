import { useEffect, useState } from "react"
import api from "../../api/api"
import { useToast } from "../../components/Toast"
import { Trash2, Edit2, Plus, Eye, Search, Filter } from "lucide-react"
export default function Staff() {
    const { showSuccess, showError } = useToast()
    // State Management
    const [staff, setStaff] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [selectedStaff, setSelectedStaff] = useState(null)
    const [showModal, setShowModal] = useState(false)
    const [showDetailModal, setShowDetailModal] = useState(false)
    const [isEditing, setIsEditing] = useState(false)
    const [confirmDelete, setConfirmDelete] = useState(null)
    // Pagination & Filtering
    const [currentPage, setCurrentPage] = useState(1)
    const [perPage, setPerPage] = useState(10)
    const [totalPages, setTotalPages] = useState(1)
    const [totalStaff, setTotalStaff] = useState(0)
    const [searchQuery, setSearchQuery] = useState("")
    const [roleFilter, setRoleFilter] = useState("")
    const [availableRoles, setAvailableRoles] = useState([])
    // Projects for assignment
    const [projects, setProjects] = useState([])
    // Form State
    const [formData, setFormData] = useState({
        name: "",
        role: "",
        phone: "",
        email: "",
        joining_date: "",
        salary: "",
        pf: "",
        esi: "",
        photo: "",
        needs_user_access: false,
        username: "",
        project_ids: []
    })
    const [formErrors, setFormErrors] = useState([])
    // Load staff data and projects - reset page when loading
    useEffect(() => {
        setCurrentPage(1)
        loadStaff()
        loadProjects()
    }, [])
    // Load staff data - pagination and filters
    useEffect(() => {
        loadStaff()
    }, [currentPage, perPage, searchQuery, roleFilter])
    // Predefined roles list
    const PREDEFINED_ROLES = [
        "Site Engineer",
        "Site Supervisor",
        "Foreman",
        "Laborer",
        "Electrician",
        "Plumber",
        "Mason",
        "Carpenter",
        "Driver",
        "Equipment Operator",
        "Project Manager",
        "Accountant",
        "Admin"
    ]
    // Extract unique roles for filter dropdown
    useEffect(() => {
        const roles = [...new Set(staff.map(s => s.role))]
        setAvailableRoles(roles.sort())
    }, [staff])
    const loadStaff = async () => {
        setLoading(true)
        setError(null)
        try {
            const params = new URLSearchParams({
                page: currentPage,
                per_page: perPage,
                ...(searchQuery && { search: searchQuery }),
                ...(roleFilter && { role: roleFilter })
            })
            const res = await api.get(`/api/staff?${params}`)
            if (res.data.success) {
                setStaff(res.data.data || [])
                setCurrentPage(res.data.pagination?.page || 1)
                setTotalPages(res.data.pagination?.pages || 1)
                setTotalStaff(res.data.pagination?.total || 0)
            } else {
                setError(res.data.error || "Failed to load staff")
            }
        } catch (err) {
            setError(err.response?.data?.error || "Error loading staff")
            setStaff([])
        } finally {
            setLoading(false)
        }
    }
    const loadProjects = async () => {
        try {
            const res = await api.get("/api/projects")
            const projectsData = Array.isArray(res.data?.data)
                ? res.data.data
                : Array.isArray(res.data)
                ? res.data
                : []
            setProjects(projectsData)
        } catch (err) {
            setProjects([])
        }
    }
    const handleAddClick = () => {
        setIsEditing(false)
        setSelectedStaff(null)
        setFormData({
            name: "",
            role: "",
            phone: "",
            email: "",
            joining_date: "",
            salary: "",
            pf: "",
            esi: "",
            photo: "",
            needs_user_access: false,
            username: "",
            project_ids: []
        })
        setFormErrors([])
        setShowModal(true)
    }
    const handleEditClick = (staffMember) => {
        setIsEditing(true)
        setSelectedStaff(staffMember)
        setFormData({
            name: staffMember.name || `${staffMember.first_name} ${staffMember.last_name}`,
            role: staffMember.role || "",
            phone: staffMember.personal_phone || staffMember.phone || "",
            email: staffMember.personal_email || staffMember.email || "",
            joining_date: staffMember.joining_date || "",
            salary: staffMember.monthly_salary || staffMember.salary || "",
            pf: staffMember.pf_percentage || staffMember.pf || "",
            esi: staffMember.esi_percentage || staffMember.esi || "",
            photo: staffMember.photo || "",
            needs_user_access: staffMember.needs_user_access || false,
            username: staffMember.username || "",
            project_ids: staffMember.project_assignments?.map(a => a.project_id) || []
        })
        setFormErrors([])
        setShowModal(true)
    }
    const handleViewDetails = (staffMember) => {
        setSelectedStaff(staffMember)
        setShowDetailModal(true)
    }
    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }))
    }
    const handleProjectToggle = (projectId) => {
        setFormData(prev => {
            const projectIds = prev.project_ids || []
            const isSelected = projectIds.includes(projectId)
            return {
                ...prev,
                project_ids: isSelected
                    ? projectIds.filter(id => id !== projectId)
                    : [...projectIds, projectId]
            }
        })
    }
    const handleSubmit = async (e) => {
        e.preventDefault()
        setFormErrors([])
        try {
            // Exclude project_ids from the submission data (backend doesn't handle it for now)
            const { project_ids, ...submitData } = formData
            if (isEditing) {
                const res = await api.put(`/api/staff/${selectedStaff.id}`, submitData)
                if (res.data.success) {
                    setShowModal(false)
                    setCurrentPage(1)
                    loadStaff()
                    showSuccess("Staff member updated successfully")
                } else {
                    setFormErrors(res.data.errors || [res.data.error])
                }
            } else {
                const res = await api.post("/api/staff", submitData)
                if (res.data.success) {
                    setShowModal(false)
                    setCurrentPage(1)
                    loadStaff()
                    showSuccess("Staff member created successfully")
                } else {
                    setFormErrors(res.data.errors || [res.data.error])
                }
            }
        } catch (err) {
            const errorData = err.response?.data
            if (errorData?.errors && Array.isArray(errorData.errors)) {
                setFormErrors(errorData.errors)
            } else {
                setFormErrors([errorData?.error || "Error saving staff member"])
            }
        }
    }
    const handleDelete = async (staffId) => {
        try {
            const res = await api.delete(`/api/staff/${staffId}`)
            if (res.data.success) {
                setConfirmDelete(null)
                loadStaff()
                showSuccess("Staff member deleted successfully")
            } else {
                showError(res.data.error || "Failed to delete staff member")
            }
        } catch (err) {
            showError(err.response?.data?.error || "Error deleting staff member")
        }
    }
    const handleReset = () => {
        setSearchQuery("")
        setRoleFilter("")
        setCurrentPage(1)
    }
    return (
        <div style={{background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)', minHeight: '100vh', padding: '24px'}}>
            <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold mb-2" style={{color: '#0052CC'}}>Staff Management</h1>
                <p className="text-gray-600">Manage your construction team members</p>
            </div>
            {/* Error Alert */}
            {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                    {error}
                </div>
            )}
            {/* Search & Filter Section */}
            <div style={{backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '24px', padding: '24px'}}>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                        <input
                            type="text"
                            placeholder="Search by name, phone, email..."
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value)
                                setCurrentPage(1)
                            }}
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    {/* Role Filter */}
                    <div className="relative">
                        <Filter className="absolute left-3 top-3 text-gray-400" size={20} />
                        <select
                            value={roleFilter}
                            onChange={(e) => {
                                setRoleFilter(e.target.value)
                                setCurrentPage(1)
                            }}
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
                        >
                            <option value="">All Roles</option>
                            {availableRoles.map(role => (
                                <option key={role} value={role}>{role}</option>
                            ))}
                        </select>
                    </div>
                    {/* Per Page */}
                    <select
                        value={perPage}
                        onChange={(e) => {
                            setPerPage(parseInt(e.target.value))
                            setCurrentPage(1)
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="5">5 per page</option>
                        <option value="10">10 per page</option>
                        <option value="25">25 per page</option>
                        <option value="50">50 per page</option>
                    </select>
                    {/* Reset Button */}
                    <button
                        onClick={handleReset}
                        className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
                    >
                        Reset Filters
                    </button>
                </div>
                {/* Add Staff Button */}
                <button
                    onClick={handleAddClick}
                    className="w-full md:w-auto text-white px-6 py-2 rounded-lg transition flex items-center justify-center gap-2"
                    style={{background: '#0052CC', cursor: 'pointer'}}
                    onMouseEnter={(e) => e.target.style.opacity = '0.8'}
                    onMouseLeave={(e) => e.target.style.opacity = '1'}
                >
                    <Plus size={20} />
                    Add Staff Member
                </button>
            </div>
            {/* Staff Table */}
            <div style={{backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden'}}>
                {loading ? (
                    <div className="p-8 text-center text-gray-500">
                        <div className="inline-block">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        </div>
                        <p className="mt-4">Loading staff members...</p>
                    </div>
                ) : staff.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        <p>No staff members found</p>
                    </div>
                ) : (
                    <>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead style={{backgroundColor: '#f0f5ff', borderBottom: '2px solid #0052CC'}}>
                                    <tr>
                                        <th className="text-left px-6 py-3 font-semibold" style={{color: '#0052CC'}}>Name</th>
                                        <th className="text-left px-6 py-3 font-semibold" style={{color: '#0052CC'}}>Role</th>
                                        <th className="text-left px-6 py-3 font-semibold" style={{color: '#0052CC'}}>Phone</th>
                                        <th className="text-left px-6 py-3 font-semibold" style={{color: '#0052CC'}}>Email</th>
                                        <th className="text-left px-6 py-3 font-semibold" style={{color: '#0052CC'}}>Joining Date</th>
                                        <th className="text-left px-6 py-3 font-semibold" style={{color: '#0052CC'}}>Salary</th>
                                        <th className="text-center px-6 py-3 font-semibold" style={{color: '#0052CC', display: 'none'}}>Projects</th>
                                        <th className="text-center px-6 py-3 font-semibold" style={{color: '#0052CC'}}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {staff.map((s) => (
                                        <tr key={s.id} className="border-b transition" style={{backgroundColor: 'white'}} onMouseEnter={(e) => e.target.style.backgroundColor = '#f0f5ff'} onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}>
                                            <td className="px-6 py-4 text-gray-900 font-medium">{s.first_name} {s.last_name}</td>
                                            <td className="px-6 py-4 text-gray-600">
                                                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                                                    {s.role}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-gray-600">{s.personal_phone}</td>
                                            <td className="px-6 py-4 text-gray-600">{s.personal_email || "-"}</td>
                                            <td className="px-6 py-4 text-gray-600">{s.joining_date}</td>
                                            <td className="px-6 py-4 text-gray-600 font-semibold">₹{parseFloat(s.monthly_salary || 0).toLocaleString()}</td>
                                            <td className="px-6 py-4 text-center" style={{display: 'none'}}>
                                                {s.project_assignments && s.project_assignments.length > 0 ? (
                                                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                                                        {s.project_assignments.length} Projects
                                                    </span>
                                                ) : (
                                                    <span className="text-gray-400 text-sm">-</span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-center">
                                                <div className="flex justify-center gap-2">
                                                    <button
                                                        onClick={() => handleViewDetails(s)}
                                                        className="p-2 text-blue-600 hover:bg-blue-50 rounded transition"
                                                        title="View details"
                                                    >
                                                        <Eye size={18} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleEditClick(s)}
                                                        className="p-2 text-green-600 hover:bg-green-50 rounded transition"
                                                        title="Edit"
                                                    >
                                                        <Edit2 size={18} />
                                                    </button>
                                                    <button
                                                        onClick={() => setConfirmDelete(s.id)}
                                                        className="p-2 text-red-600 hover:bg-red-50 rounded transition"
                                                        title="Delete"
                                                    >
                                                        <Trash2 size={18} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        {/* Pagination */}
                        <div style={{backgroundColor: '#f0f5ff', borderTop: '1px solid #ddd', padding: '16px 24px'}} className="flex items-center justify-between">
                            <div className="text-gray-600 text-sm">
                                Showing {(currentPage - 1) * perPage + 1} to {Math.min(currentPage * perPage, totalStaff)} of {totalStaff} staff members
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                    disabled={currentPage === 1}
                                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
                                >
                                    Previous
                                </button>
                                <div className="flex items-center gap-2">
                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                        const pageNum = i + 1
                                        return (
                                            <button
                                                key={pageNum}
                                                onClick={() => setCurrentPage(pageNum)}
                                                className="px-3 py-2 rounded-lg transition"
                                                style={currentPage === pageNum ? {background: '#0052CC', color: 'white'} : {border: '1px solid #ddd', backgroundColor: 'white'}}
                                            >
                                                {pageNum}
                                            </button>
                                        )
                                    })}
                                    {totalPages > 5 && <span className="px-2">...</span>}
                                </div>
                                <button
                                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                                    disabled={currentPage === totalPages}
                                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
            {/* Add/Edit Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div style={{backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 10px 25px rgba(0,0,0,0.2)'}} className="max-w-6xl w-full max-h-screen overflow-y-auto">
                        <div style={{backgroundColor: '#f0f5ff', borderBottom: '1px solid #0052CC', padding: '16px 24px'}} className="sticky top-0 flex justify-between items-center">
                            <h2 className="text-2xl font-bold" style={{color: '#0052CC'}}>
                                {isEditing ? "Edit Staff Member" : "Add New Staff Member"}
                            </h2>
                            <button
                                onClick={() => setShowModal(false)}
                                className="text-gray-500 hover:text-gray-700 text-2xl"
                            >
                                ×
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6">
                            {/* Error Messages */}
                            {formErrors.length > 0 && (
                                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                                    <ul className="text-red-700 list-disc list-inside">
                                        {formErrors.map((error, idx) => (
                                            <li key={idx}>{error}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                                {/* Name */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">Name *</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="Full name"
                                    />
                                </div>
                                {/* Role */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">Role *</label>
                                    <select
                                        name="role"
                                        value={formData.role}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                                    >
                                        <option value="">Select a role</option>
                                        {PREDEFINED_ROLES.map(role => (
                                            <option key={role} value={role}>{role}</option>
                                        ))}
                                    </select>
                                </div>
                                {/* Phone */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">Phone *</label>
                                    <input
                                        type="tel"
                                        name="phone"
                                        value={formData.phone}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="10-digit phone number"
                                    />
                                </div>
                                {/* Email */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">Email</label>
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="email@example.com"
                                    />
                                </div>
                                {/* Joining Date */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">Joining Date *</label>
                                    <input
                                        type="date"
                                        name="joining_date"
                                        value={formData.joining_date}
                                        onChange={handleInputChange}
                                        required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                {/* Salary */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">Salary *</label>
                                    <input
                                        type="number"
                                        name="salary"
                                        value={formData.salary}
                                        onChange={handleInputChange}
                                        required
                                        step="0.01"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="Monthly salary"
                                    />
                                </div>
                                {/* PF */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">PF (%) *</label>
                                    <input
                                        type="number"
                                        name="pf"
                                        value={formData.pf}
                                        onChange={handleInputChange}
                                        required
                                        step="0.01"
                                        min="0"
                                        max="100"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="PF percentage"
                                    />
                                </div>
                                {/* ESI */}
                                <div>
                                    <label className="block text-gray-700 font-semibold mb-2">ESI (%) *</label>
                                    <input
                                        type="number"
                                        name="esi"
                                        value={formData.esi}
                                        onChange={handleInputChange}
                                        required
                                        step="0.01"
                                        min="0"
                                        max="100"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="ESI percentage"
                                    />
                                </div>
                                {/* Photo URL */}
                                <div className="col-span-full">
                                    <label className="block text-gray-700 font-semibold mb-2">Photo URL</label>
                                    <input
                                        type="text"
                                        name="photo"
                                        value={formData.photo}
                                        onChange={handleInputChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="URL to staff photo"
                                    />
                                </div>
                            </div>
                            {/* User Account Section */}
                            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                <div className="flex items-center gap-3 mb-3">
                                    <input
                                        type="checkbox"
                                        id="needsUserAccess"
                                        name="needs_user_access"
                                        checked={formData.needs_user_access}
                                        onChange={handleInputChange}
                                        className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                                    />
                                    <label htmlFor="needsUserAccess" className="text-gray-700 font-semibold">
                                        Create User Account for Login
                                    </label>
                                </div>
                                <p className="text-gray-600 text-sm ml-8 mb-3">
                                    Enable this to allow this staff member to login to the system with their own account
                                </p>
                                {/* Username Field */}
                                {formData.needs_user_access && (
                                    <div className="ml-8">
                                        <label className="block text-gray-700 font-semibold mb-2">Username</label>
                                        <input
                                            type="text"
                                            name="username"
                                            value={formData.username}
                                            onChange={handleInputChange}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            placeholder="Leave blank to auto-generate from email"
                                        />
                                        <p className="text-gray-500 text-sm mt-1">
                                            Default password: Erp@123 (user must change on first login)
                                        </p>
                                    </div>
                                )}
                            {/* Project Assignment Section - Hidden */}
                            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg" style={{display: 'none'}}>
                                <label className="block text-gray-700 font-semibold mb-3">Assign Projects</label>
                                <p className="text-gray-600 text-sm mb-3">
                                    Select which projects this staff member will be assigned to
                                </p>
                                {projects.length === 0 ? (
                                    <p className="text-gray-500 text-sm">No projects available</p>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        {projects.map(project => (
                                            <div key={project.id} className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    id={`project-${project.id}`}
                                                    checked={(formData.project_ids || []).includes(project.id)}
                                                    onChange={() => handleProjectToggle(project.id)}
                                                    className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-2 focus:ring-green-500"
                                                />
                                                <label htmlFor={`project-${project.id}`} className="ml-2 text-gray-700 cursor-pointer">
                                                    {project.name || project.project_name}
                                                </label>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                            </div>
                            {/* Form Actions */}
                            <div className="flex gap-3 pt-4 border-t border-gray-300">
                                <button
                                    type="submit"
                                    className="flex-1 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-semibold"
                                >
                                    {isEditing ? "Update Staff Member" : "Create Staff Member"}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 bg-gray-300 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-400 transition font-semibold"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
            {/* Detail View Modal */}
            {showDetailModal && selectedStaff && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full">
                        <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-6 py-4 text-white flex justify-between items-center">
                            <h2 className="text-2xl font-bold">Staff Details</h2>
                            <button
                                onClick={() => setShowDetailModal(false)}
                                className="text-white hover:text-gray-200 text-2xl"
                            >
                                ×
                            </button>
                        </div>
                        <div className="p-6">
                            {selectedStaff.photo && (
                                <div className="mb-6 text-center">
                                    <img
                                        src={selectedStaff.photo}
                                        alt={selectedStaff.name}
                                        className="w-32 h-32 rounded-full mx-auto object-cover border-4 border-gray-200"
                                    />
                                </div>
                            )}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">Name</h3>
                                    <p className="text-gray-900 text-lg font-semibold">{selectedStaff.name}</p>
                                </div>
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">Role</h3>
                                    <p className="text-gray-900 text-lg font-semibold">{selectedStaff.role}</p>
                                </div>
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">Phone</h3>
                                    <p className="text-gray-900 text-lg">{selectedStaff.personal_phone}</p>
                                </div>
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">Email</h3>
                                    <p className="text-gray-900 text-lg">{selectedStaff.personal_email || "-"}</p>
                                </div>
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">Joining Date</h3>
                                    <p className="text-gray-900 text-lg">{selectedStaff.joining_date}</p>
                                </div>
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">Monthly Salary</h3>
                                    <p className="text-gray-900 text-lg font-semibold">₹{parseFloat(selectedStaff.monthly_salary || 0).toLocaleString()}</p>
                                </div>
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">PF (%)</h3>
                                    <p className="text-gray-900 text-lg">{selectedStaff.pf_percentage}%</p>
                                </div>
                                <div>
                                    <h3 className="text-gray-500 font-semibold text-sm mb-1">ESI (%)</h3>
                                    <p className="text-gray-900 text-lg">{selectedStaff.esi_percentage}%</p>
                                </div>
                            </div>
                            {/* Salary Breakdown */}
                            <div className="mt-6 bg-gray-50 rounded-lg p-4">
                                <h3 className="font-semibold text-gray-900 mb-3">Salary Breakdown</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-gray-600 text-sm">Gross Salary</p>
                                        <p className="text-gray-900 font-semibold text-lg">₹{parseFloat(selectedStaff.salary).toLocaleString()}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-600 text-sm">PF Deduction</p>
                                        <p className="text-gray-900 font-semibold text-lg">₹{(parseFloat(selectedStaff.salary) * selectedStaff.pf / 100).toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-600 text-sm">ESI Deduction</p>
                                        <p className="text-gray-900 font-semibold text-lg">₹{(parseFloat(selectedStaff.salary) * selectedStaff.esi / 100).toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
                                    </div>
                                    <div className="bg-blue-50 rounded p-3">
                                        <p className="text-gray-600 text-sm">Net Salary</p>
                                        <p className="text-blue-600 font-bold text-lg">₹{(parseFloat(selectedStaff.salary) - (parseFloat(selectedStaff.salary) * selectedStaff.pf / 100) - (parseFloat(selectedStaff.salary) * selectedStaff.esi / 100)).toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
                                    </div>
                                </div>
                            </div>
                            {/* Project Assignments - Hidden */}
                            {selectedStaff.project_assignments && selectedStaff.project_assignments.length > 0 && (
                                <div className="mt-6 bg-green-50 rounded-lg p-4 border border-green-200" style={{display: 'none'}}>
                                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                        <span className="text-green-600">📋</span>
                                        Assigned Projects
                                    </h3>
                                    <div className="space-y-2">
                                        {selectedStaff.project_assignments.map((assignment, idx) => (
                                            <div key={idx} className="flex items-center gap-2 p-2 bg-white rounded border border-green-100">
                                                <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                                                <span className="text-gray-700">
                                                    {assignment.project?.name || assignment.project_name || `Project ID: ${assignment.project_id}`}
                                                </span>
                                                <span className="text-xs text-gray-500 ml-auto">
                                                    Assigned: {new Date(assignment.assigned_on).toLocaleDateString()}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {/* Detail Actions */}
                            <div className="flex gap-3 mt-6 pt-4 border-t border-gray-300">
                                <button
                                    onClick={() => {
                                        setShowDetailModal(false)
                                        handleEditClick(selectedStaff)
                                    }}
                                    className="flex-1 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition font-semibold flex items-center justify-center gap-2"
                                >
                                    <Edit2 size={18} />
                                    Edit
                                </button>
                                <button
                                    onClick={() => setShowDetailModal(false)}
                                    className="flex-1 bg-gray-300 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-400 transition font-semibold"
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
            {/* Delete Confirmation Modal */}
            {confirmDelete !== null && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Confirm Delete</h2>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to delete this staff member? This action cannot be undone.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => handleDelete(confirmDelete)}
                                className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition font-semibold"
                            >
                                Delete
                            </button>
                            <button
                                onClick={() => setConfirmDelete(null)}
                                className="flex-1 bg-gray-300 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-400 transition font-semibold"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
            </div>
        </div>
    )
}