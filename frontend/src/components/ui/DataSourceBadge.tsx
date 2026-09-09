import React from 'react';

const DataSourceBadge: React.FC = () => {
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding: '4px 12px',
      backgroundColor: 'var(--accent-muted)',
      border: '1px solid var(--accent)',
      borderRadius: '4px',
      color: 'var(--accent)',
      fontSize: '0.75rem',
      fontWeight: 'bold',
      letterSpacing: '0.05em'
    }}>
      <span style={{ marginRight: '6px' }}>●</span>
      DATA SOURCE: DATASET-DERIVED DEMO FIXTURE
    </div>
  );
};

export default DataSourceBadge;
