import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth, Role } from '../../contexts/AuthContext';

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles: Role[];
}

const RoleGuard: React.FC<RoleGuardProps> = ({ children, allowedRoles }) => {
  const { role, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && !allowedRoles.includes(role)) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--danger)' }}>ACCESS DENIED</h2>
        <p className="text-secondary">Your current role ({role}) is not authorized to view this area.</p>
        <a href="/dashboard">Return to Dashboard</a>
      </div>
    );
  }

  return <>{children}</>;
};

export default RoleGuard;
