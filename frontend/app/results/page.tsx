"use client";

import { useEffect, useState } from "react";
import { getLogs, getMatrix, clearLogs } from "@/lib/api";
import AttackLog from "@/components/AttackLog";
import ScoreMatrix from "@/components/ScoreMatrix";

export default function ResultsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [matrix, setMatrix] = useState<any[]>([]);
  const [tab, setTab] = useState<"matrix" | "logs">("matrix");

  async function refresh() {
    const [l, m] = await Promise.all([getLogs(100), getMatrix()]);
    setLogs(l as any[]);
    setMatrix(m as any[]);
  }

  useEffect(() => { refresh(); }, []);

  async function handleClear() {
    await clearLogs();
    await refresh();
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Results</h1>
        <div className="flex gap-3">
          <button onClick={refresh} className="text-sm px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors">
            Refresh
          </button>
          <button onClick={handleClear} className="text-sm px-4 py-2 rounded-lg bg-red-900 hover:bg-red-800 transition-colors">
            Clear Logs
          </button>
        </div>
      </div>

      <div className="flex gap-2">
        {(["matrix", "logs"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              tab === t ? "bg-cyan-700 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            {t === "matrix" ? "Evaluation Matrix" : "Attack Logs"}
          </button>
        ))}
      </div>

      {tab === "matrix" && <ScoreMatrix rows={matrix} />}
      {tab === "logs" && <AttackLog entries={logs} />}
    </div>
  );
}
