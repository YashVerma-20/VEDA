import React from 'react';

interface RULCardProps {
  rulHours: number | null;
  fusionMethod: string;
}

const RULCard: React.FC<RULCardProps> = ({ rulHours, fusionMethod: _fusionMethod }) => {
  if (rulHours === null) {
    return (
      <div className="glass-panel" style={{ padding: '1.5rem', borderColor: 'var(--unknown)', borderLeftWidth: '4px' }}>
        <div className="uppercase-label text-secondary">REMAINING USEFUL LIFE</div>
        <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--unknown)', margin: '0.5rem 0' }}>UNKNOWN</div>
        <div className="text-xs text-secondary">Insufficient data available for reliable prediction.</div>
      </div>
    );
  }

  let color = 'var(--success)';
  if (rulHours < 50) color = 'var(--danger)';
  else if (rulHours < 150) color = 'var(--warning)';

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', borderColor: color, borderLeftWidth: '4px' }}>
      <div className="uppercase-label text-secondary">REMAINING USEFUL LIFE</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', margin: '0.5rem 0' }}>
        <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: color }}>
          {rulHours.toFixed(2)}
        </div>
        <div className="text-secondary font-bold">HOURS</div>
      </div>
      <div className="text-xs" style={{ color: 'var(--accent)', backgroundColor: 'var(--accent-muted)', padding: '4px 8px', borderRadius: '4px', display: 'inline-block', fontWeight: 'bold', letterSpacing: '1px' }}>
        FINAL FUSED RUL
      </div>
    </div>
  );
};

export default RULCard;
