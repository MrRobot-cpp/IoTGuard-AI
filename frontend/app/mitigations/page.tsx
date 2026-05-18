"use client";

export default function MitigationsPage() {
  const mitigations = [
    {
      id: "input_filter",
      name: "Mitigation 1 — Input / Output Filter",
      color: "border-yellow-500",
      description:
        "Scans user input and LLM output for known injection patterns using regex and keyword matching. Fast, zero LLM cost, but limited to known patterns.",
      strengths: ["No API calls required", "Deterministic", "Instant"],
      weaknesses: ["Pattern evasion possible", "Cannot catch novel attacks"],
    },
    {
      id: "privilege_separation",
      name: "Mitigation 2 — Privilege-Separated Prompt",
      color: "border-cyan-500",
      description:
        "Splits the system prompt into an immutable CORE POLICY layer and a user-facing layer. Sensor data is tagged as read-only so injected instructions are ignored.",
      strengths: ["Architectural — hard to override", "Works against indirect injection"],
      weaknesses: ["Model may still comply", "No guarantee of immutability"],
    },
    {
      id: "llm_detector",
      name: "Mitigation 3 — LLM Injection Detector",
      color: "border-purple-500",
      description:
        "A secondary LLM classifier screens the input before it reaches the main agent. Catches novel phrasing that regex cannot.",
      strengths: ["Semantic understanding", "Catches novel attacks"],
      weaknesses: ["Extra API cost per request", "Can produce false positives"],
    },
    {
      id: "constitutional_judge",
      name: "Extension — Constitutional AI Judge",
      color: "border-green-500",
      description:
        "A safety judge LLM reviews every proposed tool call before execution. Acts as a veto layer even after injection bypasses the main agent.",
      strengths: ["Post-generation safety net", "Action-level granularity"],
      weaknesses: ["Latency overhead", "Judge can also be fooled"],
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold">Mitigations</h1>

      <div className="space-y-4">
        {mitigations.map((m) => (
          <div key={m.id} className={`bg-slate-900 border-l-4 ${m.color} rounded-xl p-5`}>
            <h2 className="font-semibold mb-1">{m.name}</h2>
            <p className="text-sm text-slate-400 mb-3">{m.description}</p>
            <div className="flex gap-8 text-sm">
              <div>
                <p className="text-green-400 font-medium mb-1">Strengths</p>
                <ul className="space-y-0.5 text-slate-400">
                  {m.strengths.map((s) => <li key={s}>+ {s}</li>)}
                </ul>
              </div>
              <div>
                <p className="text-red-400 font-medium mb-1">Weaknesses</p>
                <ul className="space-y-0.5 text-slate-400">
                  {m.weaknesses.map((w) => <li key={w}>- {w}</li>)}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
