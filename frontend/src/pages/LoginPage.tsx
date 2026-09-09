import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, Role } from '../contexts/AuthContext';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = (role: Role) => {
    login(role);
    navigate('/vehicles');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--background)' }}>
      <div className="glass-panel animate-fade-in" style={{ padding: '3rem', maxWidth: '400px', width: '100%', textAlign: 'center' }}>
        <div style={{ fontSize: '2rem', fontWeight: 900, letterSpacing: '0.1em', marginBottom: '0.5rem' }}>VEDA</div>
        <div className="text-sm text-secondary" style={{ marginBottom: '2rem' }}>VEHICLE EVALUATION AND DIAGNOSTIC AGENT</div>
        
        <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: 'var(--warning-muted)', border: '1px solid var(--warning)', borderRadius: '4px' }}>
          <div className="uppercase-label text-warning" style={{ marginBottom: '0.5rem' }}>FRONTEND DEMO AUTHENTICATION</div>
          <div className="text-xs text-secondary">Select a role to preview UI capabilities. No backend security boundary is enforced.</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <button
            onClick={() => handleLogin('ADMIN')}
            style={{ padding: '1rem', background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            LOGIN AS ADMIN
          </button>
          <button
            onClick={() => handleLogin('MAINTAINER')}
            style={{ padding: '1rem', background: 'var(--surface-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            LOGIN AS MAINTAINER
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
