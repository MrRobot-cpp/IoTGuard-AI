"use client";

interface Device {
  id: string;
  name: string;
  type: string;
  state: Record<string, unknown>;
  online: boolean;
}

// Keys where true = dangerous (red) and false = safe (green)
const DANGER_WHEN_TRUE = new Set(["triggered", "ajar"]);
// Keys where false = dangerous (red) and true = safe (green)
const DANGER_WHEN_FALSE = new Set(["locked", "armed", "on", "recording"]);

function boolColor(key: string, val: boolean): string {
  if (DANGER_WHEN_TRUE.has(key)) return val ? "text-red-400" : "text-green-400";
  if (DANGER_WHEN_FALSE.has(key)) return val ? "text-green-400" : "text-red-400";
  return val ? "text-green-400" : "text-slate-400";
}

export default function DeviceCard({ device }: { device: Device }) {
  const stateEntries = Object.entries(device.state);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium">{device.name}</span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${
            device.online ? "bg-green-900 text-green-300" : "bg-red-900 text-red-300"
          }`}
        >
          {device.online ? "online" : "offline"}
        </span>
      </div>
      <p className="text-xs text-slate-500 mb-3 uppercase tracking-wide">{device.type}</p>
      <div className="space-y-1">
        {stateEntries.map(([key, val]) => (
          <div key={key} className="flex justify-between text-sm">
            <span className="text-slate-400">{key}</span>
            <span className={`font-mono font-semibold ${typeof val === "boolean" ? boolColor(key, val) : "text-cyan-300"}`}>
              {String(val)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
