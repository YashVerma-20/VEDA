import React from 'react';
import { Link } from 'react-router-dom';
import VedaLogo from './VedaLogo';
import ThemeToggle from './ThemeToggle';

interface NavbarProps {
  children?: React.ReactNode;
  rightAction?: React.ReactNode;
  position?: 'fixed' | 'sticky' | 'absolute' | 'relative';
}

const Navbar: React.FC<NavbarProps> = ({ children, rightAction, position = 'sticky' }) => {
  return (
    <header style={{
      position: position, top: 0, left: 0, right: 0,
      padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between',
      alignItems: 'center', zIndex: 100, background: 'rgba(0,0,0,0.6)',
      backdropFilter: 'blur(12px)', borderBottom: '1px solid var(--glass-border)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center' }}>
          <VedaLogo height="32px" iconOnly />
        </Link>
        {children}
      </div>
      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
        <div className="mono-metadata hidden md:block" style={{ marginRight: '1rem' }}>SYSTEM: ONLINE</div>
        <ThemeToggle />
        {rightAction !== undefined ? rightAction : (
          <Link to="/login" className="hud-border" style={{ padding: '0.5rem 1.5rem', background: 'transparent', color: 'var(--accent)', fontWeight: 'bold', fontSize: '0.875rem', letterSpacing: '1px', textDecoration: 'none' }}>
            ENTER SYSTEM
          </Link>
        )}
      </div>
    </header>
  );
};

export default Navbar;
