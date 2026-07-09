import { useState, useEffect, useMemo } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import api from "../../api/api"
import { useToast } from "../../components/Toast"
import "../../styles/Dashboard.css"

const BLUE = "#3B82F6"
const ORANGE = "#F59E0B"
const GREEN = "#10B981"
const RED = "#EF4444"
const PURPLE = "#8B5CF6"
const COLORS = [BLUE, GREEN, ORANGE, RED, PURPLE, "#06B6D4", "#EC4899"]

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

function Gauge({ pct, color = BLUE, size = 104 }) {
  const s = 6, r = (size - s) / 2, c = Math.PI * r, off = c * (1 - Math.min(Math.max(pct, 0), 100) / 100)
  const cx = size / 2, cy = size / 2
  return (
    <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
      <path d={`M ${s / 2} ${cy} A ${r} ${r} 0 0 1 ${size - s / 2} ${cy}`} fill="none" stroke="#E8EDF2" strokeWidth={s} strokeLinecap="round" />
      <path d={`M ${s / 2} ${cy} A ${r} ${r} 0 0 1 ${size - s / 2} ${cy}`} fill="none" stroke={color} strokeWidth={s} strokeLinecap="round" strokeDasharray={c} strokeDashoffset={off} />
      <text x={cx} y={cy + 4} textAnchor="middle" fontSize={20} fontWeight={700} fill="#1E293B" fontFamily="Inter,system-ui,sans-serif">
        {Math.round(pct)}<tspan fontSize={11} fill="#94A3B8">%</tspan>
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
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>
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
      <Gauge pct={pct} color={color} size={100} />
      <div className="gcrd-l">{label}</div>
      <div className="gcrd-s">{sub}</div>
    </div>
  )
}

