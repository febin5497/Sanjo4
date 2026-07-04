import { useState, useEffect } from 'react'
import api from '../../api/api'
import { useToast } from '../../components/Toast'
import { FaCheckCircle, FaTimesCircle, FaClock, FaFilter, FaSearch, FaShieldAlt } from 'react-icons/fa'
const PendingApprovalsPage = () => {
  const [pendingApprovals, setPendingApprovals] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [perPage, setPerPage] = useState(10)
  const [totalPages, setTotalPages] = useState(1)
  const [entityTypeFilter, setEntityTypeFilter] = useState('')
  const [approvalLoading, setApprovalLoading] = useState(false)
  const [rejectionModalOpen, setRejectionModalOpen] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')
  const [selectedExpenseForRejection, setSelectedExpenseForRejection] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const { showSuccess, showError } = useToast()
  useEffect(() => {
    loadApprovals()
  }, [currentPage, perPage, entityTypeFilter])
  const loadApprovals = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: currentPage,
        per_page: perPage,
        status: 'pending',
        approval_tier: 'Tier2_second'  // Tier 2 Second Approvals: >₹50,000 awaiting second approval
      })
      const res = await api.get(`/api/staff/approvals/expenses?${params}`)
      const data = res.data?.data || []
      setPendingApprovals(data)
      setTotalPages(res.data?.pagination?.pages || 1)
    } catch (err) {
      showError(err.response?.data?.error || 'Failed to load pending approvals')
    } finally {
      setLoading(false)
    }
  }
  const handleDirectApprove = async (expense) => {
    try {
      setApprovalLoading(true)
      await api.post(`/api/staff/expenses/${expense.id}/approve`)
      showSuccess('Second approval recorded. Expense fully approved!')
      loadApprovals()
    } catch (err) {
      showError(err.response?.data?.error || 'Failed to approve expense')
    } finally {
      setApprovalLoading(false)
    }
  }
  const handleDirectReject = (expense) => {
    setSelectedExpenseForRejection(expense)
    setRejectionReason('')
    setRejectionModalOpen(true)
  }
  const handleConfirmReject = async () => {
    if (!rejectionReason.trim()) {
      showError('Please provide a rejection reason')
      return
    }
    try {
      setApprovalLoading(true)
      await api.post(`/api/staff/expenses/${selectedExpenseForRejection.id}/reject`, {
        rejection_reason: rejectionReason
      })
      showSuccess('Expense rejected successfully')
      setRejectionModalOpen(false)
      setRejectionReason('')
      setSelectedExpenseForRejection(null)
      loadApprovals()
    } catch (err) {
      showError(err.response?.data?.error || 'Failed to reject expense')
    } finally {
      setApprovalLoading(false)
    }
  }
  const getStatusBadge = (status) => {
    const badges = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: FaClock },
      approved: { bg: 'bg-green-100', text: 'text-green-800', icon: FaCheckCircle },
      rejected: { bg: 'bg-red-100', text: 'text-red-800', icon: FaTimesCircle }
    }
    const badge = badges[status] || badges.pending
    const IconComponent = badge.icon
    return (
      <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${badge.bg} ${badge.text}`}>
        <IconComponent size={14} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }
  const getTierBadge = (tier, approvals_received, approvals_required) => {
    const isComplete = approvals_received >= approvals_required
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
        isComplete ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
      }`}>
        <span className="font-semibold">{tier}</span>
        <span className="text-xs font-bold">({approvals_received}/{approvals_required})</span>
      </span>
    )
  }
  const formatDate = (date) => {
    if (!date) return '-'
    return new Date(date).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  const filteredApprovals = pendingApprovals.filter(exp =>
    !searchTerm ||
    exp.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    exp.staff_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    exp.project_name?.toLowerCase().includes(searchTerm.toLowerCase())
  )
  const totalAmount = pendingApprovals.reduce((sum, exp) => sum + (exp.amount || 0), 0)
  const criticalApprovals = pendingApprovals.filter(exp => exp.amount > 200000).length
  return (
    <div className="min-h-screen" style={{background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)'}}>
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header Section */}
          <div className="mb-8">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Final Approval Required</h1>
                <p className="text-gray-600 text-lg flex items-center gap-2">
                  <FaShieldAlt className="text-orange-600" />
                  Tier 2 - Second Level Approval (Amounts {'\u003e'}₹50,000)
                </p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-orange-600">₹{totalAmount.toLocaleString('en-IN')}</div>
                <p className="text-gray-600 text-sm">Awaiting Final Approval</p>
              </div>
            </div>
          </div>
          {/* Alert Banner for Critical Approvals */}
          {criticalApprovals > 0 && (
            <div className="rounded-lg p-4 mb-8 flex items-start gap-4" style={{background: '#fee2e2', borderLeft: '4px solid #dc2626'}}>
              <FaTimesCircle className="text-xl flex-shrink-0 mt-0.5" style={{color: '#dc2626'}} />
              <div>
                <h3 className="font-bold" style={{color: '#7f1d1d'}}>Critical Approvals Pending</h3>
                <p className="text-sm mt-1" style={{color: '#991b1b'}}>
                  <strong>{criticalApprovals} expense(s)</strong> exceeding ₹2,00,000 require immediate attention
                </p>
              </div>
            </div>
          )}
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4" style={{borderLeftColor: '#0052CC'}}>
              <p className="text-gray-600 text-sm font-medium">Pending Final Approvals</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{pendingApprovals.length}</p>
              <p className="text-xs text-gray-500 mt-2">All at Stage 1/2</p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4" style={{borderLeftColor: '#0052CC'}}>
              <p className="text-gray-600 text-sm font-medium">Total Amount</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">₹{(totalAmount / 100000).toFixed(1)}L</p>
              <p className="text-xs text-gray-500 mt-2">Requiring your approval</p>
            </div>
            <div className={`rounded-lg shadow-sm p-6 border-l-4 bg-white`} style={{borderLeftColor: criticalApprovals > 0 ? '#dc2626' : '#0052CC'}}>
              <p className={`text-sm font-medium`} style={{color: criticalApprovals > 0 ? '#dc2626' : '#0052CC'}}>
                Critical Items ({'\u003e'}₹2L)
              </p>
              <p className={`text-3xl font-bold mt-2`} style={{color: criticalApprovals > 0 ? '#dc2626' : '#1e293b'}}>
                {criticalApprovals}
              </p>
              <p className="text-xs mt-2" style={{color: criticalApprovals > 0 ? '#991b1b' : '#9ca3af'}}>
                {criticalApprovals > 0 ? 'Require urgent review' : 'All within limits'}
              </p>
            </div>
          </div>
          {/* Search and Filter Section */}
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6 border border-gray-200">
            <div className="flex gap-4 items-center flex-wrap">
              <div className="flex-1 min-w-[250px] relative">
                <FaSearch className="absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by staff, project, or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:border-transparent"
                  style={{outline: 'none', boxShadow: 'none'}}
                  onFocus={(e) => e.target.style.borderColor = '#0052CC'}
                  onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                />
              </div>
              <div className="flex items-center gap-2">
                <FaFilter className="text-gray-400" size={16} />
                <select
                  value={entityTypeFilter}
                  onChange={(e) => {
                    setEntityTypeFilter(e.target.value)
                    setCurrentPage(1)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:border-transparent bg-white"
                  style={{outline: 'none', boxShadow: 'none'}}
                  onFocus={(e) => e.target.style.borderColor = '#0052CC'}
                  onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                >
                  <option value="">All Categories</option>
                  <option value="Materials">Materials</option>
                  <option value="Labor">Labor</option>
                  <option value="Equipment">Equipment</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </div>
          {/* Table Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="text-center">
                  <div className="inline-block animate-spin">
                    <div className="h-12 w-12 border-4 border-orange-200 border-t-orange-600 rounded-full"></div>
                  </div>
                  <p className="text-gray-500 mt-4">Loading pending approvals...</p>
                </div>
              </div>
            ) : filteredApprovals.length === 0 ? (
              <div className="flex justify-center items-center h-64">
                <div className="text-center">
                  <FaCheckCircle className="mx-auto text-5xl text-green-400 mb-4" />
                  <p className="text-gray-600 text-lg font-medium">All set! ✨</p>
                  <p className="text-gray-500 mt-2">No expenses awaiting final approval</p>
                </div>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left" style={{background: '#f0f5ff'}}>
                        <th className="px-6 py-4 font-semibold" style={{color: '#0052CC'}}>Staff</th>
                        <th className="px-6 py-4 font-semibold" style={{color: '#0052CC'}}>Project</th>
                        <th className="px-6 py-4 font-semibold" style={{color: '#0052CC'}}>Description</th>
                        <th className="px-6 py-4 font-semibold" style={{color: '#0052CC'}}>Category</th>
                        <th className="px-6 py-4 font-semibold text-right" style={{color: '#0052CC'}}>Amount</th>
                        <th className="px-6 py-4 font-semibold" style={{color: '#0052CC'}}>Approval Stage</th>
                        <th className="px-6 py-4 font-semibold" style={{color: '#0052CC'}}>Status</th>
                        <th className="px-6 py-4 font-semibold text-center" style={{color: '#0052CC'}}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredApprovals.map((expense) => (
                        <tr key={expense.id} className="border-b transition duration-150 group" style={{background: '#ffffff'}} onMouseEnter={(e) => e.currentTarget.style.background = '#f0f5ff'} onMouseLeave={(e) => e.currentTarget.style.background = '#ffffff'}>
                          <td className="px-6 py-4 font-medium text-gray-900">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 rounded-full text-white flex items-center justify-center text-xs font-bold" style={{background: '#0052CC'}}>
                                {expense.staff_name?.[0] || 'U'}
                              </div>
                              {expense.staff_name || 'Unknown'}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-gray-700 font-medium">
                            {expense.project_name || 'Unassigned'}
                          </td>
                          <td className="px-6 py-4">
                            <span className="px-3 py-1 rounded-md font-medium text-xs text-white" style={{background: '#0052CC'}}>
                              {expense.description}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-gray-600">
                            <span className="px-2 py-1 rounded bg-gray-100 text-gray-700 text-xs">
                              {expense.category}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div>
                              <span className={`font-bold text-lg block ${expense.amount > 200000 ? 'text-red-600' : 'text-gray-900'}`}>
                                ₹{expense.amount?.toLocaleString('en-IN')}
                              </span>
                              {expense.amount > 200000 && (
                                <span className="text-red-600 text-xs font-semibold">⚠️ Critical</span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <div className="flex gap-1">
                                <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-white text-xs font-bold">✓</div>
                                <div className="w-6 h-6 rounded-full bg-orange-500 flex items-center justify-center text-white text-xs font-bold">
                                  {expense.approvals_received + 1}
                                </div>
                              </div>
                              <span className="text-gray-700 text-sm font-medium">1 of 2</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            {getStatusBadge(expense.status)}
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="flex gap-2 justify-center opacity-0 group-hover:opacity-100 transition">
                              <button
                                onClick={() => handleDirectApprove(expense)}
                                disabled={approvalLoading}
                                className="px-4 py-2 text-white rounded-lg transition text-xs font-medium disabled:opacity-50 shadow-sm"
                                style={{background: '#0052CC'}}
                                onMouseEnter={(e) => e.target.style.opacity = '0.8'}
                                onMouseLeave={(e) => e.target.style.opacity = '1'}
                                title="Final Approval"
                              >
                                ✓ Final Approve
                              </button>
                              <button
                                onClick={() => handleDirectReject(expense)}
                                disabled={approvalLoading}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-xs font-medium disabled:opacity-50 shadow-sm"
                                title="Reject this expense"
                              >
                                ✕ Reject
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {/* Pagination */}
                <div className="border-t px-6 py-4 flex items-center justify-between bg-gray-50">
                  <div className="text-sm text-gray-600">
                    Page <span className="font-semibold text-gray-900">{currentPage}</span> of <span className="font-semibold text-gray-900">{totalPages}</span>
                    {' '} • Showing <span className="font-semibold text-gray-900">{filteredApprovals.length}</span> items
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
                    >
                      ← Previous
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
                    >
                      Next →
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
      {/* Rejection Modal */}
      {rejectionModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full animate-in">
            <div className="border-b border-gray-200 px-6 py-4 bg-red-50">
              <h3 className="text-xl font-bold text-red-900">Reject Expense</h3>
              <p className="text-red-700 text-sm mt-1">
                {selectedExpenseForRejection?.description} - ₹{selectedExpenseForRejection?.amount?.toLocaleString('en-IN')}
              </p>
            </div>
            <div className="px-6 py-4">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Rejection Reason <span className="text-red-500">*</span>
              </label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Provide a clear reason for rejecting this expense..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                rows="4"
              />
            </div>
            <div className="border-t border-gray-200 px-6 py-4 flex gap-3 justify-end">
              <button
                onClick={() => {
                  setRejectionModalOpen(false)
                  setRejectionReason('')
                  setSelectedExpenseForRejection(null)
                }}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmReject}
                disabled={approvalLoading}
                className="px-6 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition disabled:opacity-50"
              >
                {approvalLoading ? 'Rejecting...' : 'Confirm Rejection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
export default PendingApprovalsPage
