"use client";

import { useState } from "react";
import { runPayload } from "@/lib/api";

interface Payload {
  id: string;
  name: string;
  category: string;
  description: string;
  payload?: string;
  turns?: string[];
  risk: string;
}

interface Props {
  payload: Payload;
  mitigation: string;
  useJudge: boolean;
  onResult: (result: unknown) => void;
}

export default function PayloadEditor({ payload, mitigation, useJudge, onResult }: Props) {
  const [loading, setLoading] = useState(false);

  const riskColor: Record<string, string> = {
    high: "text-red-400",
    medium: "text-yellow-400",
    low: "text-green-400",
  };

  async function run() {
    setLoading(true);
    try {
      const result = await runPayload(payload.id, mitigation, useJudge);
      onResult(result);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <div className="flex items-start justify-between mb-2">
        <div>
          <span className="text-xs font-mono text-slate-500 mr-2">{payload.id}</span>
          <span className="font-medium">{payload.name}</span>
        </div>
        <span className={`text-xs font-semibold uppercase ${riskColor[payload.risk] ?? "text-slate-400"}`}>
          {payload.risk}
        </span>
      </div>
      <p className="text-sm text-slate-400 mb-3">{payload.description}</p>
      <div className="bg-slate-950 rounded p-3 mb-3 text-xs font-mono text-slate-300 max-h-24 overflow-y-auto">
        {payload.turns
          ? payload.turns.map((t, i) => <div key={i}><span className="text-slate-600">T{i + 1}: </span>{t}</div>)
          : payload.payload}
      </div>
      <button
        onClick={run}
        disabled={loading}
        className="w-full py-2 rounded-lg bg-red-700 hover:bg-red-600 disabled:opacity-50 text-sm font-medium transition-colors"
      >
        {loading ? "Running..." : "Run Attack"}
      </button>
    </div>
  );
}
