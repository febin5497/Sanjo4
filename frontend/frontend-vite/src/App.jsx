import { useEffect, Suspense, lazy } from "react"

import TopNavigation from "./components/TopNavigation"
import Navbar from "./components/Navbar"
import ProtectedRoute from "./components/ProtectedRoute"
import ErrorBoundary from "./components/ErrorBoundary"
import { ToastProvider } from "./components/Toast"
import "./styles/mobile-utilities.css"

import Login from "./pages/auth/Login"
import Register from "./pages/auth/Register"
import ChangePasswordFirstLogin from "./pages/auth/ChangePasswordFirstLogin"

import Dashboard from "./pages/dashboard/Dashboard"
import Projects from "./pages/projects/Projects"
import ProjectForm from "./pages/projects/ProjectForm"
import ProjectDetails from "./pages/projects/ProjectDetails"
import Staff from "./pages/staff/Staff"
import Vehicles from "./pages/vehicles/Vehicles"
import VehicleAllocationPage from "./pages/vehicles/VehicleAllocationPage"
import Materials from "./pages/materials/Materials"
import Finance from "./pages/finance/Finance"
import AddTransaction from "./pages/transactions/AddTransaction"
import Documents from "./pages/documents/Documents"
import Invoices from "./pages/invoices/Invoices"
import ProjectMap from "./pages/projects/ProjectMap"
import AttendanceUnified from "./pages/attendance/AttendanceUnified"
import AttendanceReport from "./pages/attendance/AttendanceReport"
import AttendancePhotoApprovals from "./pages/attendance/AttendancePhotoApprovals"
import ProjectProgress from "./pages/projects/ProjectProgress"
import MaterialUsage from "./pages/materials/MaterialUsage"
import GanttPlanner from "./pages/projects/GanttPlanner"
import ProjectCost from "./pages/projects/ProjectCost"
import SitePhotos from "./pages/projects/SitePhotos"
import ProjectAssignmentManager from "./pages/projects/ProjectAssignmentManager"
import ProjectTasks from "./pages/projects/ProjectTasks"
import Profile from "./pages/profile/Profile"
import Settings from "./pages/profile/Settings"
import RoleRoute from "./components/RoleRoute"
import Suppliers from "./pages/procurement/Suppliers"
import Purchases from "./pages/procurement/Purchases"
import PurchaseReturns from "./pages/procurement/PurchaseReturns"
import Sales from "./pages/sales/Sales"
import SalesReturns from "./pages/sales/SalesReturns"
import AdminDashboard from "./pages/admin/AdminDashboard"
import Users from "./pages/admin/Users"
import Roles from "./pages/admin/Roles"
import ActivityLogs from "./pages/admin/ActivityLogs"
import CompanySettings from "./pages/admin/CompanySettings"
import ExpenseList from "./pages/staff/ExpenseList"
import ExpenseApprovalsPage from "./pages/staff/ExpenseApprovalsPage"
import PendingApprovalsPage from "./pages/staff/PendingApprovalsPage"
import BudgetPage from "./pages/finance/BudgetPage"
import IndentPage from "./pages/procurement/IndentPage"
import GRNPage from "./pages/procurement/GRNPage"
import ProcurementPipelinePage from "./pages/procurement/ProcurementPipelinePage"
import ChartOfAccountsPage from "./pages/finance/ChartOfAccountsPage"
import ReportsPage from "./pages/reports/ReportsPage"
import ProjectProfitabilityReport from "./pages/finance/ProjectProfitabilityReport"
import CostVsBudgetReport from "./pages/finance/CostVsBudgetReport"
import CashFlowReport from "./pages/finance/CashFlowReport"
import ReceivablesAgingReport from "./pages/finance/ReceivablesAgingReport"
import StagesPage from "./pages/projects/StagesPage"
import StageBillingPage from "./pages/finance/StageBillingPage"
import RetentionTrackingPage from "./pages/finance/RetentionTrackingPage"
import PayrollCyclePage from "./pages/staff/PayrollCyclePage"
import VendorManagementPage from "./pages/procurement/VendorManagementPage"
import Reports from "./pages/reports/Reports"
import MobileDashboard from "./pages/dashboard/MobileDashboard"
import Store from "./pages/inventory/Store"
import Estimates from "./pages/quotes/Estimates"
const PlanViewer3D = lazy(() => import("./pages/plan-viewer/PlanViewer3D"))
// import EquipmentList from "./pages/equipment/EquipmentList"
// import EquipmentForm from "./pages/equipment/EquipmentForm"
// import EquipmentDetail from "./pages/equipment/EquipmentDetail"
// import QuoteList from "./pages/quotes/QuoteList"
// import QuoteForm from "./pages/quotes/QuoteForm"
// import QuoteDetail from "./pages/quotes/QuoteDetail"
import QuoteTemplate from "./pages/quotes/QuoteTemplate"

