export interface TelemetryRecord {
  [key: string]: string | number;
}

export interface InferenceRequest {
  vehicle_id: string;
  vehicle_class: string;
  telemetry: TelemetryRecord[];
}

export interface AgentResult {
  [key: string]: any;
}

export interface FleetReadinessStatus {
  readiness_status: string;
  ready_count: number;
  attention_count: number;
  not_ready_count: number;
  unknown_count: number;
  ready_percentage: number;
}

export interface OrchestrationResult {
  request_id: string;
  timestamp: string;
  status: string;
  fleet_status?: FleetReadinessStatus;
  vehicle_results: Record<string, Record<string, AgentResult>>;
  execution_trace?: any[];
  error_state?: string;
}

export interface InferenceResultHistory {
  fusion_rul_hours: number | null;
  fusion_method: string;
}

export interface InferenceRunHistory {
  id: number;
  vehicle_id: string;
  vehicle_class: string;
  timestep_count: number;
  status: string;
  created_at: string;
  inference_result?: InferenceResultHistory;
  fleet_readiness?: FleetReadinessStatus;
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '';

export const inferVehicle = async (request: InferenceRequest): Promise<OrchestrationResult> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/inference/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    throw new Error(`API returned ${response.status}: ${await response.text()}`);
  }

  return await response.json();
};

export const getVehicleHistory = async (vehicleId: string): Promise<InferenceRunHistory[]> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/vehicles/${vehicleId}/inferences`);
  
  if (!response.ok) {
    if (response.status === 404) return [];
    throw new Error(`History API returned ${response.status}: ${await response.text()}`);
  }

  return await response.json();
};
