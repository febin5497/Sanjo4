import { useState, useEffect, useMemo } from "react"
import { BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import api from "../../api/api"
import axios from "axios"
import { useToast } from "../../components/Toast"
import "../../styles/Dashboard.css"

const BLUE = "#3B82F6"
const ORANGE = "#F59E0B"
const GREEN = "#10B981"
const RED = "#EF4444"
const PURPLE = "#8B5CF6"
const CYAN = "#06B6D4"
const PINK = "#EC4899"
const COLORS = [BLUE, GREEN, ORANGE, RED, PURPLE, CYAN, PINK]

function n(v) { return v ?? 0 }

function fmt(n) {
  if (!n) return "₹0"
  const a = Math.abs(n)
  if (a >= 1e7) return `₹${(a / 1e7).toFixed(1)}Cr`
  if (a >= 1e5) return `₹${(a / 1e5).toFixed(1)}L`
  if (a >= 1e3) return `₹${(a / 1e3).toFixed(1)}K`
  return `₹${Math.round(a).toLocaleString('en-IN')}`
}

function ago(ts) {
  if (!ts) return ""
  try {
    const s = Math.floor((Date.now() - new Date(ts).getTime()) / 1000)
    if (s < 60) return "Just now"
    if (s < 3600) return `${Math.floor(s / 60)}m ago`
    if (s < 86400) return `${Math.floor(s / 3600)}h ago`
    if (s < 604800) return `${Math.floor(s / 86400)}d ago`
    return new Date(ts).toLocaleDateString()
  } catch { return "" }
}

function Gauge({ pct, color = BLUE, size = 80 }) {
  const s = 5, r = (size - s) / 2, c = Math.PI * r, off = c * (1 - Math.min(Math.max(pct, 0), 100) / 100)
  const cx = size / 2, cy = size / 2
  return (
    <svg width={size} height={size / 2 + 16} viewBox={`0 0 ${size} ${size / 2 + 16}`}>
      <path d={`M ${s / 2} ${cy} A ${r} ${r} 0 0 1 ${size - s / 2} ${cy}`} fill="none" stroke="#E8EDF2" strokeWidth={s} strokeLinecap="round" />
      <path d={`M ${s / 2} ${cy} A ${r} ${r} 0 0 1 ${size - s / 2} ${cy}`} fill="none" stroke={color} strokeWidth={s} strokeLinecap="round" strokeDasharray={c} strokeDashoffset={off} />
      <text x={cx} y={cy + 2} textAnchor="middle" fontSize={14} fontWeight={700} fill="#1E293B" fontFamily="Inter,system-ui,sans-serif">
        {Math.round(pct)}<tspan fontSize={8} fill="#94A3B8">%</tspan>
      </text>
    </svg>
  )
}

function Avatar({ name, color }) {
  const init = (name || "?").split(" ").map(s => s[0]).join("").toUpperCase().slice(0, 2)
  return <div className="av" style={{ background: color || BLUE }}>{init}</div>
}

function StatMini({ icon, value, label, color }) {
  return (
    <div className="stat-mini">
      <div className="stat-mini-icon" style={{ background: `${color}12`, color }}>{icon}</div>
      <div className="stat-mini-val">{value}</div>
      <div className="stat-mini-lbl">{label}</div>
    </div>
  )
}

function HeroCard({ project, totalIncome, totalExpense, balance, margin }) {
  const p = project || { name: "No projects yet", progress: 0, status: "pending" }
  const statusColor = p.status === 'active' || p.status === 'in_progress' ? GREEN : p.status === 'pending' ? ORANGE : "#94A3B8"
  const sl = (p.status || "").replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())
  return (
    <div className="hero-crd">
      <div className="hero-bg" />
      <div className="hero-inner">
        <div className="hero-top">
          <div>
            <span className="hero-tag">Current Project</span>
            <h2 className="hero-title">{p.name}</h2>
            <p className="hero-desc">Commercial construction · Downtown development · Phase 2</p>
          </div>
          <span className="hero-badge" style={{ color: statusColor, background: `${statusColor}12` }}>{sl}</span>
        </div>
        <div className="hero-mid">
          <div className="hero-prog">
            <div className="hero-prog-top">
              <span className="hero-prog-l">Overall Progress</span>
              <span className="hero-prog-v">{p.progress}%</span>
            </div>
            <div className="hero-bar"><div className="hero-bar-f" style={{ width: `${p.progress}%` }} /></div>
          </div>
          <div className="hero-stats">
            <div className="hero-stat"><span className="hero-stat-v">{fmt(totalIncome)}</span><span className="hero-stat-l">Revenue</span></div>
            <div className="hero-stat"><span className="hero-stat-v">{fmt(totalExpense)}</span><span className="hero-stat-l">Expenses</span></div>
            <div className="hero-stat"><span className="hero-stat-v" style={{ color: balance >= 0 ? GREEN : RED }}>{fmt(balance)}</span><span className="hero-stat-l">{margin}% margin</span></div>
          </div>
        </div>
        <div className="hero-btm">
          <div className="hero-team">
            <Avatar name="John D" color="#3B82F6" />
            <Avatar name="Sarah M" color="#10B981" />
            <Avatar name="Raj K" color="#F59E0B" />
            <div className="av av-more">+2</div>
          </div>
          <div className="hero-meta">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>
            <span>Deadline: Dec 2026</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function GaugeCard({ pct, label, sub, color = BLUE }) {
  return (
    <div className="gcrd">
      <Gauge pct={pct} color={color} size={80} />
      <div className="gcrd-l">{label}</div>
      <div className="gcrd-s">{sub}</div>
    </div>
  )
}

function ChartTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#fff', borderRadius: 10, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', padding: '8px 12px', fontFamily: 'Inter,system-ui,sans-serif', fontSize: 12 }}>
      <div style={{ fontWeight: 600, color: '#1E293B', marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, display: 'flex', justifyContent: 'space-between', gap: 16 }}>
          <span>{p.name}</span>
          <span style={{ fontWeight: 600 }}>{formatter ? formatter(p.value) : fmt(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const { showError } = useToast()
  const [loading, setLoading] = useState(true)
  const [raw, setRaw] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const token = localStorage.getItem("token")
      const hdrs = token ? { Authorization: `Bearer ${token}` } : {}
      const ok = r => r?.data?.success && r?.data?.data
      const ar = r => ok(r) ? (Array.isArray(r.data.data) ? r.data.data : (r.data.data.items || [])) : []
      const w = url => axios.get(url, { headers: hdrs, timeout: 8000 }).then(r => r).catch(() => ({ data: { success: false, data: null } }))
      try {
        const [pr, sr, vr, fr, br, er, lr, tr, att, attStats, exp, inv, maint, cashFlow] = await Promise.all([
          w('/api/projects?per_page=100'), w('/api/staff?per_page=100'),
          w('/api/vehicles?per_page=100'), w('/api/finance/summary'),
          w('/api/finance/budgets?per_page=50'), w('/api/equipment/stats'),
          w('/api/admin/activity-logs?per_page=10'), w('/api/finance/transactions?per_page=50'),
          w('/api/attendance?per_page=100'), w('/api/attendance/approvals/stats'),
          w('/api/staff/expenses?per_page=50'), w('/api/finance/invoices?per_page=20'),
          w('/api/vehicles/maintenance-due'), w('/api/finance/reports/cash-flow'),
        ])
        const projects = ar(pr), staff = ar(sr), vehicles = ar(vr), budgets = ar(br)
        const txs = ar(tr), logs = ar(lr).slice(0, 8)
        const attendance = ar(att), expenses = ar(exp), invoices = ar(inv)
        const maintenanceDue = ar(maint)

        let ti = 0, te = 0
        if (ok(fr)) { ti = n(fr.data.data.total_income); te = n(fr.data.data.total_expense) }

        let mr = 0
        try { const dr = await w('/api/dashboard'); if (ok(dr)) mr = n(dr.data.data.monthlyRevenue) } catch {}

        let bu = 0, bt = 0
        budgets.forEach(b => { bt += n(b.allocated_amount || b.budget_amount); bu += n(b.used_amount) })

        let ea = 0, et = 0
        if (ok(er)) { et = n(er.data.data.total); ea = n(er.data.data.active || er.data.data.available) }

        let cats = []
        try {
          const all = await w('/api/finance/transactions?per_page=500')
          const a = ar(all); const m = {}
          a.forEach(x => { const c = x.category || 'Other'; m[c] = (m[c] || 0) + Math.abs(n(x.amount)) })
          cats = Object.entries(m).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 6)
        } catch {}

        let attStatsData = {}
        if (ok(attStats)) attStatsData = attStats.data.data || {}

        let totalFuel = 0
        vehicles.forEach(v => { totalFuel += n(v.fuel_cost || v.total_fuel_cost) })

        let pendingExpenses = expenses.filter(e => e.status === 'pending')
        let totalPendingExpenses = pendingExpenses.reduce((s, e) => s + n(e.amount), 0)

        let paidInvoices = invoices.filter(i => i.status === 'paid' || i.payment_status === 'paid')
        let pendingInvoices = invoices.filter(i => i.status !== 'paid' && i.payment_status !== 'paid')
        let totalPendingInvoiceAmt = pendingInvoices.reduce((s, i) => s + n(i.total_amount || i.amount), 0)

        let cashFlowData = []
        if (ok(cashFlow)) cashFlowData = Array.isArray(cashFlow.data.data) ? cashFlow.data.data : []

        // Build expense trend from transactions
        const expTrend = {}
        txs.filter(t => t.type === 'expense').forEach(t => {
          const d = t.date || (t.created_at || '').slice(0, 10)
          if (d) expTrend[d] = (expTrend[d] || 0) + Math.abs(n(t.amount))
        })
        const expenseTrend = Object.entries(expTrend).map(([date, amount]) => ({ date, amount })).sort((a, b) => a.date.localeCompare(b.date)).slice(-7)

        // Build income trend
        const incTrend = {}
        txs.filter(t => t.type === 'income').forEach(t => {
          const d = t.date || (t.created_at || '').slice(0, 10)
          if (d) incTrend[d] = (incTrend[d] || 0) + n(t.amount)
        })
        const incomeTrend = Object.entries(incTrend).map(([date, amount]) => ({ date, amount })).sort((a, b) => a.date.localeCompare(b.date)).slice(-7)

        // Staff by role
        const roleMap = {}
        staff.forEach(s => { const r = s.role || 'Other'; roleMap[r] = (roleMap[r] || 0) + 1 })
        const staffByRole = Object.entries(roleMap).map(([name, value]) => ({ name: name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()), value }))

        // Attendance by status
        const attStatus = { Present: 0, Absent: 0, Late: 0, Leave: 0 }
        attendance.forEach(a => {
          const st = (a.status || 'present').toLowerCase()
          if (st === 'present' || st === 'approved') attStatus.Present++
          else if (st === 'absent') attStatus.Absent++
          else if (st === 'late') attStatus.Late++
          else if (st === 'leave') attStatus.Leave++
        })
        const attPie = Object.entries(attStatus).filter(([, v]) => v > 0).map(([name, value]) => ({ name, value }))

        // Monthly revenue data (last 6 months)
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        const revByMonth = {}
        txs.filter(t => t.type === 'income').forEach(t => {
          const d = new Date(t.date || t.created_at)
          const m = months[d.getMonth()]
          revByMonth[m] = (revByMonth[m] || 0) + n(t.amount)
        })
        const revData = months.filter(m => revByMonth[m]).map(m => ({ month: m, revenue: revByMonth[m] }))

        // Project status distribution
        const projStatus = {}
        projects.forEach(p => { const s = (p.status || 'pending').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()); projStatus[s] = (projStatus[s] || 0) + 1 })
        const projDist = Object.entries(projStatus).map(([name, value]) => ({ name, value }))

        setRaw({ projects, staff, vehicles, ti, te, mr, bu, bt, ea, et, txs: txs.slice(0, 6), logs, cats, attendance, attStatsData, expenses, pendingExpenses, totalPendingExpenses, invoices, paidInvoices, pendingInvoices, totalPendingInvoiceAmt, maintenanceDue, totalFuel, cashFlowData, expenseTrend, incomeTrend, staffByRole, attPie, revData, projDist })
      } catch { setRaw({}); showError('Failed to load') }
      setLoading(false)
    }
    load()
  }, [])

  const metrics = useMemo(() => {
    if (!raw) return { count: 0, activeStaff: 0, totalStaff: 0, ti: 0, te: 0, mr: 0, balance: 0, margin: "0.0", bpct: 0, avgProgress: 0, resourcePct: 0, revPct: 0, featured: null, projects: [], txs: [], logs: [], cats: [], bu: 0, bt: 0, activeVehicles: 0, totalVehicles: 0, maintDueCount: 0, totalFuel: 0, presentToday: 0, pendingApprovals: 0, pendingExpenses: [], totalPendingExpenses: 0, paidInvoices: 0, pendingInvoices: [], totalPendingInvoiceAmt: 0, cashFlowData: [], expenseTrend: [], incomeTrend: [], staffByRole: [], attPie: [], revData: [], projDist: [] }
    const { projects, staff, vehicles, ti, te, mr, bu, bt, ea, et, txs, logs, cats, attendance, attStatsData = {}, expenses, pendingExpenses, totalPendingExpenses, invoices, paidInvoices, pendingInvoices, totalPendingInvoiceAmt, maintenanceDue, totalFuel, cashFlowData, expenseTrend, incomeTrend, staffByRole, attPie, revData, projDist } = raw
    const count = (projects || []).length
    const activeStaff = (staff || []).filter(s => s.status !== 'inactive').length
    const totalStaff = (staff || []).length
    const balance = ti - te
    const margin = ti > 0 ? ((balance / ti) * 100).toFixed(1) : "0.0"
    const bpct = bt > 0 ? Math.round((bu / bt) * 100) : 0
    const avgProgress = projects?.length > 0 ? Math.round(projects.reduce((s, p) => s + n(p.progress), 0) / projects.length) : 0
    const staffUtil = activeStaff > 0 ? Math.round((activeStaff / Math.max(activeStaff + 3, 1)) * 100) : 0
    const equipUtil = et > 0 ? Math.round((ea / et) * 100) : 0
    const resourcePct = Math.round((staffUtil + equipUtil) / 2)
    const monthlyTarget = ti > 0 && ti / 12 > 0 ? Math.round((mr / (ti / 12)) * 100) : 0
    const revPct = Math.min(monthlyTarget, 100)
    const featured = projects?.[0] || null
    const activeVehicles = (vehicles || []).filter(v => v.status === 'active' || !v.status).length
    const totalVehicles = (vehicles || []).length
    const maintDueCount = (maintenanceDue || []).length
    const todayAtt = (attendance || []).filter(a => {
      const d = new Date(a.date || a.created_at)
      const today = new Date()
      return d.toDateString() === today.toDateString()
    }).length
    const presentToday = attStatsData.approved || attStatsData.today_present || todayAtt
    const pendingApprovals = attStatsData.pending || 0
    return { count, activeStaff, totalStaff, ti, te, mr, balance, margin, bpct, avgProgress, resourcePct, revPct, featured, projects: (projects || []).slice(0, 4), txs, logs, cats, bu, bt, activeVehicles, totalVehicles, maintDueCount, totalFuel, presentToday, pendingApprovals, pendingExpenses: (pendingExpenses || []).slice(0, 5), totalPendingExpenses, paidInvoices: (paidInvoices || []).length, pendingInvoices: (pendingInvoices || []).slice(0, 5), totalPendingInvoiceAmt, cashFlowData, expenseTrend, incomeTrend, staffByRole, attPie, revData, projDist }
  }, [raw])

  if (loading || !raw) return (
    <div className="db" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <span style={{ fontFamily: 'Inter, system-ui, sans-serif', color: '#94A3B8', fontSize: 13 }}>Loading dashboard…</span>
    </div>
  )

  const { count, activeStaff, totalStaff, ti, te, mr, balance, margin, bpct, avgProgress, resourcePct, revPct, featured, projects, txs, logs, cats, bu, bt, activeVehicles, totalVehicles, maintDueCount, totalFuel, presentToday, pendingApprovals, pendingExpenses, totalPendingExpenses, paidInvoices, pendingInvoices, totalPendingInvoiceAmt, cashFlowData, expenseTrend, incomeTrend, staffByRole, attPie, revData, projDist } = metrics

  return (
    <div className="db">
      <div className="db-inner">
        {/* Row 1: Hero + Activity */}
        <div className="db-g">
          <div className="col-8">
            <HeroCard project={featured} totalIncome={ti} totalExpense={te} balance={balance} margin={margin} />
          </div>
          <div className="col-4">
            <div className="alert-crd">
              <div className="alert-h">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={ORANGE} strokeWidth="2"><path d="M18 20V10" /><path d="M12 20V4" /><path d="M6 20v-6" /></svg>
                <span>Activity Feed</span>
              </div>
              <div className="alert-l">
                {logs.length > 0 ? logs.map((a, i) => (
                  <div key={i} className="alert-i">
                    <div className="alert-d" />
                    <div>
                      <p className="alert-msg">{a.action} {a.entity_type || ''}</p>
                      <p className="alert-t">{ago(a.created_at || a.timestamp)}</p>
                    </div>
                  </div>
                )) : <p style={{ color: '#94A3B8', fontSize: 12, padding: 12, textAlign: 'center' }}>No recent activity</p>}
              </div>
            </div>
          </div>
        </div>

        {/* Row 2: Gauge Cards */}
        <div className="db-g">
          <div className="col-3"><GaugeCard pct={bpct} label="Budget Utilization" sub={`${fmt(bu)} / ${fmt(bt)}`} color={bpct > 80 ? RED : BLUE} /></div>
          <div className="col-3"><GaugeCard pct={avgProgress} label="Project Progress" sub={`${count} projects`} color={GREEN} /></div>
          <div className="col-3"><GaugeCard pct={resourcePct} label="Resource Allocation" sub="Staff & Equipment" color={ORANGE} /></div>
          <div className="col-3"><GaugeCard pct={revPct} label="Revenue Target" sub={`${fmt(mr)} this month`} color={PURPLE} /></div>
        </div>

        {/* Row 3: Staff + Vehicle + Finance Summary */}
        <div className="db-g">
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>👥 Staff Overview</span></div>
              <div className="acrd-body">
                <div className="stat-grid">
                  <StatMini icon="👤" value={totalStaff} label="Total" color={BLUE} />
                  <StatMini icon="✅" value={presentToday} label="Present" color={GREEN} />
                  <StatMini icon="⏳" value={pendingApprovals} label="Approvals" color={ORANGE} />
                  <StatMini icon="📊" value={activeStaff} label="Active" color={PURPLE} />
                </div>
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>🚗 Vehicle Status</span></div>
              <div className="acrd-body">
                <div className="stat-grid">
                  <StatMini icon="🚐" value={activeVehicles} label="Active" color={BLUE} />
                  <StatMini icon="🔧" value={maintDueCount} label="Service Due" color={maintDueCount > 0 ? RED : GREEN} />
                  <StatMini icon="⛽" value={fmt(totalFuel)} label="Fuel Cost" color={ORANGE} />
                  <StatMini icon="📊" value={totalVehicles} label="Fleet" color={PURPLE} />
                </div>
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>💰 Finance Summary</span></div>
              <div className="acrd-body">
                <div className="stat-grid">
                  <StatMini icon="📄" value={paidInvoices} label="Paid" color={GREEN} />
                  <StatMini icon="⏳" value={pendingInvoices.length} label="Pending" color={ORANGE} />
                  <StatMini icon="💸" value={fmt(totalPendingInvoiceAmt)} label="Outstanding" color={RED} />
                  <StatMini icon="📊" value={fmt(balance)} label="Net" color={balance >= 0 ? GREEN : RED} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Row 4: Income vs Expenses + Spending Pie + Attendance Pie */}
        <div className="db-g">
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>Income vs Expenses</span>
                <span className="acrd-badge" style={{ color: GREEN, background: '#10B98112' }}>Net {fmt(balance)}</span>
              </div>
              <div className="acrd-body">
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={[{ n: 'Income', v: ti }, { n: 'Expenses', v: te }]} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                    <XAxis dataKey="n" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                    <YAxis tick={{ fontSize: 9, fill: '#94A3B8' }} tickFormatter={v => `₹${(v / 1e5).toFixed(0)}L`} width={40} />
                    <Tooltip content={<ChartTooltip formatter={v => fmt(v)} />} />
                    <Bar dataKey="v" radius={[4, 4, 0, 0]} barSize={36}>
                      <Cell fill={BLUE} /><Cell fill={ORANGE} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>Spending by Category</span></div>
              <div className="acrd-body" style={{ display: 'flex', alignItems: 'center' }}>
                {cats.length > 0 ? (
                  <>
                    <ResponsiveContainer width="50%" height={150}>
                      <PieChart>
                        <Pie data={cats} cx="50%" cy="50%" outerRadius={55} innerRadius={35} paddingAngle={2} dataKey="value">
                          {cats.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                        </Pie>
                        <Tooltip content={<ChartTooltip formatter={v => fmt(v)} />} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="pie-legend">
                      {cats.slice(0, 5).map((c, i) => (
                        <div key={i} className="pl-i"><span style={{ background: COLORS[i % COLORS.length] }} />{c.name}</div>
                      ))}
                    </div>
                  </>
                ) : <div style={{ flex: 1, textAlign: 'center', color: '#94A3B8', fontSize: 12 }}>No data</div>}
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>Attendance Today</span></div>
              <div className="acrd-body" style={{ display: 'flex', alignItems: 'center' }}>
                {attPie.length > 0 ? (
                  <>
                    <ResponsiveContainer width="50%" height={150}>
                      <PieChart>
                        <Pie data={attPie} cx="50%" cy="50%" outerRadius={55} innerRadius={35} paddingAngle={2} dataKey="value">
                          {attPie.map((_, i) => <Cell key={i} fill={[GREEN, RED, ORANGE, PURPLE][i % 4]} />)}
                        </Pie>
                        <Tooltip content={<ChartTooltip />} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="pie-legend">
                      {attPie.map((c, i) => (
                        <div key={i} className="pl-i"><span style={{ background: [GREEN, RED, ORANGE, PURPLE][i % 4] }} />{c.name} ({c.value})</div>
                      ))}
                    </div>
                  </>
                ) : <div style={{ flex: 1, textAlign: 'center', color: '#94A3B8', fontSize: 12 }}>No attendance data</div>}
              </div>
            </div>
          </div>
        </div>

        {/* Row 5: Revenue Trend + Expense Trend + Cash Flow */}
        <div className="db-g">
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>Revenue Trend</span></div>
              <div className="acrd-body">
                {incomeTrend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={140}>
                    <AreaChart data={incomeTrend} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                      <defs><linearGradient id="gInc" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={GREEN} stopOpacity={0.3} /><stop offset="100%" stopColor={GREEN} stopOpacity={0.02} /></linearGradient></defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#94A3B8' }} tickFormatter={d => d.slice(5)} />
                      <YAxis tick={{ fontSize: 9, fill: '#94A3B8' }} tickFormatter={v => `₹${(v / 1e3).toFixed(0)}K`} width={38} />
                      <Tooltip content={<ChartTooltip formatter={v => fmt(v)} />} />
                      <Area type="monotone" dataKey="amount" stroke={GREEN} fill="url(#gInc)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : <div className="acrd-empty">No data</div>}
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>Expense Trend</span></div>
              <div className="acrd-body">
                {expenseTrend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={140}>
                    <AreaChart data={expenseTrend} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                      <defs><linearGradient id="gExp" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={RED} stopOpacity={0.3} /><stop offset="100%" stopColor={RED} stopOpacity={0.02} /></linearGradient></defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#94A3B8' }} tickFormatter={d => d.slice(5)} />
                      <YAxis tick={{ fontSize: 9, fill: '#94A3B8' }} tickFormatter={v => `₹${(v / 1e3).toFixed(0)}K`} width={38} />
                      <Tooltip content={<ChartTooltip formatter={v => fmt(v)} />} />
                      <Area type="monotone" dataKey="amount" stroke={RED} fill="url(#gExp)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : <div className="acrd-empty">No data</div>}
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>Cash Flow</span></div>
              <div className="acrd-body">
                {cashFlowData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={140}>
                    <BarChart data={cashFlowData.slice(-7)} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#94A3B8' }} />
                      <YAxis tick={{ fontSize: 9, fill: '#94A3B8' }} tickFormatter={v => `₹${(v / 1e3).toFixed(0)}K`} width={38} />
                      <Tooltip content={<ChartTooltip formatter={v => fmt(v)} />} />
                      <Bar dataKey="inflow" fill={GREEN} radius={[3, 3, 0, 0]} barSize={10} />
                      <Bar dataKey="outflow" fill={RED} radius={[3, 3, 0, 0]} barSize={10} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : <div className="acrd-empty">No data</div>}
              </div>
            </div>
          </div>
        </div>

        {/* Row 6: Staff by Role + Project Status + Transactions + Projects */}
        <div className="db-g">
          <div className="col-3">
            <div className="acrd">
              <div className="acrd-h"><span>Staff by Role</span></div>
              <div className="acrd-body" style={{ display: 'flex', alignItems: 'center' }}>
                {staffByRole.length > 0 ? (
                  <>
                    <ResponsiveContainer width="50%" height={130}>
                      <PieChart>
                        <Pie data={staffByRole} cx="50%" cy="50%" outerRadius={48} innerRadius={28} paddingAngle={2} dataKey="value">
                          {staffByRole.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                        </Pie>
                        <Tooltip content={<ChartTooltip />} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="pie-legend">
                      {staffByRole.map((c, i) => (
                        <div key={i} className="pl-i"><span style={{ background: COLORS[i % COLORS.length] }} />{c.name} ({c.value})</div>
                      ))}
                    </div>
                  </>
                ) : <div className="acrd-empty">No staff</div>}
              </div>
            </div>
          </div>
          <div className="col-3">
            <div className="acrd">
              <div className="acrd-h"><span>Project Status</span></div>
              <div className="acrd-body" style={{ display: 'flex', alignItems: 'center' }}>
                {projDist.length > 0 ? (
                  <>
                    <ResponsiveContainer width="50%" height={130}>
                      <PieChart>
                        <Pie data={projDist} cx="50%" cy="50%" outerRadius={48} innerRadius={28} paddingAngle={2} dataKey="value">
                          {projDist.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                        </Pie>
                        <Tooltip content={<ChartTooltip />} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="pie-legend">
                      {projDist.map((c, i) => (
                        <div key={i} className="pl-i"><span style={{ background: COLORS[i % COLORS.length] }} />{c.name} ({c.value})</div>
                      ))}
                    </div>
                  </>
                ) : <div className="acrd-empty">No projects</div>}
              </div>
            </div>
          </div>
          <div className="col-3">
            <div className="acrd">
              <div className="acrd-h"><span>Recent Transactions</span></div>
              {txs.length > 0 ? (
                <div className="tx-tbl">
                  <div className="tx-th"><span>Date</span><span>Category</span><span style={{ textAlign: 'right' }}>Amount</span></div>
                  {txs.slice(0, 5).map((t, i) => (
                    <div key={i} className="tx-tr">
                      <span className="tx-td">{t.date || '—'}</span>
                      <span className="tx-tc"><span className={`tx-dot ${t.type}`} />{t.category || '—'}</span>
                      <span className={`tx-ta ${t.type}`}>{t.type === 'income' ? '+' : '-'}{fmt(t.amount)}</span>
                    </div>
                  ))}
                </div>
              ) : <div className="acrd-empty">No transactions</div>}
            </div>
          </div>
          <div className="col-3">
            <div className="acrd">
              <div className="acrd-h"><span>Active Projects</span></div>
              {projects.length > 0 ? (
                <div className="proj-tbl">
                  {projects.map((p, i) => (
                    <div key={i} className="proj-tr">
                      <div className="proj-tl">
                        <span className="proj-tn">{p.name}</span>
                        <span className="proj-ts" style={{
                          color: p.status === 'active' || p.status === 'in_progress' ? GREEN : p.status === 'pending' ? ORANGE : '#94A3B8',
                          background: (p.status === 'active' || p.status === 'in_progress' ? GREEN : p.status === 'pending' ? ORANGE : '#94A3B8') + '15'
                        }}>{(p.status || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                      </div>
                      <div className="proj-tbar"><div className="proj-tbf" style={{ width: `${p.progress}%` }} /></div>
                    </div>
                  ))}
                </div>
              ) : <div className="acrd-empty">No projects</div>}
            </div>
          </div>
        </div>

        {/* Row 7: Pending Items + Maintenance */}
        <div className="db-g" style={{ marginBottom: 0 }}>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>Pending Expenses</span>
                {totalPendingExpenses > 0 && <span className="acrd-badge" style={{ color: ORANGE, background: '#F59E0B12' }}>{fmt(totalPendingExpenses)}</span>}
              </div>
              {pendingExpenses.length > 0 ? (
                <div className="tx-tbl">
                  <div className="tx-th"><span>Staff</span><span>Category</span><span style={{ textAlign: 'right' }}>Amount</span></div>
                  {pendingExpenses.map((e, i) => (
                    <div key={i} className="tx-tr">
                      <span className="tx-td">{e.staff_name || e.staff?.name || '—'}</span>
                      <span className="tx-tc"><span className="tx-dot expense" />{e.category || '—'}</span>
                      <span className="tx-ta expense">{fmt(e.amount)}</span>
                    </div>
                  ))}
                </div>
              ) : <div className="acrd-empty">No pending expenses</div>}
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>Pending Invoices</span>
                {totalPendingInvoiceAmt > 0 && <span className="acrd-badge" style={{ color: RED, background: '#EF444412' }}>{fmt(totalPendingInvoiceAmt)}</span>}
              </div>
              {pendingInvoices.length > 0 ? (
                <div className="tx-tbl">
                  <div className="tx-th"><span>Client</span><span>Project</span><span style={{ textAlign: 'right' }}>Amount</span></div>
                  {pendingInvoices.map((inv, i) => (
                    <div key={i} className="tx-tr">
                      <span className="tx-td">{inv.client_name || inv.client?.name || '—'}</span>
                      <span className="tx-tc">{inv.project_name || inv.project?.name || '—'}</span>
                      <span className="tx-ta expense">{fmt(inv.total_amount || inv.amount)}</span>
                    </div>
                  ))}
                </div>
              ) : <div className="acrd-empty">All invoices paid</div>}
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h"><span>🔧 Maintenance Alerts</span></div>
              <div className="acrd-body">
                {maintDueCount > 0 ? (
                  <div className="tx-tbl">
                    <div className="tx-th"><span>Vehicle</span><span>Type</span><span style={{ textAlign: 'right' }}>Due</span></div>
                    {(raw.maintenanceDue || []).slice(0, 4).map((m, i) => (
                      <div key={i} className="tx-tr">
                        <span className="tx-td">{m.vehicle_name || m.make || '—'}</span>
                        <span className="tx-tc"><span className="tx-dot expense" />{m.maintenance_type || m.type || 'Service'}</span>
                        <span className="tx-ta expense">{m.due_date || m.next_due || '—'}</span>
                      </div>
                    ))}
                  </div>
                ) : <div className="acrd-empty" style={{ color: GREEN }}>✓ All vehicles maintained</div>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
