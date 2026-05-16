const BASE = "/api";

async function errorDetail(res: Response): Promise<string> {
  try {
    const data = await res.json();
    const d = data?.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) return d.map((x: { msg?: string }) => x.msg).filter(Boolean).join("; ");
    if (d && typeof d === "object") return JSON.stringify(d);
    if (data?.message) return String(data.message);
  } catch {
    /* ignore */
  }
  return String(res.status);
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${await errorDetail(res)}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${await errorDetail(res)}`);
  return res.json();
}

async function del<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`);
  return res.json();
}

// Gateway
export const getDevices = () => get("/gateway/devices");
export const getSensors = (inject?: string) =>
  get(`/gateway/sensors${inject ? `?inject=${encodeURIComponent(inject)}` : ""}`);
export const sendCommand = (message: string, mitigation: string, use_judge: boolean, sensor_inject?: string) =>
  post("/gateway/command", { message, mitigation, use_judge, sensor_inject });
export const resetDevices = () => post("/gateway/reset", {});

export const getSimulationSummary = () => get("/gateway/simulation");
export const getLlmHealth = () => get("/gateway/llm/health");
export const runSensorLlmManage = (opts?: {
  goal?: string;
  poll_sensors_first?: boolean;
  apply_plan?: boolean;
}) => post("/gateway/llm/manage", opts ?? {});

// Attacks
export const getAttackLibrary = () => get("/attacks/library");
export const runPayload = (payload_id: string, mitigation: string, use_judge: boolean) =>
  post("/attacks/run", { payload_id, mitigation, use_judge });
export const runAllAttacks = (category: string | null, mitigation: string, use_judge: boolean) =>
  post("/attacks/run-all", { category, mitigation, use_judge });

// Mitigations
export const getMitigations = () => get("/mitigations/list");
export const testFilter = (text: string) => post("/mitigations/test-filter", { text });
export const testDetector = (text: string) => post("/mitigations/test-detector", { text });

// Results
export const getLogs = (limit?: number) => get(`/results/logs${limit ? `?limit=${limit}` : ""}`);
export const getMatrix = () => get("/results/matrix");
export const clearLogs = () => del("/results/clear");
