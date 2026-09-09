import React from 'react';
import { OrchestrationResult } from '../../services/api';

interface AgentPipelineProps {
  orchestrationResult: OrchestrationResult;
}

const AgentPipeline: React.FC<AgentPipelineProps> = ({ orchestrationResult }) => {
  const agents = [
    { id: 'monitoring', label: 'MONITORING' },
    { id: 'diagnostics', label: 'DIAGNOSTICS' },
    { id: 'prognostics', label: 'PROGNOSTICS' },
    { id: 'maintenance_planning', label: 'MAINTENANCE' },
    { id: 'spare_parts', label: 'SPARE PARTS' },
    { id: 'fleet_readiness', label: 'FLEET READINESS' }
  ];

  // We extract the first vehicle's results. (Since vehicle dashboards query a specific vehicle)
  const vehicleId = Object.keys(orchestrationResult.vehicle_results || {})[0];
  const results = vehicleId ? orchestrationResult.vehicle_results[vehicleId] : {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {agents.map((agent, index) => {
        const result = results[agent.id];
        const status = result?.status || 'UNKNOWN';
        
        let colorVar = 'var(--text-secondary)';
        let borderColor = 'var(--border)';
        
        if (status === 'OK' || status === 'HEALTHY' || status === 'READY') {
          colorVar = 'var(--success)';
          borderColor = 'var(--success)';
        } else if (status === 'WARNING' || status === 'ATTENTION REQUIRED') {
          colorVar = 'var(--warning)';
          borderColor = 'var(--warning)';
        } else if (status === 'CRITICAL' || status === 'NOT READY') {
          colorVar = 'var(--danger)';
          borderColor = 'var(--danger)';
        } else if (status === 'UNKNOWN') {
          colorVar = 'var(--unknown)';
          borderColor = 'var(--unknown)';
        }

        return (
          <div key={agent.id} style={{ display: 'flex', alignItems: 'flex-start' }}>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              marginRight: '1rem',
              minWidth: '24px'
            }}>
              <div style={{ 
                width: '16px', 
                height: '16px', 
                borderRadius: '50%', 
                backgroundColor: colorVar,
                border: `2px solid var(--background)`,
                boxShadow: `0 0 0 2px ${borderColor}`,
                zIndex: 2
              }} />
              {index < agents.length - 1 && (
                <div style={{ width: '2px', height: '100%', minHeight: '60px', backgroundColor: 'var(--border)', margin: '4px 0' }} />
              )}
            </div>
            <div className="glass-panel animate-fade-in" style={{ flex: 1, padding: '1rem', borderColor: borderColor, borderLeftWidth: '4px', animationDelay: `${index * 0.1}s` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <div className="font-bold">{agent.label} AGENT</div>
                <div className="uppercase-label" style={{ color: colorVar }}>{status}</div>
              </div>
              <div className="text-sm text-secondary" style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                {!result ? 'AWAITING INFERENCE' : 
                  agent.id === 'monitoring' ? `Severity Score: ${result.severity_score?.toFixed(4) || 'N/A'}` :
                  agent.id === 'diagnostics' ? `${result.active_fault_codes?.length ? 'FAULTS DETECTED' : 'CLEAR'}` :
                  agent.id === 'prognostics' ? `RUL CALCULATED` :
                  agent.id === 'maintenance_planning' ? `${result.recommended_action || 'NO ACTION'}` :
                  agent.id === 'spare_parts' ? `${result.inventory_status === 'NOT_AVAILABLE' ? 'NOT AVAILABLE' : result.inventory_status || 'UNKNOWN'}` :
                  agent.id === 'fleet_readiness' ? `${result.readiness_status || 'UNKNOWN'}` :
                  'No data available'}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AgentPipeline;
