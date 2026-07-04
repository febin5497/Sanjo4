import React, { useState, useEffect } from 'react';
import api from '../../api/api';
import { useToast } from '../../components/Toast';
import FormModal from '../../components/FormModal';
import { PlusIcon, CalculatorIcon } from 'lucide-react';
const PayrollCyclePage = () => {
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    start_date: '',
    end_date: ''
  });
  useEffect(() => {
    fetchCycles();
  }, []);
  const fetchCycles = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/payroll/cycles');
      setCycles(response.data?.data?.cycles || []);
    } catch (error) {
      showToast('Error fetching cycles', 'error');
    } finally {
      setLoading(false);
    }
  };
  const handleSubmit = async () => {
    try {
      await api.post('/api/payroll/cycles', formData);
      showToast('Payroll cycle created successfully', 'success');
      setShowModal(false);
      fetchCycles();
    } catch (error) {
      showToast(error.response?.data?.message || 'Error creating cycle', 'error');
    }
  };
  const months = [
    { value: 1, label: 'January' },
    { value: 2, label: 'February' },
    { value: 3, label: 'March' },
    { value: 4, label: 'April' },
    { value: 5, label: 'May' },
    { value: 6, label: 'June' },
    { value: 7, label: 'July' },
    { value: 8, label: 'August' },
    { value: 9, label: 'September' },
    { value: 10, label: 'October' },
    { value: 11, label: 'November' },
    { value: 12, label: 'December' }
  ];
  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }
  return (
    <div className="p-6 max-w-6xl mx-auto min-h-screen" style={{ background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)' }}>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold" style={{ color: '#0052CC' }}>Payroll Management</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-white rounded-lg transition"
          style={{ backgroundColor: '#0052CC' }}
          onMouseEnter={(e) => e.target.style.opacity = '0.85'}
          onMouseLeave={(e) => e.target.style.opacity = '1'}
        >
          <PlusIcon size={20} />
          New Cycle
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg border p-6" style={{ borderColor: '#e2e8f0' }}>
          <p className="text-sm mb-1" style={{ color: '#64748b' }}>Total Cycles</p>
          <p className="text-2xl font-bold" style={{ color: '#1e293b' }}>{cycles.length}</p>
        </div>
        <div className="rounded-lg border p-6" style={{ backgroundColor: '#f0f5ff', borderColor: '#0052CC' }}>
          <p className="text-sm mb-1" style={{ color: '#0052CC' }}>Draft</p>
          <p className="text-2xl font-bold" style={{ color: '#0052CC' }}>
            {cycles.filter(c => c.status === 'draft').length}
          </p>
        </div>
        <div className="rounded-lg border p-6" style={{ backgroundColor: '#f0fdf4', borderColor: '#10b981' }}>
          <p className="text-sm mb-1" style={{ color: '#10b981' }}>Approved</p>
          <p className="text-2xl font-bold" style={{ color: '#10b981' }}>
            {cycles.filter(c => c.status === 'approved').length}
          </p>
        </div>
        <div className="rounded-lg border p-6" style={{ backgroundColor: '#faf5ff', borderColor: '#9333ea' }}>
          <p className="text-sm mb-1" style={{ color: '#9333ea' }}>Paid</p>
          <p className="text-2xl font-bold" style={{ color: '#9333ea' }}>
            {cycles.filter(c => c.status === 'paid').length}
          </p>
        </div>
      </div>
      <div className="bg-white rounded-lg border overflow-hidden" style={{ borderColor: '#e2e8f0' }}>
        <table className="w-full">
          <thead style={{ backgroundColor: '#f0f5ff', borderColor: '#e2e8f0', borderBottom: '1px solid #e2e8f0' }}>
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold" style={{ color: '#0052CC' }}>Period</th>
              <th className="px-6 py-3 text-left text-sm font-semibold" style={{ color: '#0052CC' }}>Start Date</th>
              <th className="px-6 py-3 text-left text-sm font-semibold" style={{ color: '#0052CC' }}>End Date</th>
              <th className="px-6 py-3 text-center text-sm font-semibold" style={{ color: '#0052CC' }}>Status</th>
              <th className="px-6 py-3 text-center text-sm font-semibold" style={{ color: '#0052CC' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {cycles.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center" style={{ color: '#64748b' }}>
                  No payroll cycles created yet
                </td>
              </tr>
            ) : (
              cycles.map(cycle => (
                <tr key={cycle.id} className="border-b" style={{ borderColor: '#e2e8f0', color: '#1e293b' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0f5ff'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                  <td className="px-6 py-4 font-semibold">
                    {months[cycle.month - 1]?.label} {cycle.year}
                  </td>
                  <td className="px-6 py-4">
                    {cycle.start_date ? new Date(cycle.start_date).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4">
                    {cycle.end_date ? new Date(cycle.end_date).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="px-3 py-1 rounded-full text-xs font-medium" style={{
                      backgroundColor: cycle.status === 'draft' ? '#f3f4f6' : cycle.status === 'approved' ? '#f0fdf4' : '#faf5ff',
                      color: cycle.status === 'draft' ? '#1e293b' : cycle.status === 'approved' ? '#10b981' : '#9333ea'
                    }}>
                      {cycle.status.charAt(0).toUpperCase() + cycle.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {cycle.status === 'draft' && (
                      <button className="p-2 rounded transition" style={{ color: '#0052CC' }} onMouseEnter={(e) => e.target.style.backgroundColor = '#f0f5ff'} onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}>
                        <CalculatorIcon size={18} />
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <FormModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create Payroll Cycle"
        onSubmit={handleSubmit}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#1e293b' }}>Month *</label>
              <select
                className="w-full px-3 py-2 rounded"
                style={{ borderColor: '#d1d5db', border: '1px solid #d1d5db' }}
                onFocus={(e) => { e.target.style.borderColor = '#0052CC'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 82, 204, 0.1)'; }}
                onBlur={(e) => { e.target.style.borderColor = '#d1d5db'; e.target.style.boxShadow = 'none'; }}
                value={formData.month}
                onChange={(e) => setFormData({ ...formData, month: parseInt(e.target.value) })}
              >
                {months.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#1e293b' }}>Year *</label>
              <input
                type="number"
                className="w-full px-3 py-2 rounded"
                style={{ borderColor: '#d1d5db', border: '1px solid #d1d5db' }}
                onFocus={(e) => { e.target.style.borderColor = '#0052CC'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 82, 204, 0.1)'; }}
                onBlur={(e) => { e.target.style.borderColor = '#d1d5db'; e.target.style.boxShadow = 'none'; }}
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#1e293b' }}>Start Date</label>
              <input
                type="date"
                className="w-full px-3 py-2 rounded"
                style={{ borderColor: '#d1d5db', border: '1px solid #d1d5db' }}
                onFocus={(e) => { e.target.style.borderColor = '#0052CC'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 82, 204, 0.1)'; }}
                onBlur={(e) => { e.target.style.borderColor = '#d1d5db'; e.target.style.boxShadow = 'none'; }}
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#1e293b' }}>End Date</label>
              <input
                type="date"
                className="w-full px-3 py-2 rounded"
                style={{ borderColor: '#d1d5db', border: '1px solid #d1d5db' }}
                onFocus={(e) => { e.target.style.borderColor = '#0052CC'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 82, 204, 0.1)'; }}
                onBlur={(e) => { e.target.style.borderColor = '#d1d5db'; e.target.style.boxShadow = 'none'; }}
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              />
            </div>
          </div>
        </div>
      </FormModal>
    </div>
  );
};
export default PayrollCyclePage;
