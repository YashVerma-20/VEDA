import React, { useState, useRef } from 'react';

interface DatasetUploaderProps {
  onDataReady: (data: any[]) => void;
  isLoading: boolean;
}

const ACCEPTED_EXTENSIONS = ['.json', '.csv', '.xlsx'];
const ACCEPTED_MIME = [
  'application/json',
  'text/csv',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
];

const isValidFile = (file: File) => {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  return ACCEPTED_EXTENSIONS.includes(ext) || ACCEPTED_MIME.includes(file.type);
};

const DatasetUploader: React.FC<DatasetUploaderProps> = ({ onDataReady, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const processFile = (file: File) => {
    setError(null);

    if (!isValidFile(file)) {
      setError('INVALID FORMAT: Only .json, .csv, or .xlsx datasets are supported.');
      return;
    }

    const ext = '.' + file.name.split('.').pop()?.toLowerCase();

    if (ext === '.json') {
      // Parse JSON directly
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const json = JSON.parse(e.target?.result as string);
          if (!Array.isArray(json)) {
            setError('INVALID SCHEMA: Expected a JSON array of telemetry records.');
            return;
          }
          onDataReady(json);
        } catch {
          setError('PARSE ERROR: Unreadable JSON file.');
        }
      };
      reader.readAsText(file);
    } else {
      // For .csv and .xlsx, send the raw File to the backend via FormData
      // We read as ArrayBuffer and pass as a blob — handled by the parent via a separate API call.
      // For now, signal to the parent with the File object wrapped in a special marker.
      // Actually: we pass to onDataReady with a special sentinel so VehicleDashboard can handle multipart upload.
      // But since the current API accepts a JSON body, we parse CSV client-side for now.
      if (ext === '.csv') {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const text = e.target?.result as string;
            const lines = text.trim().split('\n');
            const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
            const records = lines.slice(1).map(line => {
              const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
              const record: Record<string, any> = {};
              headers.forEach((h, i) => {
                const val = values[i];
                const num = Number(val);
                record[h] = (val !== '' && !isNaN(num)) ? num : val;
              });
              return record;
            });
            onDataReady(records);
          } catch {
            setError('PARSE ERROR: Could not parse CSV file.');
          }
        };
        reader.readAsText(file);
      } else {
        setError('XLSX support requires server-side parsing. Please convert to .csv or .json first.');
      }
    }
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
        accept=".json,.csv,.xlsx"
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

      <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
        {['.json', '.csv', '.xlsx'].map(fmt => (
          <span key={fmt} style={{
            padding: '2px 10px',
            border: '1px solid var(--border)',
            borderRadius: '4px',
            fontSize: '0.7rem',
            letterSpacing: '1px',
            color: 'var(--text-secondary)',
            fontWeight: 'bold'
          }}>
            {fmt.toUpperCase()}
          </span>
        ))}
      </div>
    </div>
  );
};

export default DatasetUploader;
