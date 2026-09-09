import React from 'react';
import { useNavigate } from 'react-router-dom';
import DataSourceBadge from '../components/ui/DataSourceBadge';

const VehiclesPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSelect = (category: string) => {
    // Navigate to a placeholder vehicle ID for the category so the Command Center can use it
    if (category === 'TANK') navigate('/vehicle/2?class=TANK');
    else if (category === 'LOGISTIC') navigate('/vehicle/LOV_001?class=LOGISTIC TRUCK');
  };

  return (
    <div style={{ minHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '3rem' }}>
        <div>
          <h1 className="text-2xl font-bold" style={{ margin: 0, letterSpacing: '2px' }}>VEHICLE SELECTION</h1>
          <p className="text-secondary" style={{ marginTop: '0.5rem' }}>Select a vehicle category to enter the diagnostic command center.</p>
        </div>
        <DataSourceBadge />
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '3rem', flex: 1, alignItems: 'center', alignContent: 'center' }}>
        
        {/* TANK CARD */}
        <div 
          className="hud-border glass-panel vehicle-selection-card animate-fade-in"
          onClick={() => handleSelect('TANK')}
          style={{ cursor: 'pointer', padding: '3rem', textAlign: 'center', transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)', animationDelay: '0.1s', position: 'relative', overflow: 'hidden', borderRadius: 0 }}
        >
          <div className="card-bg-glow" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '100%', height: '100%', background: 'radial-gradient(circle, var(--accent-muted) 0%, transparent 60%)', opacity: 0, transition: 'opacity 0.4s ease', zIndex: 0 }} />
          <div style={{ position: 'relative', height: '250px', marginBottom: '2rem', zIndex: 1 }}>
            <img 
              src="/assets/vehicles/tank/normal.png" 
              alt="Tank" 
              style={{ width: '100%', height: '100%', objectFit: 'contain', transition: 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)', filter: 'drop-shadow(0 15px 25px rgba(0,0,0,0.6))' }} 
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
            />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <h2 className="text-2xl font-bold" style={{ marginBottom: '1rem', letterSpacing: '0.2em' }}>HEAVY ARMOR / TANK</h2>
            <p className="text-secondary" style={{ marginBottom: '2rem', lineHeight: 1.6 }}>Heavy armor diagnostic and prognostics workflow. Evaluates engine, transmission, and operational readiness.</p>
            <div style={{ color: 'var(--accent)', fontWeight: 'bold', letterSpacing: '2px', textTransform: 'uppercase' }}>INITIALIZE TANK CENTER &rarr;</div>
          </div>
        </div>

        {/* LOGISTIC / OFFICER CARD */}
        <div 
          className="hud-border glass-panel vehicle-selection-card animate-fade-in"
          onClick={() => handleSelect('LOGISTIC')}
          style={{ cursor: 'pointer', padding: '3rem', textAlign: 'center', transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)', animationDelay: '0.2s', position: 'relative', overflow: 'hidden', borderRadius: 0 }}
        >
          <div className="card-bg-glow" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '100%', height: '100%', background: 'radial-gradient(circle, var(--accent-muted) 0%, transparent 60%)', opacity: 0, transition: 'opacity 0.4s ease', zIndex: 0 }} />
          <div style={{ position: 'relative', height: '250px', marginBottom: '2rem', zIndex: 1 }}>
            <img 
              src="/assets/vehicles/logistic/normal.png" 
              alt="Logistic Truck" 
              style={{ width: '100%', height: '100%', objectFit: 'contain', transition: 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)', filter: 'drop-shadow(0 15px 25px rgba(0,0,0,0.6))' }} 
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
            />
          </div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <h2 className="text-2xl font-bold" style={{ marginBottom: '1rem', letterSpacing: '0.2em' }}>LOGISTIC / OFFICER</h2>
            <p className="text-secondary" style={{ marginBottom: '2rem', lineHeight: 1.6 }}>Light and medium transport diagnostics. Evaluates drivetrain, electrical systems, and fleet readiness.</p>
            <div style={{ color: 'var(--accent)', fontWeight: 'bold', letterSpacing: '2px', textTransform: 'uppercase' }}>INITIALIZE VEHICLE CENTER &rarr;</div>
          </div>
        </div>

      </div>

      <style>{`
        .vehicle-selection-card:hover {
          transform: translateY(-5px);
          border-color: var(--accent);
          box-shadow: 0 15px 40px rgba(88, 166, 255, 0.2);
          background: rgba(0,0,0,0.4);
        }
        .vehicle-selection-card:hover img {
          transform: scale(1.05) translateY(-3px);
        }
        .vehicle-selection-card:hover .card-bg-glow {
          opacity: 0.6 !important;
        }
      `}</style>
    </div>
  );
};

export default VehiclesPage;
