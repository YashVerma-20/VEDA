import React from 'react';

export const LoadingState: React.FC<{ message?: string }> = ({ message = 'Loading system data...' }) => (
  <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
    <div style={{ 
      display: 'inline-block', 
      width: '24px', 
      height: '24px', 
      border: '3px solid var(--border)', 
      borderTopColor: 'var(--accent)', 
      borderRadius: '50%',
      animation: 'spin 1s linear infinite',
      marginBottom: '1rem'
    }} />
    <div className="uppercase-label">{message}</div>
    <style>{`
      @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    `}</style>
  </div>
);

export const ErrorState: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', borderColor: 'var(--danger)', borderLeftWidth: '4px' }}>
    <div style={{ color: 'var(--danger)', fontWeight: 'bold', marginBottom: '0.5rem' }}>SYSTEM ERROR</div>
    <div className="text-secondary" style={{ marginBottom: '1rem' }}>{message}</div>
    {onRetry && (
      <button 
        onClick={onRetry}
        style={{
          background: 'var(--danger-muted)',
          color: 'var(--danger)',
          border: '1px solid var(--danger)',
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        RETRY CONNECTION
      </button>
    )}
  </div>
);

export const UnknownState: React.FC = () => (
  <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', borderColor: 'var(--unknown)', borderLeftWidth: '4px' }}>
    <div style={{ color: 'var(--unknown)', fontWeight: 'bold', marginBottom: '0.5rem', fontSize: '1.25rem' }}>UNKNOWN</div>
    <div className="text-secondary uppercase-label">INSUFFICIENT DATA: 30 TIMESTEPS REQUIRED</div>
  </div>
);
