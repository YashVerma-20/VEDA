import React from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Navbar from '../ui/Navbar';

const TopNavigation: React.FC = () => {
  const { role, logout } = useAuth();
  const location = useLocation();

  const getPageTitle = (path: string) => {
    if (path.startsWith('/dashboard')) return 'FLEET COMMAND';
    if (path.startsWith('/vehicle/')) return 'VEHICLE DIAGNOSTICS';
    if (path.startsWith('/vehicles')) return 'VEHICLE ROSTER';
    if (path.startsWith('/fleet')) return 'FLEET READINESS';
    if (path.startsWith('/history')) return 'INFERENCE HISTORY';
    if (path.startsWith('/agents')) return 'AGENT STATUS';
    if (path.startsWith('/admin')) return 'SYSTEM ADMINISTRATION';
    return 'COMMAND CENTER';
  };

  return (
    <Navbar 
      position="sticky"
      rightAction={
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ 
            padding: '4px 10px', 
            backgroundColor: 'var(--surface-elevated)', 
            border: '1px solid var(--border)', 
            borderRadius: '4px',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            letterSpacing: '0.05em'
          }}>
            ROLE: <span className="text-accent">{role}</span>
          </div>
          <button 
            onClick={logout}
            className="hud-border"
            style={{
              background: 'transparent',
              color: 'var(--text-primary)',
              padding: '6px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '0.75rem',
              letterSpacing: '0.05em'
            }}
          >
            LOGOUT
          </button>
        </div>
      }
    >
      <div style={{ width: '1px', height: '24px', backgroundColor: 'var(--border)' }} />
      <div className="uppercase-label text-secondary">{getPageTitle(location.pathname)}</div>
    </Navbar>
  );
};

export default TopNavigation;
