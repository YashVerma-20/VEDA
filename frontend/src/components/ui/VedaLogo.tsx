import React from 'react';
import { motion } from 'framer-motion';

interface VedaLogoProps {
  className?: string;
  height?: number | string;
  style?: React.CSSProperties;
  iconOnly?: boolean;
}

const VedaLogo: React.FC<VedaLogoProps> = ({ className = '', height = "1em", iconOnly = false, style = {} }) => {
  return (
    <div 
      className={`veda-logotype-container ${className}`} 
      style={{ 
        position: 'relative', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        ...style
      }}
    >
      <svg 
        height={height} 
        viewBox={iconOnly ? "5 15 90 80" : "5 15 370 80"} 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        style={{ overflow: 'visible' }}
      >
        <defs>
          <mask id="veda-slice-mask">
            <rect width="400" height="100" fill="white" />
            {/* Center vertical gap for the V */}
            <rect x="47" y="0" width="6" height="100" fill="black" />
            {/* Massive diagonal slice across the entire word */}
            <polygon points="-10,75 400,25 400,31 -10,81" fill="black" />
          </mask>
          <linearGradient id="veda-accent-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="1" />
            <stop offset="100%" stopColor="var(--accent-muted)" stopOpacity="0.5" />
          </linearGradient>
        </defs>

        {/* The massive, heavy sliced logotype */}
        <g fill="var(--text-primary)" mask="url(#veda-slice-mask)">
          {/* V */}
          <polygon points="5,15 35,15 50,65 65,15 95,15 50,95" />
          
          {!iconOnly && (
            <>
              {/* E */}
              <polygon points="110,15 180,15 180,35 135,35 135,45 170,45 170,65 135,65 135,75 180,75 180,95 110,95" />
              
              {/* D */}
              <path d="M 195 15 L 255 15 L 275 35 L 275 75 L 255 95 L 195 95 Z M 220 35 L 220 75 L 245 75 L 255 65 L 255 45 L 245 35 Z" fillRule="evenodd" />
              
              {/* A */}
              <path d="M 320 15 L 340 15 L 370 95 L 345 95 L 338 75 L 322 75 L 315 95 L 290 95 Z M 330 30 L 335 60 L 325 60 Z" fillRule="evenodd" />
            </>
          )}
        </g>

        {/* Floating accent chevron in the V's negative space */}
        <motion.polygon 
          points="50,50 62,25 52,25 50,32 48,25 38,25" 
          fill="url(#veda-accent-grad)"
          filter="drop-shadow(0 0 5px var(--accent-muted))"
          animate={{ y: [-3, 3, -3] }}
          transition={{ duration: 4, ease: "easeInOut", repeat: Infinity }}
        />
      </svg>
    </div>
  );
};

export default VedaLogo;
