import React, { useState, useEffect } from 'react';
import { getVehicleHistory, InferenceRunHistory } from '../services/api';
import DataSourceBadge from '../components/ui/DataSourceBadge';
import { LoadingState } from '../components/ui/States';

const demoVehicles = [
  { id: '2', class: 'TANK' },
  { id: 'LOV_001', class: 'LOGISTIC TRUCK' },
  { id: 'LOV_021', class: 'OFFICER VEHICLE' }
];

const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<InferenceRunHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllHistory = async () => {
      try {
        const promises = demoVehicles.map(v => getVehicleHistory(v.id));
        const results = await Promise.all(promises);
        
        // Merge and sort descending
        const combined = results.flat().sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        
        setHistory(combined);
      } catch (err) {
        console.error("Failed to load history for fleet", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAllHistory();
  }, []);

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 className="text-2xl font-bold" style={{ margin: 0, letterSpacing: '2px' }}>INFERENCE HISTORY</h1>
          <p className="text-secondary" style={{ marginTop: '0.5rem' }}>Global persistent log of all evaluation and diagnostic runs.</p>
        </div>
        <DataSourceBadge />
      </header>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        {loading ? (
          <LoadingState message="Aggregating Fleet History..." />
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
            NO INFERENCE RECORDS FOUND IN DATABASE
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                  <th style={{ padding: '12px' }}>DATE</th>
                  <th style={{ padding: '12px' }}>VEHICLE ID</th>
                  <th style={{ padding: '12px' }}>CLASS</th>
                  <th style={{ padding: '12px' }}>TIMESTEPS</th>
                  <th style={{ padding: '12px' }}>RUL (HOURS)</th>
                  <th style={{ padding: '12px' }}>FUSION METHOD</th>
                  <th style={{ padding: '12px' }}>READINESS</th>
                </tr>
              </thead>
              <tbody>
                {history.map((run) => (
                  <tr key={run.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '12px', color: 'var(--text-primary)' }}>{new Date(run.created_at).toLocaleString()}</td>
                    <td style={{ padding: '12px', fontWeight: 'bold', color: 'var(--accent)' }}>{run.vehicle_id}</td>
                    <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{run.vehicle_class}</td>
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
  );
};

export default HistoryPage;
