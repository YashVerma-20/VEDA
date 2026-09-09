import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import AppShell from './components/layout/AppShell';
import RoleGuard from './components/ui/RoleGuard';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import FleetDashboard from './pages/FleetDashboard';
import VehiclesPage from './pages/VehiclesPage';
import VehicleDashboard from './pages/VehicleDashboard';
import HistoryPage from './pages/HistoryPage';

// Placeholder Pages for uncompleted routes
const AgentsPage = () => <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}><h2 className="text-accent">AGENT ORCHESTRATION PIPELINE</h2><p className="text-secondary">Administrative view of internal agent communications.</p></div>;
const AdminPage = () => <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}><h2 className="text-danger">SYSTEM ADMINISTRATION</h2><p className="text-secondary">Global configurations and user management.</p></div>;

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected Routes Wrapper */}
            <Route element={<AppShell><Outlet /></AppShell>}>
              {/* Shared Admin & Maintainer */}
              <Route path="/vehicles" element={<RoleGuard allowedRoles={['ADMIN', 'MAINTAINER']}><VehiclesPage /></RoleGuard>} />
              <Route path="/vehicle/:vehicleId" element={<RoleGuard allowedRoles={['ADMIN', 'MAINTAINER']}><VehicleDashboard /></RoleGuard>} />
              <Route path="/history" element={<RoleGuard allowedRoles={['ADMIN', 'MAINTAINER']}><HistoryPage /></RoleGuard>} />
              
              {/* Admin Only */}
              <Route path="/dashboard" element={<RoleGuard allowedRoles={['ADMIN']}><FleetDashboard /></RoleGuard>} />
              <Route path="/fleet" element={<RoleGuard allowedRoles={['ADMIN']}><FleetDashboard /></RoleGuard>} />
              <Route path="/agents" element={<RoleGuard allowedRoles={['ADMIN']}><AgentsPage /></RoleGuard>} />
              <Route path="/admin" element={<RoleGuard allowedRoles={['ADMIN']}><AdminPage /></RoleGuard>} />

              <Route path="*" element={<Navigate to="/vehicles" replace />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
