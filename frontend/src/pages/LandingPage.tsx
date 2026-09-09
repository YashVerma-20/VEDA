import React, { useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import ThemeToggle from '../components/ui/ThemeToggle';

const items = [
  { id: 1, color: "var(--accent)", label: "Tank", image: "/assets/vehicles/tank/normal.png" },
  { id: 2, color: "var(--success)", label: "Logistic Platform", image: "/assets/vehicles/logistic/normal.png" },
];

const ITEM_WIDTH = 400;
const GAP = 30;

const LandingPage: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  const totalDistance = (items.length - 1) * (ITEM_WIDTH + GAP);
  const x = useTransform(scrollYProgress, [0, 1], [0, -totalDistance]);

  return (
    <div className="tech-grid-bg" style={{ background: 'var(--background)' }}>
      {/* Persistent Header */}
      <header style={{ 
        position: 'fixed', top: 0, left: 0, right: 0,
        padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between', 
        alignItems: 'center', zIndex: 100, background: 'rgba(0,0,0,0.4)', 
        backdropFilter: 'blur(12px)', borderBottom: '1px solid var(--glass-border)' 
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '8px', height: '24px', background: 'var(--accent)' }} />
          <div style={{ fontSize: '1.5rem', fontWeight: 900, letterSpacing: '0.15em' }}>VEDA</div>
        </div>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <div className="mono-metadata hidden md:block" style={{ marginRight: '1rem' }}>SYSTEM: ONLINE</div>
          <ThemeToggle />
          <Link to="/login" className="hud-border" style={{ padding: '0.5rem 1.5rem', background: 'transparent', color: 'var(--accent)', fontWeight: 'bold', fontSize: '0.875rem', letterSpacing: '1px', textDecoration: 'none' }}>
            ENTER SYSTEM
          </Link>
        </div>
      </header>

      {/* EXACT MOTION.DEV DOM STRUCTURE */}
      <div id="example">
        
        {/* Intro Section */}
        <section className="intro-section">
          <h1 className="impact">VEDA</h1>
          <p className="text-xl text-secondary" style={{ marginTop: '1rem', maxWidth: '600px' }}>
            Vehicle Evaluation and Diagnostic Agent.<br/>
            Predict failure before it becomes a mission problem.
          </p>
          <div className="uppercase-label text-secondary" style={{ marginTop: '3rem' }}>SCROLL TO INSPECT</div>
          <div style={{ width: '2px', height: '40px', background: 'var(--accent)', opacity: 0.5, marginTop: '1rem' }} />
        </section>

        {/* Horizontal Scroll Gallery */}
        <div ref={containerRef} className="scroll-container">
          <div className="sticky-wrapper">
            <motion.div className="gallery" style={{ x }}>
              {items.map((item) => (
                <div
                  key={item.id}
                  className="gallery-item"
                  style={{
                    '--item-color': item.color,
                    '--item-image': `url(${item.image})`,
                  } as React.CSSProperties}
                >
                  <div className="item-content">
                    <span className="item-number">0{item.id}</span>
                    <h2>{item.label}</h2>
                  </div>
                </div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* Outro Section */}
        <section className="outro-section">
          <h2 className="text-4xl font-bold letter-spacing-1" style={{ marginBottom: '1rem' }}>INTELLIGENCE PIPELINE</h2>
          <p className="text-lg text-secondary" style={{ marginBottom: '4rem', maxWidth: '800px', lineHeight: 1.6, textAlign: 'center' }}>
            VEDA orchestrates a multi-stage machine learning pipeline. Telemetry undergoes classification routing before branching into specialized predictive models, fusing results into a final precision RUL.
          </p>
          
          <div className="glass-panel" style={{ padding: '3rem', position: 'relative', overflow: 'hidden', maxWidth: '1000px', width: '100%', marginBottom: '6rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', position: 'relative', zIndex: 2 }}>
              <div style={{ padding: '1.5rem', textAlign: 'center', flex: 1, borderRight: '1px solid var(--border)' }}>
                <div className="text-xs text-secondary uppercase-label">Step 1</div>
                <div className="font-bold letter-spacing-1">DATASET UPLOAD</div>
              </div>
              <div style={{ padding: '1.5rem', textAlign: 'center', flex: 1, borderRight: '1px solid var(--border)' }}>
                <div className="text-xs text-secondary uppercase-label">Step 2</div>
                <div className="font-bold letter-spacing-1">PREPROCESSING</div>
              </div>
              <div style={{ padding: '1.5rem', textAlign: 'center', flex: 1, borderRight: '1px solid var(--border)' }}>
                <div className="text-xs text-secondary uppercase-label">Step 3 (ROUTER)</div>
                <div className="font-bold letter-spacing-1">RANDOM FOREST</div>
              </div>
              <div style={{ padding: '1.5rem', textAlign: 'center', flex: 1, borderRight: '1px solid var(--border)' }}>
                <div className="text-xs text-secondary uppercase-label">Step 4 (PARALLEL)</div>
                <div className="font-bold letter-spacing-1 text-accent">XGBoost / LSTM</div>
              </div>
              <div style={{ padding: '1.5rem', textAlign: 'center', flex: 1 }}>
                <div className="text-xs text-secondary uppercase-label">Step 5</div>
                <div className="font-bold letter-spacing-1 text-success">FUSION RUL</div>
              </div>
            </div>
          </div>

          <h2 className="text-5xl font-bold" style={{ marginBottom: '1.5rem', letterSpacing: '0.15em', textAlign: 'center' }}>READY FOR DEPLOYMENT</h2>
          <Link to="/login" className="hud-border" style={{ 
            display: 'inline-block', padding: '1.25rem 4rem', background: 'var(--glass-bg)', 
            backdropFilter: 'blur(10px)', color: 'var(--accent)', fontWeight: 'bold', 
            fontSize: '1.25rem', letterSpacing: '3px', transition: 'all 0.3s ease', textDecoration: 'none' 
          }} 
            onMouseOver={(e) => { e.currentTarget.style.background = 'var(--accent-muted)'; e.currentTarget.style.boxShadow = '0 0 20px var(--accent-muted)'; }}
            onMouseOut={(e) => { e.currentTarget.style.background = 'var(--glass-bg)'; e.currentTarget.style.boxShadow = 'none'; }}
          >
            ENTER VEDA →
          </Link>
        </section>

      </div>
    </div>
  );
};

export default LandingPage;