import { Routes, Route, useLocation, Navigate } from "react-router-dom"

function App() {

    const location = useLocation()
    const isAuthPage = location.pathname === "/login" || location.pathname === "/register" || location.pathname === "/change-password-first-login"
    const isDashboard = location.pathname === "/dashboard"

    // Reset all dropdowns and form states when user navigates to a different page
    useEffect(() => {
        // Clear any open dropdowns or modals when navigating
        const allSelects = document.querySelectorAll('select');
        allSelects.forEach(select => {
            select.value = select.options[0]?.value || '';
            // Trigger change event for React state updates
            select.dispatchEvent(new Event('change', { bubbles: true }));
        });

        // Close any open modals
        const modals = document.querySelectorAll('[role="dialog"], .modal-overlay');
        modals.forEach(modal => {
            if (modal.style && modal.style.display !== 'none') {
                modal.style.display = 'none';
            }
        });

        // Scroll to top
        window.scrollTo(0, 0);
    }, [location.pathname])

    return (
        <ErrorBoundary>
            <ToastProvider>
                <div style={{display: "flex", flexDirection: "column", height: "100vh", width: "100vw", margin: 0, padding: 0}}>

                {/* Top Navigation */}
                {!isAuthPage && <TopNavigation />}

            <div
                className="flex-1 flex flex-col"
                style={{
                    backgroundColor: "var(--bg-tertiary)",
                    minHeight: 0,
                    overflow: "hidden"
                }}
            >

                <div className="flex-1 p-4" style={{minHeight: 0, overflow: isDashboard ? "hidden" : "auto", overflowX: "auto"}}>

                    <Routes>

                        {/* PUBLIC */}
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/change-password-first-login" element={<ChangePasswordFirstLogin />} />

                        {/* PROTECTED */}

                        <Route path="/" element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        } />

                        <Route path="/dashboard" element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        } />

                        <Route path="/projects" element={
                            <ProtectedRoute>
                                <Projects />
                            </ProtectedRoute>
                        } />
                        <Route path="/projects/new" element={
                            <ProtectedRoute>
                                <ProjectForm />
                            </ProtectedRoute>
                        } />
                        <Route path="/projects/:id" element={
                            <ProtectedRoute>
                                <ProjectDetails />
                            </ProtectedRoute>
                        } />
                        <Route path="/projects/:id/edit" element={
                            <ProtectedRoute>
                                <ProjectForm />
                            </ProtectedRoute>
                        } />

                        <Route path="/projects/assignment-manager" element={
                            <ProtectedRoute>
                                <ProjectAssignmentManager />
                            </ProtectedRoute>
                        } />

                        <Route path="/projects/:projectId/tasks" element={
                            <ProtectedRoute>
                                <ProjectTasks />
                            </ProtectedRoute>
                        } />

                        <Route path="/staff" element={
                            <ProtectedRoute>
                                <Staff />
                            </ProtectedRoute>
                        } />

                        <Route path="/vehicles" element={
                            <ProtectedRoute>
                                <Vehicles />
                            </ProtectedRoute>
                        } />

                        <Route path="/vehicles/allocation" element={
                            <ProtectedRoute>
                                <VehicleAllocationPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/materials" element={
                            <ProtectedRoute>
                                <Materials />
                            </ProtectedRoute>
                        } />

                        <Route path="/finance" element={
                            <ProtectedRoute>
                                <Finance />
                            </ProtectedRoute>
                        } />

                        <Route path="/finance/add" element={
                            <ProtectedRoute>
                                <AddTransaction />
                            </ProtectedRoute>
                        } />

                        <Route path="/finance/transactions" element={
                            <ProtectedRoute>
                                <Navigate to="/finance" replace />
                            </ProtectedRoute>
                        } />

                        <Route path="/finance/pending-approvals" element={
                            <ProtectedRoute>
                                <PendingApprovalsPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/budgets" element={
                            <ProtectedRoute>
                                <BudgetPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/indents" element={
                            <ProtectedRoute>
                                <IndentPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/grns" element={
                            <ProtectedRoute>
                                <GRNPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/procurement-pipeline" element={
                            <ProtectedRoute>
                                <ProcurementPipelinePage />
                            </ProtectedRoute>
                        } />

                        <Route path="/chart-of-accounts" element={
                            <ProtectedRoute>
                                <ChartOfAccountsPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/finance/approvals" element={
                            <ProtectedRoute>
                                <ExpenseApprovalsPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/reports" element={
                            <ProtectedRoute>
                                <ReportsPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/reports/profitability" element={
                            <ProtectedRoute>
                                <ProjectProfitabilityReport />
                            </ProtectedRoute>
                        } />

                        <Route path="/reports/budget-variance" element={
                            <ProtectedRoute>
                                <CostVsBudgetReport />
                            </ProtectedRoute>
                        } />

                        <Route path="/reports/cash-flow" element={
                            <ProtectedRoute>
                                <CashFlowReport />
                            </ProtectedRoute>
                        } />

                        <Route path="/reports/receivables-aging" element={
                            <ProtectedRoute>
                                <ReceivablesAgingReport />
                            </ProtectedRoute>
                        } />

                        <Route path="/projects/:projectId/stages" element={
                            <ProtectedRoute>
                                <StagesPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/stage-billing" element={
                            <ProtectedRoute>
                                <StageBillingPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/retention-tracking" element={
                            <ProtectedRoute>
                                <RetentionTrackingPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/payroll" element={
                            <ProtectedRoute>
                                <PayrollCyclePage />
                            </ProtectedRoute>
                        } />

                        <Route path="/vendors" element={
                            <ProtectedRoute>
                                <VendorManagementPage />
                            </ProtectedRoute>
                        } />

                        <Route path="/documents" element={
                            <ProtectedRoute>
                                <Documents />
                            </ProtectedRoute>
                        } />

                        <Route path="/invoices" element={
                            <ProtectedRoute>
                                <Invoices />
                            </ProtectedRoute>
                        } />

                        <Route path="/map" element={
                            <ProtectedRoute>
                                <ProjectMap />
                            </ProtectedRoute>
                        } />

                        <Route path="/plan-viewer" element={
                            <ProtectedRoute>
                                <Suspense fallback={
                                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh', color: 'var(--text-muted)', fontSize: '16px' }}>
                                        Loading 3D Viewer...
                                    </div>
                                }>
                                    <PlanViewer3D />
                                </Suspense>
                            </ProtectedRoute>
                        } />

                        <Route path="/attendance/unified" element={
                            <ProtectedRoute>
                                <AttendanceUnified />
                            </ProtectedRoute>
                        } />

                        <Route path="/attendance/report" element={
                            <ProtectedRoute>
                                <AttendanceReport />
                            </ProtectedRoute>
                        } />

                        <Route path="/attendance/approvals" element={
                            <ProtectedRoute>
                                <AttendancePhotoApprovals />
                            </ProtectedRoute>
                        } />

                        <Route path="/progress" element={
                            <ProtectedRoute>
                                <ProjectProgress />
                            </ProtectedRoute>
                        } />

                        <Route path="/material-usage" element={
                            <ProtectedRoute>
                                <MaterialUsage />
                            </ProtectedRoute>
                        } />

                        <Route path="/planner" element={
                            <ProtectedRoute>
                                <GanttPlanner />
                            </ProtectedRoute>
                        } />

                        <Route path="/project-cost" element={
                            <ProtectedRoute>
                                <ProjectCost />
                            </ProtectedRoute>
                        } />

                        <Route path="/site-photos" element={
                            <ProtectedRoute>
                                <SitePhotos />
                            </ProtectedRoute>
                        } />

                        <Route path="/profile" element={
                            <ProtectedRoute>
                                <Profile />
                            </ProtectedRoute>
                        } />

                        <Route path="/settings" element={
                            <ProtectedRoute>
                                <Settings />
                            </ProtectedRoute>
                        } />

                        {/* Inventory Management Routes */}
                        <Route path="/suppliers" element={
                            <ProtectedRoute>
                                <Suppliers />
                            </ProtectedRoute>
                        } />

                        <Route path="/purchases" element={
                            <ProtectedRoute>
                                <Purchases />
                            </ProtectedRoute>
                        } />

                        <Route path="/purchase-returns" element={
                            <ProtectedRoute>
                                <PurchaseReturns />
                            </ProtectedRoute>
                        } />

                        <Route path="/sales" element={
                            <ProtectedRoute>
                                <Sales />
                            </ProtectedRoute>
                        } />

                        <Route path="/sales-returns" element={
                            <ProtectedRoute>
                                <SalesReturns />
                            </ProtectedRoute>
                        } />

                        {/* Equipment Management Routes */}
                        {/* <Route path="/equipment" element={
                            <ProtectedRoute>
                                <EquipmentList />
                            </ProtectedRoute>
                        } />

                        <Route path="/equipment/new" element={
                            <ProtectedRoute>
                                <EquipmentForm />
                            </ProtectedRoute>
                        } />

                        <Route path="/equipment/:id" element={
                            <ProtectedRoute>
                                <EquipmentDetail />
                            </ProtectedRoute>
                        } />

                        <Route path="/equipment/:id/edit" element={
                            <ProtectedRoute>
                                <EquipmentForm />
                            </ProtectedRoute>
                        } /> */}

                        {/* Quotation Management Routes */}
                        {/* <Route path="/quotes" element={
                            <ProtectedRoute>
                                <QuoteList />
                            </ProtectedRoute>
                        } />

                        <Route path="/quotes/new" element={
                            <ProtectedRoute>
                                <QuoteForm />
                            </ProtectedRoute>
                        } />

                        <Route path="/quotes/:id" element={
                            <ProtectedRoute>
                                <QuoteDetail />
                            </ProtectedRoute>
                        } />

                        <Route path="/quotes/:id/edit" element={
                            <ProtectedRoute>
                                <QuoteForm />
                            </ProtectedRoute>
                        } /> */}

                        <Route path="/quote-templates" element={
                            <ProtectedRoute>
                                <QuoteTemplate />
                            </ProtectedRoute>
                        } />

                        {/* Administration Routes */}
                        <Route path="/admin/dashboard" element={
                            <ProtectedRoute>
                                <AdminDashboard />
                            </ProtectedRoute>
                        } />

                        <Route path="/admin/users" element={
                            <ProtectedRoute>
                                <Users />
                            </ProtectedRoute>
                        } />

                        <Route path="/admin/roles" element={
                            <ProtectedRoute>
                                <Roles />
                            </ProtectedRoute>
                        } />

                        <Route path="/admin/activity-logs" element={
                            <ProtectedRoute>
                                <ActivityLogs />
                            </ProtectedRoute>
                        } />

                        <Route path="/admin/company-settings" element={
                            <ProtectedRoute>
                                <CompanySettings />
                            </ProtectedRoute>
                        } />

                        {/* New Modules Routes */}
                        <Route path="/staff/expenses" element={
                            <ProtectedRoute>
                                <ExpenseList />
                            </ProtectedRoute>
                        } />

                        <Route path="/store" element={
                            <ProtectedRoute>
                                <Store />
                            </ProtectedRoute>
                        } />

                        <Route path="/estimates" element={
                            <ProtectedRoute>
                                <Estimates />
                            </ProtectedRoute>
                        } />

                        <Route path="/reports" element={
                            <ProtectedRoute>
                                <Reports />
                            </ProtectedRoute>
                        } />

                        <Route path="/mobile-dashboard" element={
                            <ProtectedRoute>
                                <MobileDashboard />
                            </ProtectedRoute>
                        } />

                    </Routes>

                </div>

            </div>

            </div>
            </ToastProvider>
        </ErrorBoundary>

    )
}

export default App