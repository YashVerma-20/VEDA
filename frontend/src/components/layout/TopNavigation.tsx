import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ThemeToggle from '../ui/ThemeToggle';

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
    <header className="glass-panel" style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      padding: '0.75rem 2rem',
      borderTop: 'none',
      borderLeft: 'none',
      borderRight: 'none',
      borderRadius: 0,
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <Link to="/" style={{ color: 'var(--text-primary)', textDecoration: 'none' }}>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '0.1em' }}>VEDA</div>
        </Link>
        <div style={{ width: '1px', height: '24px', backgroundColor: 'var(--border)' }} />
        <div className="uppercase-label text-secondary">{getPageTitle(location.pathname)}</div>
      </div>
      
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
        <ThemeToggle />
        <button 
          onClick={logout}
          style={{
            background: 'transparent',
            border: '1px solid var(--border)',
            color: 'var(--text-primary)',
            padding: '6px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.75rem',
            fontWeight: 'bold'
          }}
        >
          LOGOUT
        </button>
      </div>
    </header>
  );
};

export default TopNavigation;
