"use client";

import { useEffect, useState } from "react";
import { getAttackLibrary, runAllAttacks } from "@/lib/api";
import PayloadEditor from "@/components/PayloadEditor";

export default function AttacksPage() {
  const [library, setLibrary] = useState<any>({});
  const [category, setCategory] = useState<string>("direct");
  const [mitigation, setMitigation] = useState("none");
  const [useJudge, setUseJudge] = useState(false);
  const [lastResult, setLastResult] = useState<any>(null);
  const [runningAll, setRunningAll] = useState(false);

  useEffect(() => {
    getAttackLibrary().then((data) => setLibrary(data as any));
  }, []);

  async function handleRunAll() {
    setRunningAll(true);
    try {
      const results = await runAllAttacks(category, mitigation, useJudge);
      setLastResult(results);
    } finally {
      setRunningAll(false);
    }
  }

  const payloads: any[] = library[category] ?? [];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Attack Library</h1>

      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex gap-2">
          {["direct", "indirect", "multiturn"].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                category === cat ? "bg-red-700 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <select
          value={mitigation}
          onChange={(e) => setMitigation(e.target.value)}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm"
        >
          <option value="none">No Mitigation</option>
          <option value="input_filter">Input Filter</option>
          <option value="privilege_separation">Privilege Separation</option>
          <option value="llm_detector">LLM Detector</option>
        </select>

        <label className="flex items-center gap-2 text-sm text-slate-400">
          <input type="checkbox" checked={useJudge} onChange={(e) => setUseJudge(e.target.checked)} />
          Constitutional Judge
        </label>

        <button
          onClick={handleRunAll}
          disabled={runningAll}
          className="ml-auto px-5 py-2 rounded-lg bg-red-900 hover:bg-red-800 disabled:opacity-50 text-sm font-medium transition-colors"
        >
          {runningAll ? "Running..." : `Run All ${category}`}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {payloads.map((p: any) => (
          <PayloadEditor
            key={p.id}
            payload={p}
            mitigation={mitigation}
            useJudge={useJudge}
            onResult={setLastResult}
          />
        ))}
      </div>

      {lastResult && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h2 className="text-sm font-semibold mb-2 text-slate-400">Last Result</h2>
          <pre className="text-xs font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(lastResult, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
