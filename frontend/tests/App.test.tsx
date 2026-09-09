import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LandingPage from '../src/pages/LandingPage';
import FleetDashboard from '../src/pages/FleetDashboard';
import VehicleDashboard from '../src/pages/VehicleDashboard';
import { Route, Routes } from 'react-router-dom';

global.fetch = vi.fn();

const mockSuccessResponse = {
  request_id: 'test_req',
  timestamp: '2023-01-01T00:00:00Z',
  status: 'SUCCESS',
  fleet_status: {
    readiness_status: 'READY',
    ready_count: 1,
    attention_count: 0,
    not_ready_count: 0,
    unknown_count: 0,
    ready_percentage: 100
  },
  vehicle_results: {
    '2': {
      monitoring: { abnormal_detected: true, severity_score: 0.9 },
      diagnostics: { active_fault_codes: ['ERR01'] },
      prognostics: { fusion_rul_hours: 15.5, xgb_rul_hours: 15.5, lstm_rul_hours: 10 },
      maintenance_planning: { recommended_action: 'Inspect Engine', priority: 'HIGH' },
      spare_parts: { part_identifier: 'NOT_AVAILABLE', inventory_status: 'NOT_AVAILABLE' }
    },
    'LOV_001': {
      monitoring: { abnormal_detected: false, severity_score: 0.1 },
      diagnostics: { active_fault_codes: [] },
      prognostics: { fusion_rul_hours: 45.0, xgb_rul_hours: 40.0, lstm_rul_hours: 50.0 },
      maintenance_planning: { recommended_action: 'NO ACTION', priority: 'LOW' },
      spare_parts: { part_identifier: 'AVAILABLE', inventory_status: 'AVAILABLE' }
    }
  },
  execution_trace: []
};

// Mock FileReader to execute synchronously for tests
class MockFileReader {
  onload: ((e: any) => void) | null = null;
  readAsText(file: File) {
    if (this.onload) {
      // Simulate reading a JSON array
      this.onload({ target: { result: '[{"mock": "telemetry"}]' } });
    }
  }
}
(global as any).FileReader = MockFileReader;

describe('Phase 7E Frontend Tests', () => {

  it('renders Landing Page with Phase 7F narrative', () => {
    render(<MemoryRouter><LandingPage /></MemoryRouter>);
    expect(screen.getByText(/Predict failure before it becomes a mission problem/i)).toBeInTheDocument();
  });

  it('renders Fleet Dashboard and vehicles with DEMO MODE disclosure', () => {
    render(<MemoryRouter><FleetDashboard /></MemoryRouter>);
    expect(screen.getByText(/VEDA FLEET COMMAND/i)).toBeInTheDocument();
    expect(screen.getByText(/DEMO MODE/i)).toBeInTheDocument();
    expect(screen.getAllByText(/DATASET-DERIVED DEMO FIXTURE/i).length).toBeGreaterThan(0);
  });

  it('handles invalid vehicle classes safely', () => {
    render(
      <MemoryRouter initialEntries={['/vehicle/999?class=INVALID']}>
        <Routes>
          <Route path="/vehicle/:vehicleId" element={<VehicleDashboard />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText(/Invalid Vehicle Class/i)).toBeInTheDocument();
  });

  it('verifies absence of live telemetry terminology', () => {
    render(
      <MemoryRouter initialEntries={['/vehicle/2?class=TANK']}>
        <Routes>
          <Route path="/vehicle/:vehicleId" element={<VehicleDashboard />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.queryByText(/Live Telemetry/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Streaming/i)).not.toBeInTheDocument();
    expect(screen.getByText(/DATASET-DERIVED DEMO FIXTURE/i)).toBeInTheDocument();
  });

  it('simulates Tank pipeline inference with correct fusion method', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockSuccessResponse
    });

    render(
      <MemoryRouter initialEntries={['/vehicle/2?class=TANK']}>
        <Routes>
          <Route path="/vehicle/:vehicleId" element={<VehicleDashboard />} />
        </Routes>
      </MemoryRouter>
    );
    
    // Simulate File Upload instead of clicking RUN DEMO INFERENCE
    const input = screen.getByTestId('dataset-input');
    const file = new File(['[{"mock": "data"}]'], 'mock.json', { type: 'application/json' });
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      // Results should now be on screen, including the fusion method
      expect(screen.getByText(/1.00 × XGBoost/i)).toBeInTheDocument();
      expect(screen.getByText(/15.50/i)).toBeInTheDocument();
      expect(screen.getByText(/ERR01/i)).toBeInTheDocument();
      expect(screen.getByText(/Inspect Engine/i)).toBeInTheDocument();
      expect(screen.getByText(/NOT AVAILABLE/i)).toBeInTheDocument();
      expect(screen.getAllByText(/READY/i).length).toBeGreaterThan(0);
    });
  });

  it('simulates Logistic pipeline inference with correct fusion method', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockSuccessResponse
    });

    render(
      <MemoryRouter initialEntries={['/vehicle/LOV_001?class=LOGISTIC TRUCK']}>
        <Routes>
          <Route path="/vehicle/:vehicleId" element={<VehicleDashboard />} />
        </Routes>
      </MemoryRouter>
    );
    
    // Simulate File Upload
    const input = screen.getByTestId('dataset-input');
    const file = new File(['[{"mock": "data"}]'], 'mock.json', { type: 'application/json' });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      // Fusion method check for Logistic
      expect(screen.getByText(/0.30 × LSTM/i)).toBeInTheDocument();
      expect(screen.getByText(/\+ 0.70 × XGBoost/i)).toBeInTheDocument();
    });
  });

  it('simulates UNKNOWN state for short telemetry', async () => {
    const mockUnknown = JSON.parse(JSON.stringify(mockSuccessResponse));
    mockUnknown.vehicle_results['2'].prognostics.fusion_rul_hours = null;

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockUnknown
    });

    // We will override FileReader specifically to return short telemetry just to mock our UI if necessary,
    // but the fetch mock is what controls the response.
    render(
      <MemoryRouter initialEntries={['/vehicle/2?class=TANK']}>
        <Routes>
          <Route path="/vehicle/:vehicleId" element={<VehicleDashboard />} />
        </Routes>
      </MemoryRouter>
    );
    
    const input = screen.getByTestId('dataset-input');
    const file = new File(['[{"short": "telemetry"}]'], 'mock.json', { type: 'application/json' });
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getAllByText(/UNKNOWN/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/INSUFFICIENT DATA/i)).toBeInTheDocument();
    });
  });

  it('renders safe error state on backend failure without tracebacks', async () => {
    (global.fetch as any).mockRejectedValue(new Error('Network Error'));

    render(
      <MemoryRouter initialEntries={['/vehicle/2?class=TANK']}>
        <Routes>
          <Route path="/vehicle/:vehicleId" element={<VehicleDashboard />} />
        </Routes>
      </MemoryRouter>
    );
    
    const input = screen.getByTestId('dataset-input');
    const file = new File(['[{"mock": "data"}]'], 'mock.json', { type: 'application/json' });
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText(/INFERENCE ERROR: Unable to process the telemetry dataset./i)).toBeInTheDocument();
      expect(screen.queryByText(/Traceback/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Python/i)).not.toBeInTheDocument();
    });
  });

});
