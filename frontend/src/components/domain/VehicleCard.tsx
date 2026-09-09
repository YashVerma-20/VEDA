import React from 'react';
import { useNavigate } from 'react-router-dom';

interface VehicleCardProps {
  id: string;
  name: string;
  imageSrc: string;
  count: number;
  statusSummary?: { healthy: number; attention: number; notReady: number; unknown: number };
}

const VehicleCard: React.FC<VehicleCardProps> = ({ id, name, imageSrc, count, statusSummary }) => {
  const navigate = useNavigate();

  return (
    <div 
      className="glass-panel animate-fade-in"
      style={{
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        cursor: 'pointer'
      }}
      onClick={() => navigate(`/vehicle/${id}`)}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = 'var(--glass-shadow), 0 8px 24px var(--accent-muted)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'var(--glass-shadow)';
      }}
    >
      <div style={{ height: '200px', backgroundColor: 'var(--surface-elevated)', position: 'relative' }}>
        <img 
          src={imageSrc} 
          alt={name} 
          style={{ width: '100%', height: '100%', objectFit: 'contain', padding: '1rem' }} 
        />
        <div style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'var(--background)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold' }}>
          COUNT: {count}
        </div>
      </div>
      <div style={{ padding: '1.5rem' }}>
        <div className="uppercase-label text-secondary">CLASS</div>
        <div className="text-xl font-bold" style={{ marginBottom: '1rem' }}>{name}</div>
        
        {statusSummary && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-xs text-secondary">HEALTHY</span>
              <span className="text-xs text-success font-bold">{statusSummary.healthy}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-xs text-secondary">ATTENTION</span>
              <span className="text-xs text-warning font-bold">{statusSummary.attention}</span>
            </div>
          </div>
        )}
      </div>
      <div style={{ 
        padding: '1rem', 
        borderTop: '1px solid var(--border)', 
        textAlign: 'center', 
        color: 'var(--accent)', 
        fontWeight: 'bold', 
        fontSize: '0.875rem',
        backgroundColor: 'var(--accent-muted)'
      }}>
        OPEN DIAGNOSTICS
      </div>
    </div>
  );
};

export default VehicleCard;
