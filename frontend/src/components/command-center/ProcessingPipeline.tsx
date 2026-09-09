import React from 'react';
import { OrchestrationResult } from '../../services/api';

interface ProcessingPipelineProps {
  status: 'IDLE' | 'PROCESSING' | 'COMPLETE' | 'ERROR';
  result: OrchestrationResult | null;
  isTank: boolean;
}

const ProcessingPipeline: React.FC<ProcessingPipelineProps> = ({ status, result: _result }) => {
  const getStageStatus = (_stage: string) => {
    if (status === 'ERROR') return 'ERROR';
    if (status === 'IDLE') return 'IDLE';
    if (status === 'PROCESSING') return 'PROCESSING';
    return 'COMPLETE';
  };

  const PipelineNode: React.FC<{ label: string; activeStatus: string; delay: number }> = ({ label, activeStatus, delay }) => {
    const isError = activeStatus === 'ERROR';
    const isComplete = activeStatus === 'COMPLETE';
    const isProcessing = activeStatus === 'PROCESSING';
    
    let color = 'var(--text-secondary)';
    let borderColor = 'var(--border)';
    let bg = 'transparent';
    let pulse = false;

    if (isError) {
      color = 'var(--danger)';
      borderColor = 'var(--danger)';
    } else if (isComplete) {
      color = 'var(--success)';
      borderColor = 'var(--success)';
    } else if (isProcessing) {
      color = 'var(--accent)';
      borderColor = 'var(--accent)';
      bg = 'var(--accent-muted)';
      pulse = true;
    }

    return (
      <div 
        className="glass-panel"
        style={{ 
          padding: '1rem', 
          textAlign: 'center', 
          flex: 1, 
          minWidth: '120px',
          borderColor,
          backgroundColor: bg,
          color,
          animation: pulse ? 'pulse 2s infinite' : 'none',
          animationDelay: `${delay}s`,
          transition: 'all 0.3s ease'
        }}
      >
        <div className="text-xs uppercase-label" style={{ marginBottom: '0.5rem' }}>{label}</div>
        {isComplete && <div style={{ fontWeight: 'bold' }}>✓ COMPLETE</div>}
        {isProcessing && <div style={{ fontWeight: 'bold' }}>○ PROCESSING</div>}
        {isError && <div style={{ fontWeight: 'bold' }}>✕ ERROR</div>}
        {(!isComplete && !isProcessing && !isError) && <div style={{ opacity: 0.5 }}>PENDING</div>}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <style>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.4); }
          70% { box-shadow: 0 0 0 10px rgba(88, 166, 255, 0); }
          100% { box-shadow: 0 0 0 0 rgba(88, 166, 255, 0); }
        }
      `}</style>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <PipelineNode label="DATASET UPLOAD" activeStatus={status !== 'IDLE' ? (status === 'ERROR' ? 'ERROR' : 'COMPLETE') : 'IDLE'} delay={0} />
        <div className="text-secondary">&rarr;</div>
        
        <PipelineNode label="PREPROCESSING" activeStatus={getStageStatus('PREPROCESSING')} delay={0.1} />
        <div className="text-secondary">&rarr;</div>
        
        <PipelineNode label="RANDOM FOREST" activeStatus={getStageStatus('RF')} delay={0.2} />
        <div className="text-secondary">&rarr;</div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <PipelineNode label="XGBoost" activeStatus={getStageStatus('MODEL')} delay={0.3} />
          <PipelineNode label="LSTM + 1D CNN" activeStatus={getStageStatus('MODEL')} delay={0.35} />
        </div>
        <div className="text-secondary">&rarr;</div>
        
        <PipelineNode label="FUSION & RUL" activeStatus={getStageStatus('FUSION')} delay={0.4} />
      </div>
    </div>
  );
};

export default ProcessingPipeline;
