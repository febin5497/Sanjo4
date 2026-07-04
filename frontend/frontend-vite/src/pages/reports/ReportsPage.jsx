import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, LineChart, PieChart, Download } from 'lucide-react';
const ReportsPage = () => {
  const navigate = useNavigate();
  const [selectedReport, setSelectedReport] = useState(null);
  const reports = [
    {
      id: 'profitability',
      name: 'Project Profitability',
      description: 'Revenue vs Expenses analysis by project',
      icon: BarChart,
      route: '/reports/profitability'
    },
    {
      id: 'budget-variance',
      name: 'Budget vs Actual',
      description: 'Compare budgeted amounts with actual spending',
      icon: LineChart,
      route: '/reports/budget-variance'
    },
    {
      id: 'cash-flow',
      name: 'Cash Flow',
      description: 'Track cash inflows and outflows over time',
      icon: LineChart,
      route: '/reports/cash-flow'
    },
    {
      id: 'receivables-aging',
      name: 'Receivables Aging',
      description: 'Monitor outstanding customer payments',
      icon: PieChart,
      route: '/reports/receivables-aging'
    }
  ];
  const handleViewReport = (route) => {
    navigate(route);
  };
  return (
    <div className="p-6 max-w-6xl mx-auto min-h-screen" style={{ background: 'linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%)' }}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold" style={{ color: '#0052CC' }}>Financial Reports</h1>
        <p style={{ color: '#64748b' }} className="mt-2">Generate and view comprehensive financial reports</p>
      </div>
      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map(report => {
          const Icon = report.icon;
          return (
            <div
              key={report.id}
              className="bg-white rounded-lg border p-6 transition-shadow cursor-pointer"
              style={{ borderColor: '#e2e8f0' }}
              onClick={() => handleViewReport(report.route)}
              onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 82, 204, 0.16)'}
              onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-lg" style={{ backgroundColor: '#f0f5ff' }}>
                    <Icon size={24} style={{ color: '#0052CC' }} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold" style={{ color: '#1e293b' }}>{report.name}</h3>
                  </div>
                </div>
              </div>
              <p style={{ color: '#64748b' }} className="mb-4">{report.description}</p>
              <button className="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition" style={{ backgroundColor: '#0052CC' }} onMouseEnter={(e) => e.target.style.opacity = '0.85'} onMouseLeave={(e) => e.target.style.opacity = '1'}>
                <Download size={16} />
                View Report
              </button>
            </div>
          );
        })}
      </div>
      {/* Quick Stats */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold mb-6" style={{ color: '#0052CC' }}>Report Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border p-6" style={{ borderColor: '#e2e8f0' }}>
            <p className="text-sm mb-1" style={{ color: '#64748b' }}>Total Reports</p>
            <p className="text-3xl font-bold" style={{ color: '#1e293b' }}>4</p>
          </div>
          <div className="bg-white rounded-lg border p-6" style={{ borderColor: '#e2e8f0' }}>
            <p className="text-sm mb-1" style={{ color: '#64748b' }}>Generated Today</p>
            <p className="text-3xl font-bold" style={{ color: '#1e293b' }}>0</p>
          </div>
          <div className="bg-white rounded-lg border p-6" style={{ borderColor: '#e2e8f0' }}>
            <p className="text-sm mb-1" style={{ color: '#64748b' }}>This Month</p>
            <p className="text-3xl font-bold" style={{ color: '#1e293b' }}>0</p>
          </div>
          <div className="bg-white rounded-lg border p-6" style={{ borderColor: '#e2e8f0' }}>
            <p className="text-sm mb-1" style={{ color: '#64748b' }}>Last Updated</p>
            <p className="text-lg font-semibold" style={{ color: '#1e293b' }}>-</p>
          </div>
        </div>
      </div>
    </div>
  );
};
export default ReportsPage;
