import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const { role } = useAuth();

  const links = [
    { path: '/dashboard', label: 'COMMAND DASHBOARD', roles: ['ADMIN', 'MAINTAINER'] },
    { path: '/vehicles', label: 'VEHICLES', roles: ['ADMIN', 'MAINTAINER'] },
    { path: '/fleet', label: 'FLEET STATUS', roles: ['ADMIN', 'MAINTAINER'] },
    { path: '/history', label: 'INFERENCE HISTORY', roles: ['ADMIN', 'MAINTAINER'] },
    { path: '/agents', label: 'AGENT ORCHESTRATION', roles: ['ADMIN'] },
    { path: '/admin', label: 'ADMINISTRATION', roles: ['ADMIN'] },
  ];

  return (
    <aside className="glass-panel" style={{
      width: '260px',
      borderTop: 'none',
      borderBottom: 'none',
      borderLeft: 'none',
      borderRadius: 0,
      padding: '2rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '0.5rem'
    }}>
      <div className="uppercase-label text-secondary" style={{ padding: '0 1rem', marginBottom: '0.5rem' }}>
        SYSTEM NAVIGATION
      </div>
      {links.filter(l => role && l.roles.includes(role)).map(link => (
        <NavLink
          key={link.path}
          to={link.path}
          style={({ isActive }) => ({
            padding: '0.75rem 1rem',
            borderRadius: '4px',
            textDecoration: 'none',
            color: isActive ? 'var(--accent)' : 'var(--text-primary)',
            backgroundColor: isActive ? 'var(--accent-muted)' : 'transparent',
            fontWeight: isActive ? 600 : 500,
            fontSize: '0.875rem',
            letterSpacing: '0.02em',
            transition: 'background-color 0.2s',
            borderLeft: isActive ? '3px solid var(--accent)' : '3px solid transparent'
          })}
        >
          {link.label}
        </NavLink>
      ))}
      <div style={{ marginTop: 'auto', padding: '1rem' }}>
        <div className="text-xs text-secondary">VEDA DEMONSTRATION</div>
        <div className="text-xs text-secondary">BUILD 2.0.0</div>
      </div>
    </aside>
  );
};

export default Sidebar;
