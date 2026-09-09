import React, { useState, useRef } from 'react';

interface DatasetUploaderProps {
  onDataReady: (data: any[]) => void;
  isLoading: boolean;
}

const DatasetUploader: React.FC<DatasetUploaderProps> = ({ onDataReady, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = (file: File) => {
    setError(null);
    if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
      setError('INVALID FORMAT: Only .json telemetry datasets are supported.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string);
        if (!Array.isArray(json)) {
          setError('INVALID SCHEMA: Expected a JSON array of telemetry records.');
          return;
        }
        onDataReady(json);
      } catch (err) {
        setError('PARSE ERROR: Unreadable JSON file.');
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`glass-panel ${dragActive ? 'drag-active' : ''}`}
      style={{ 
        padding: '3rem 2rem', 
        textAlign: 'center', 
        borderStyle: dragActive ? 'dashed' : 'solid',
        borderColor: dragActive ? 'var(--accent)' : 'var(--glass-border)',
        transition: 'all 0.3s ease',
        position: 'relative'
      }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input 
        ref={inputRef} 
        type="file" 
        accept=".json" 
        data-testid="dataset-input"
        style={{ display: 'none' }} 
        onChange={handleChange}
        disabled={isLoading}
      />
      
      <div style={{ marginBottom: '1.5rem', opacity: isLoading ? 0.5 : 1 }}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-secondary)' }}>
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
      </div>

      <h3 className="text-xl font-bold" style={{ marginBottom: '0.5rem', letterSpacing: '1px' }}>DATASET INPUT</h3>
      <p className="text-secondary" style={{ marginBottom: '2rem' }}>
        {isLoading ? 'PROCESSING DATASET...' : 'Drag & Drop Telemetry Dataset'}
      </p>

      {error && <div style={{ color: 'var(--danger)', marginBottom: '1.5rem', fontWeight: 'bold' }}>{error}</div>}

      <button 
        onClick={() => inputRef.current?.click()}
        disabled={isLoading}
        style={{
          padding: '10px 24px',
          background: isLoading ? 'var(--surface-elevated)' : 'transparent',
          color: isLoading ? 'var(--text-secondary)' : 'var(--accent)',
          border: `1px solid ${isLoading ? 'var(--border)' : 'var(--accent)'}`,
          borderRadius: '4px',
          fontWeight: 'bold',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          letterSpacing: '1px'
        }}
      >
        {isLoading ? 'UPLOADING...' : 'SELECT FILE'}
      </button>

      <div className="text-xs text-secondary" style={{ marginTop: '1.5rem', fontStyle: 'italic' }}>
        * Only supports project canonical dataset format (.json)
      </div>
    </div>
  );
};

export default DatasetUploader;
