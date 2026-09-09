import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { inferVehicle, getVehicleHistory, OrchestrationResult, TelemetryRecord, InferenceRunHistory } from '../services/api';
import DataSourceBadge from '../components/ui/DataSourceBadge';
import RULCard from '../components/domain/RULCard';
import AgentPipeline from '../components/domain/AgentPipeline';
import { LoadingState, ErrorState, UnknownState } from '../components/ui/States';
import ThemeToggle from '../components/ui/ThemeToggle';
import DatasetUploader from '../components/command-center/DatasetUploader';
import ProcessingPipeline from '../components/command-center/ProcessingPipeline';

const VehicleDashboard: React.FC = () => {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const [searchParams] = useSearchParams();
  const vehicleClass = searchParams.get('class') || 'UNKNOWN_CLASS';
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState<'IDLE' | 'PROCESSING' | 'COMPLETE' | 'ERROR'>('IDLE');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<OrchestrationResult | null>(null);
  const [history, setHistory] = useState<InferenceRunHistory[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [currentTelemetry, setCurrentTelemetry] = useState<TelemetryRecord | null>(null);

  if (vehicleClass !== 'TANK' && vehicleClass !== 'LOGISTIC TRUCK' && vehicleClass !== 'OFFICER VEHICLE') {
    return <ErrorState message="Invalid Vehicle Class" onRetry={() => navigate('/vehicles')} />;
  }

  const isTank = vehicleClass === 'TANK';

  const loadHistory = async () => {
    if (!vehicleId) return;
    setHistoryLoading(true);
    try {
      const data = await getVehicleHistory(vehicleId);
      setHistory(data);
    } catch (e) {
      console.error('Failed to load history', e);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [vehicleId]);

  const handleDatasetReady = async (telemetryData: any[]) => {
    setLoading(true);
    setPipelineStatus('PROCESSING');
    setError(null);
    setResult(null);
    
    // Grab the latest telemetry point for display
    if (telemetryData.length > 0) {
      setCurrentTelemetry(telemetryData[telemetryData.length - 1]);
    }

    try {
      const res = await inferVehicle({
        vehicle_id: vehicleId || 'unknown',
        vehicle_class: vehicleClass,
        telemetry: telemetryData
      });
      setResult(res);
      setPipelineStatus('COMPLETE');
      await loadHistory();
    } catch (err: any) {
      setError('INFERENCE ERROR: Unable to process the telemetry dataset.');
      setPipelineStatus('ERROR');
    } finally {
      setLoading(false);
    }
  };

  const vRes = result && vehicleId ? result.vehicle_results[vehicleId] : null;
  const isUnknown = vRes && vRes.prognostics && vRes.prognostics.fusion_rul_hours === null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', paddingBottom: '4rem' }}>
      
      {/* Header */}
      <header className="glass-panel" style={{ padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '-2rem -2rem 2rem', borderRadius: 0, borderLeft: 'none', borderRight: 'none', borderTop: 'none' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1 className="text-xl font-bold" style={{ margin: 0, textTransform: 'uppercase', letterSpacing: '2px' }}>
            VEDA COMMAND CENTER <span className="text-secondary" style={{ margin: '0 10px' }}>|</span> {vehicleClass} <span className="text-accent">#{vehicleId}</span>
          </h1>
          <DataSourceBadge />
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <ThemeToggle />
          <button 
            onClick={() => navigate('/vehicles')} 
            style={{ padding: '8px 16px', background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            ← SELECT VEHICLE
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
        
        {/* Left Column (Primary Operations) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h2 className="uppercase-label text-secondary" style={{ marginBottom: '1.5rem' }}>DATASET &amp; ML PIPELINE</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <DatasetUploader onDataReady={handleDatasetReady} isLoading={loading} />
              
              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '2rem' }}>
                <ProcessingPipeline status={pipelineStatus} result={result} isTank={isTank} />
              </div>
            </div>
            {error && <div style={{ color: 'var(--danger)', marginTop: '1rem', fontWeight: 'bold' }}>{error}</div>}
          </div>
          
          {vRes && (
            <div className="animate-fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              {isUnknown ? (
                <div style={{ gridColumn: '1 / -1' }}><UnknownState /></div>
              ) : (
                <>
                  <RULCard 
                    rulHours={vRes.prognostics?.fusion_rul_hours ?? null} 
                    fusionMethod={isTank ? '1.00 × XGBoost' : '0.30 × LSTM + 0.70 × XGBoost'} 
                  />
                  <div className="glass-panel" style={{ padding: '1.5rem', borderColor: result?.fleet_status?.readiness_status === 'READY' ? 'var(--success)' : 'var(--danger)', borderLeftWidth: '4px' }}>
                    <div className="uppercase-label text-secondary">FLEET READINESS STATUS</div>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: result?.fleet_status?.readiness_status === 'READY' ? 'var(--success)' : 'var(--danger)', margin: '0.5rem 0' }}>
                      {result?.fleet_status?.readiness_status || 'UNKNOWN'}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Six-Agent Visualization */}
          {result && (
            <div className="glass-panel animate-fade-in" style={{ padding: '1.5rem' }}>
              <div className="uppercase-label text-secondary" style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>SIX-AGENT ORCHESTRATION</div>
              <AgentPipeline orchestrationResult={result} />
            </div>
          )}

          {/* History */}
          <div className="glass-panel">
            <div className="uppercase-label text-secondary" style={{ padding: '1.5rem 1.5rem 0' }}>PERSISTED INFERENCE HISTORY</div>
            <div style={{ padding: '1.5rem' }}>
              {historyLoading ? (
                <LoadingState message="Loading History..." />
              ) : history.length === 0 ? (
                <div style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>NO HISTORY FOUND</div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                        <th style={{ padding: '12px' }}>DATE</th>
                        <th style={{ padding: '12px' }}>TIMESTEPS</th>
                        <th style={{ padding: '12px' }}>RUL (HOURS)</th>
                        <th style={{ padding: '12px' }}>FUSION METHOD</th>
                        <th style={{ padding: '12px' }}>READINESS</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Array.isArray(history) && history.map((run) => (
                        <tr key={run.id} style={{ borderBottom: '1px solid var(--border)' }}>
                          <td style={{ padding: '12px', color: 'var(--text-primary)' }}>{new Date(run.created_at).toLocaleString()}</td>
                          <td style={{ padding: '12px', color: 'var(--text-primary)' }}>{run.timestep_count}</td>
                          <td style={{ padding: '12px', fontWeight: 'bold', color: run.inference_result?.fusion_rul_hours === null ? 'var(--unknown)' : 'var(--text-primary)' }}>
                            {run.inference_result?.fusion_rul_hours === null ? 'UNKNOWN' : run.inference_result?.fusion_rul_hours?.toFixed(2)}
                          </td>
                          <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{run.inference_result?.fusion_method || 'N/A'}</td>
                          <td style={{ padding: '12px', fontWeight: 'bold', color: run.fleet_readiness?.readiness_status === 'READY' ? 'var(--success)' : run.fleet_readiness?.readiness_status === 'UNKNOWN' ? 'var(--unknown)' : 'var(--danger)' }}>
                            {run.fleet_readiness?.readiness_status || run.status}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column (Diagnostics) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
             <div className="uppercase-label text-secondary" style={{ marginBottom: '1rem' }}>RF CLASSIFICATION</div>
             {vRes ? (
               <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                   <span className="text-secondary">ABNORMAL DETECTED</span>
                   <span style={{ color: vRes.monitoring?.abnormal_detected ? 'var(--danger)' : 'var(--success)', fontWeight: 'bold' }}>{vRes.monitoring?.abnormal_detected ? 'YES' : 'NO'}</span>
                 </div>
                 <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                   <span className="text-secondary">SEVERITY SCORE</span>
                   <span>{vRes.monitoring?.severity_score?.toFixed(4) ?? 'N/A'}</span>
                 </div>
                 <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px dashed var(--border)', paddingTop: '12px' }}>
                   <span className="text-secondary">RISK THRESHOLD</span>
                   <span>{isTank ? '0.52' : '0.35'}</span>
                 </div>
               </div>
             ) : <div className="text-secondary" style={{ fontStyle: 'italic' }}>AWAITING DATASET UPLOAD</div>}
          </div>

          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <div className="uppercase-label text-secondary" style={{ marginBottom: '1rem' }}>DIAGNOSTICS</div>
            {vRes ? (
               <div>
                 {vRes.diagnostics?.active_fault_codes?.length > 0 ? (
                   <div style={{ color: 'var(--danger)', fontWeight: 'bold', fontSize: '1.25rem' }}>{vRes.diagnostics.active_fault_codes.join(', ')}</div>
                 ) : (
                   <div style={{ color: 'var(--success)', fontWeight: 'bold' }}>NO ACTIVE FAULTS</div>
                 )}
               </div>
             ) : <div className="text-secondary" style={{ fontStyle: 'italic' }}>AWAITING DATASET UPLOAD</div>}
          </div>

          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <div className="uppercase-label text-secondary" style={{ marginBottom: '1rem' }}>LATEST TELEMETRY</div>
            {currentTelemetry ? (
               <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.8rem' }}>
                 {Object.entries(currentTelemetry).slice(0, 15).map(([k, v]) => (
                   <div key={k} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', paddingBottom: '4px' }}>
                     <span className="text-secondary" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '120px' }} title={k}>{k.replace(/_/g, ' ')}</span>
                     <span style={{ fontWeight: 500 }}>{typeof v === 'number' ? v.toFixed(2) : v}</span>
                   </div>
                 ))}
               </div>
             ) : <div className="text-secondary" style={{ fontStyle: 'italic' }}>NO DATA AVAILABLE</div>}
          </div>

        </div>
      </div>
    </div>
  );
};

export default VehicleDashboard;
