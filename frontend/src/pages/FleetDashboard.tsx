import React from 'react';
import { Link } from 'react-router-dom';
import DataSourceBadge from '../components/ui/DataSourceBadge';
import VehicleCard from '../components/domain/VehicleCard';
import Navbar from '../components/ui/Navbar';

const FleetDashboard: React.FC = () => {
  
  const vehicles = [
    { id: '2', class: 'TANK', label: 'TANK UNIT #2', pipeline: '1.00 × XGBOOST', img: '/tank-exploded.png', counts: { healthy: 1, attention: 0, notReady: 0, unknown: 0 } },
    { id: 'LOV_001', class: 'LOGISTIC TRUCK', label: 'LOGISTIC TRUCK LOV_001', pipeline: '0.30 × LSTM + 0.70 × XGBOOST', img: '/logistic-exploded.png', counts: { healthy: 1, attention: 0, notReady: 0, unknown: 0 } },
    { id: 'LOV_021', class: 'OFFICER VEHICLE', label: 'OFFICER VEHICLE LOV_021', pipeline: '0.30 × LSTM + 0.70 × XGBOOST', img: '/officer-exploded.png', counts: { healthy: 1, attention: 0, notReady: 0, unknown: 0 } }
  ];

  return (
    <div style={{ paddingBottom: '4rem' }}>
      <Navbar rightAction={
        <Link to="/" className="hud-border" style={{ padding: '0.5rem 1.5rem', background: 'transparent', color: 'var(--accent)', fontWeight: 'bold', fontSize: '0.875rem', letterSpacing: '1px', textDecoration: 'none' }}>
          LOGOUT
        </Link>
      } />
      
      <div style={{ padding: '2rem' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 className="text-2xl font-bold" style={{ margin: 0, letterSpacing: '2px' }}>VEDA FLEET COMMAND</h1>
          <div className="text-warning font-bold">DEMO MODE</div>
          <p className="text-secondary" style={{ marginTop: '0.5rem' }}>Overview of active fleet diagnostic monitoring systems.</p>
        </div>
        <div style={{ textAlign: 'right' }}>
           <DataSourceBadge />
           <div className="text-xs text-secondary" style={{ marginTop: '8px', maxWidth: '400px' }}>
             * Current telemetry is derived from the project's canonical datasets for demonstration. Real-time vehicle sensor ingestion is not connected.
           </div>
        </div>
      </header>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', marginBottom: '3rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div className="uppercase-label text-secondary">TOTAL VEHICLES</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>3</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--success)' }}>
          <div className="uppercase-label text-success">HEALTHY</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)' }}>3</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--warning)' }}>
          <div className="uppercase-label text-warning">ATTENTION REQUIRED</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--warning)' }}>0</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--danger)' }}>
          <div className="uppercase-label text-danger">NOT READY</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--danger)' }}>0</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--unknown)' }}>
          <div className="uppercase-label text-unknown">UNKNOWN</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--unknown)' }}>0</div>
        </div>
      </div>

      <h2 className="text-lg font-bold" style={{ marginBottom: '1.5rem', letterSpacing: '1px' }}>ACTIVE DEMONSTRATION VEHICLES</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '2rem' }}>
        {vehicles.map(v => (
          <VehicleCard 
            key={v.id} 
            id={v.id + '?class=' + encodeURIComponent(v.class)} 
            name={v.class} 
            imageSrc={v.img} 
            count={1} 
            statusSummary={v.counts} 
          />
        ))}
        </div>
      </div>
    </div>
  );
};

export default FleetDashboard;
