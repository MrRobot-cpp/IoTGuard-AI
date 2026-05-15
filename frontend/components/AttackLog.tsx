"use client";

interface LogEntry {
  id: number;
  payload_id: string;
  category: string;
  payload: string;
  llm_response: string;
  success: boolean;
  mitigation_active: string;
  timestamp: string;
}

export default function AttackLog({ entries }: { entries: LogEntry[] }) {
  if (!entries.length) {
    return <p className="text-slate-500 text-sm">No attack logs yet.</p>;
  }

  return (
    <div className="space-y-3">
      {entries.map((e) => (
        <div key={e.id} className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-xs font-mono text-slate-400">{e.payload_id}</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
              {e.category}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded-full ${
                e.success
                  ? "bg-red-900 text-red-300"
                  : "bg-green-900 text-green-300"
              }`}
            >
              {e.success ? "ATTACKED" : "BLOCKED"}
            </span>
            <span className="text-xs text-slate-600 ml-auto">{e.mitigation_active}</span>
          </div>
          <p className="text-xs text-slate-500 font-mono truncate mb-1">{e.payload}</p>
          <p className="text-sm text-slate-300">{e.llm_response}</p>
        </div>
      ))}
    </div>
  );
}