export default function Dashboard() {
  const { showError } = useToast()
  const [loading, setLoading] = useState(true)
  const [raw, setRaw] = useState({})

  useEffect(() => {
    async function load() {
      setLoading(true)
      const ok = r => r?.data?.success && r?.data?.data
      const ar = r => ok(r) ? (Array.isArray(r.data.data) ? r.data.data : (r.data.data.items || [])) : []
      const w = p => p.then(r => r).catch(() => ({ data: { success: false, data: null } }))
      try {
        const [pr, sr, vr, fr, br, er, lr, tr, att, attStats, exp, inv, maint, cashFlow] = await Promise.all([
          w(api.get('/api/projects?per_page=100')), w(api.get('/api/staff?per_page=100')),
          w(api.get('/api/vehicles?per_page=100')), w(api.get('/api/finance/summary')),
          w(api.get('/api/finance/budgets?per_page=50')), w(api.get('/api/equipment/stats')),
          w(api.get('/api/admin/activity-logs?per_page=10')), w(api.get('/api/finance/transactions?per_page=10')),
          w(api.get('/api/attendance?per_page=100')), w(api.get('/api/attendance/approvals/stats')),
          w(api.get('/api/staff/expenses?per_page=50')), w(api.get('/api/finance/invoices?per_page=20')),
          w(api.get('/api/vehicles/maintenance-due')), w(api.get('/api/finance/reports/cash-flow')),
        ])
        const projects = ar(pr), staff = ar(sr), vehicles = ar(vr), budgets = ar(br)
        const txs = ar(tr).slice(0, 6), logs = ar(lr).slice(0, 6)
        const attendance = ar(att), expenses = ar(exp), invoices = ar(inv)
        const maintenanceDue = ar(maint)

        let ti = 0, te = 0
        if (ok(fr)) { ti = n(fr.data.data.total_income); te = n(fr.data.data.total_expense) }

        let mr = 0
        try { const dr = await api.get('/api/dashboard'); if (ok(dr)) mr = n(dr.data.data.monthlyRevenue) } catch {}

        let bu = 0, bt = 0
        budgets.forEach(b => { bt += n(b.allocated_amount || b.budget_amount); bu += n(b.used_amount) })

        let ea = 0, et = 0
        if (ok(er)) { et = n(er.data.data.total); ea = n(er.data.data.active || er.data.data.available) }

        let cats = []
        try {
          const all = await api.get('/api/finance/transactions?per_page=500')
          const a = ar(all); const m = {}
          a.forEach(x => { const c = x.category || 'Other'; m[c] = (m[c] || 0) + Math.abs(n(x.amount)) })
          cats = Object.entries(m).map(([n, v]) => ({ name: n, value: v })).sort((a, b) => b.value - a.value).slice(0, 6)
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

        setRaw({ projects, staff, vehicles, ti, te, mr, bu, bt, ea, et, txs, logs, cats, attendance, attStatsData, expenses, pendingExpenses, totalPendingExpenses, invoices, paidInvoices, pendingInvoices, totalPendingInvoiceAmt, maintenanceDue, totalFuel, cashFlowData })
      } catch { showError('Failed to load') }
      setLoading(false)
    }
    load()
  }, [])

  const metrics = useMemo(() => {
    const { projects, staff, vehicles, ti, te, mr, bu, bt, ea, et, txs, logs, cats, attendance, attStatsData = {}, expenses, pendingExpenses, totalPendingExpenses, invoices, paidInvoices, pendingInvoices, totalPendingInvoiceAmt, maintenanceDue, totalFuel, cashFlowData } = raw || {}
    if (!projects && !staff && !vehicles) return { count: 0, activeStaff: 0, totalStaff: 0, ti: 0, te: 0, mr: 0, balance: 0, margin: "0.0", bpct: 0, avgProgress: 0, resourcePct: 0, revPct: 0, featured: null, projects: [], txs: [], logs: [], cats: [], bu: 0, bt: 0, activeVehicles: 0, totalVehicles: 0, maintDueCount: 0, totalFuel: 0, presentToday: 0, pendingApprovals: 0, pendingExpenses: [], totalPendingExpenses: 0, paidInvoices: 0, pendingInvoices: [], totalPendingInvoiceAmt: 0, cashFlowData: [] }
    const count = n(projects?.length)
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

    return { count, activeStaff, totalStaff, ti, te, mr, balance, margin, bpct, avgProgress, resourcePct, revPct, featured, projects: projects?.slice(0, 4) || [], txs, logs, cats, bu, bt, activeVehicles, totalVehicles, maintDueCount, totalFuel, presentToday, pendingApprovals, pendingExpenses: pendingExpenses?.slice(0, 5) || [], totalPendingExpenses, paidInvoices: paidInvoices?.length || 0, pendingInvoices: pendingInvoices?.slice(0, 5) || [], totalPendingInvoiceAmt, cashFlowData }
  }, [raw])

  if (loading) return (
    <div className="db" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
      <span style={{ fontFamily: 'Inter, system-ui, sans-serif', color: '#94A3B8', fontSize: 14 }}>Loading dashboard…</span>
    </div>
  )

  const { count, activeStaff, totalStaff, ti, te, mr, balance, margin, bpct, avgProgress, resourcePct, revPct, featured, projects, txs, logs, cats, bu, bt, activeVehicles, totalVehicles, maintDueCount, totalFuel, presentToday, pendingApprovals, pendingExpenses, totalPendingExpenses, paidInvoices, pendingInvoices, totalPendingInvoiceAmt, cashFlowData } = metrics

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
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={ORANGE} strokeWidth="2"><path d="M18 20V10" /><path d="M12 20V4" /><path d="M6 20v-6" /></svg>
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
                )) : <p style={{ color: '#94A3B8', fontSize: 13, padding: 16, textAlign: 'center' }}>No recent activity</p>}
              </div>
              <button className="alert-btn">View All Activity →</button>
            </div>
          </div>
        </div>

        {/* Row 2: Gauge Cards */}
        <div className="db-g">
          <div className="col-3">
            <GaugeCard pct={bpct} label="Budget Utilization" sub={`${fmt(bu)} / ${fmt(bt)}`} color={bpct > 80 ? RED : BLUE} />
          </div>
          <div className="col-3">
            <GaugeCard pct={avgProgress} label="Project Progress" sub={`${count} projects`} color={GREEN} />
          </div>
          <div className="col-3">
            <GaugeCard pct={resourcePct} label="Resource Allocation" sub="Staff & Equipment" color={ORANGE} />
          </div>
          <div className="col-3">
            <GaugeCard pct={revPct} label="Revenue Target" sub={`${fmt(mr)} this month`} color={PURPLE} />
          </div>
        </div>

        {/* Row 3: Staff + Vehicle + Finance Summary */}
        <div className="db-g">
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>👥 Staff Overview</span>
              </div>
              <div className="acrd-body">
                <div className="stat-grid">
                  <StatMini icon="👤" value={totalStaff} label="Total Staff" color={BLUE} />
                  <StatMini icon="✅" value={presentToday} label="Present Today" color={GREEN} />
                  <StatMini icon="⏳" value={pendingApprovals} label="Pending Approvals" color={ORANGE} />
                  <StatMini icon="📊" value={`${activeStaff}`} label="Active Staff" color={PURPLE} />
                </div>
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>🚗 Vehicle Status</span>
              </div>
              <div className="acrd-body">
                <div className="stat-grid">
                  <StatMini icon="🚐" value={activeVehicles} label="Active Vehicles" color={BLUE} />
                  <StatMini icon="🔧" value={maintDueCount} label="Maintenance Due" color={maintDueCount > 0 ? RED : GREEN} />
                  <StatMini icon="⛽" value={fmt(totalFuel)} label="Total Fuel Cost" color={ORANGE} />
                  <StatMini icon="📊" value={totalVehicles} label="Total Fleet" color={PURPLE} />
                </div>
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>💰 Finance Summary</span>
              </div>
              <div className="acrd-body">
                <div className="stat-grid">
                  <StatMini icon="📄" value={paidInvoices} label="Paid Invoices" color={GREEN} />
                  <StatMini icon="⏳" value={pendingInvoices.length} label="Pending Invoices" color={ORANGE} />
                  <StatMini icon="💸" value={fmt(totalPendingInvoiceAmt)} label="Outstanding" color={RED} />
                  <StatMini icon="📊" value={fmt(balance)} label="Net Profit" color={balance >= 0 ? GREEN : RED} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Row 4: Charts */}
        <div className="db-g">
          <div className="col-6">
            <div className="acrd">
              <div className="acrd-h">
                <span>Income vs Expenses</span>
                <span className="acrd-badge" style={{ color: GREEN, background: '#10B98112' }}>Net {fmt(balance)}</span>
              </div>
              <div className="acrd-body">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={[{ n: 'Income', v: ti }, { n: 'Expenses', v: te }]} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                    <XAxis dataKey="n" tick={{ fontSize: 12, fill: '#94A3B8', fontFamily: 'Inter,system-ui,sans-serif' }} />
                    <YAxis tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Inter,system-ui,sans-serif' }} tickFormatter={v => `₹${(v / 1e5).toFixed(0)}L`} width={45} />
                    <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', fontFamily: 'Inter,system-ui,sans-serif', fontSize: 12 }} formatter={v => [fmt(v), 'Amount']} />
                    <Bar dataKey="v" radius={[6, 6, 0, 0]} barSize={50}>
                      <Cell fill={BLUE} /><Cell fill={ORANGE} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="acrd-f">
                <span><span style={{ color: BLUE }}>●</span> Income: {fmt(ti)}</span>
                <span><span style={{ color: ORANGE }}>●</span> Expenses: {fmt(te)}</span>
                <span><span style={{ color: balance >= 0 ? GREEN : RED }}>●</span> Profit: {fmt(balance)}</span>
              </div>
            </div>
          </div>
          <div className="col-6">
            <div className="acrd">
              <div className="acrd-h">
                <span>Spending by Category</span>
              </div>
              <div className="acrd-body" style={{ display: 'flex', alignItems: 'center' }}>
                {cats.length > 0 ? (
                  <>
                    <ResponsiveContainer width="55%" height={200}>
                      <PieChart>
                        <Pie data={cats} cx="50%" cy="50%" outerRadius={72} innerRadius={48} paddingAngle={3} dataKey="value">
                          {cats.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                        </Pie>
                        <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', fontFamily: 'Inter,system-ui,sans-serif', fontSize: 12 }} formatter={v => [fmt(v), 'Amount']} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="pie-legend">
                      {cats.map((c, i) => (
                        <div key={i} className="pl-i"><span style={{ background: COLORS[i % COLORS.length] }} />{c.name}</div>
                      ))}
                    </div>
                  </>
                ) : <div style={{ flex: 1, textAlign: 'center', color: '#94A3B8', fontSize: 13 }}>No transaction data</div>}
              </div>
            </div>
          </div>
        </div>

        {/* Row 5: Transactions + Projects + Pending Expenses */}
        <div className="db-g">
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>Recent Transactions</span>
              </div>
              {txs.length > 0 ? (
                <div className="tx-tbl">
                  <div className="tx-th"><span>Date</span><span>Category</span><span style={{ textAlign: 'right' }}>Amount</span></div>
                  {txs.map((t, i) => (
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
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>Active Projects</span>
              </div>
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
                      <span className="proj-tp">{p.progress}%</span>
                    </div>
                  ))}
                </div>
              ) : <div className="acrd-empty">No projects</div>}
            </div>
          </div>
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
        </div>

        {/* Row 6: Pending Invoices + Cash Flow + Maintenance */}
        <div className="db-g" style={{ marginBottom: 0 }}>
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
              <div className="acrd-h">
                <span>Cash Flow</span>
              </div>
              <div className="acrd-body">
                {cashFlowData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={cashFlowData.slice(-7)} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                      <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} tickFormatter={v => `₹${(v / 1e3).toFixed(0)}K`} width={40} />
                      <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', fontSize: 12 }} formatter={v => [fmt(v), 'Amount']} />
                      <Bar dataKey="inflow" fill={GREEN} radius={[4, 4, 0, 0]} barSize={16} />
                      <Bar dataKey="outflow" fill={RED} radius={[4, 4, 0, 0]} barSize={16} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : <div className="acrd-empty">No cash flow data</div>}
              </div>
            </div>
          </div>
          <div className="col-4">
            <div className="acrd">
              <div className="acrd-h">
                <span>🔧 Maintenance Alerts</span>
              </div>
              <div className="acrd-body">
                {maintDueCount > 0 ? (
                  <div className="tx-tbl">
                    <div className="tx-th"><span>Vehicle</span><span>Type</span><span style={{ textAlign: 'right' }}>Due</span></div>
                    {(raw.maintenanceDue || []).slice(0, 5).map((m, i) => (
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
