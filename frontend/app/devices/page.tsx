"use client";

import { useEffect, useState } from "react";
import {
  getDevices,
  getSensors,
  sendCommand,
  resetDevices,
  getLlmHealth,
  runSensorLlmManage,
} from "@/lib/api";
import DeviceCard from "@/components/DeviceCard";

export default function DevicesPage() {
  const [devices, setDevices] = useState<any[]>([]);
  const [sensors, setSensors] = useState<any[]>([]);
  const [command, setCommand] = useState("");
  const [mitigation, setMitigation] = useState("none");
  const [useJudge, setUseJudge] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [llmHealth, setLlmHealth] = useState<any>(null);
  const [llmResult, setLlmResult] = useState<any>(null);
  const [commandError, setCommandError] = useState<string | null>(null);

  async function refresh() {
    const [d, s] = await Promise.all([getDevices(), getSensors()]);
    setDevices(d as any[]);
    setSensors(s as any[]);
  }

  useEffect(() => {
    refresh();
    getLlmHealth().then(setLlmHealth).catch(() => setLlmHealth(null));
  }, []);

  async function handleCommand() {
    setLoading(true);
    setCommandError(null);
    try {
      const result = await sendCommand(command, mitigation, useJudge);
      setResponse(result);
      await refresh();
    } catch (err) {
      setCommandError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    await resetDevices();
    await refresh();
  }

  async function handleLlmManage() {
    setLoading(true);
    try {
      const result = await runSensorLlmManage({
        poll_sensors_first: true,
        apply_plan: true,
      });
      setLlmResult(result);
      await refresh();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Live Devices</h1>
        <div className="flex gap-2">
          <button
            onClick={handleLlmManage}
            disabled={loading}
            className="text-sm px-4 py-2 rounded-lg bg-violet-800 hover:bg-violet-700 disabled:opacity-50 transition-colors"
          >
            Ollama: Manage Sensors
          </button>
          <button
            onClick={handleReset}
            className="text-sm px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            Reset All
          </button>
        </div>
      </div>

      {llmHealth && (
        <p className="text-xs text-slate-500">
          Ollama: {llmHealth.ok ? "connected" : "offline"}
          {llmHealth.models?.length
            ? ` · models: ${llmHealth.models.join(", ")}`
            : " · pull a model: ollama pull llama3.2"}
        </p>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {devices.map((d) => (
          <DeviceCard key={d.id} device={d} />
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Sensor Readings (simulation hub)</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {sensors.map((s) => (
            <div key={s.sensor_id} className="bg-slate-900 rounded-lg p-3 text-sm">
              <span className="text-slate-400">{s.sensor_id}: </span>
              <span className="font-mono text-cyan-300">
                {String(s.value)}
                {s.unit}
              </span>
            </div>
          ))}
        </div>
      </div>

      {llmResult && (
        <div className="bg-slate-900 border border-violet-900 rounded-xl p-4 text-sm space-y-2">
          <p className="text-violet-300 font-medium">Ollama sensor plan applied</p>
          <pre className="text-xs text-slate-400 overflow-auto">
            {JSON.stringify(llmResult.plan, null, 2)}
          </pre>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-3">Send Command</h2>
        <div className="space-y-3">
          <textarea
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="e.g. Turn on the living room light"
            rows={3}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm resize-none focus:outline-none focus:border-cyan-500"
          />
          <div className="flex gap-4 items-center flex-wrap">
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
              <input
                type="checkbox"
                checked={useJudge}
                onChange={(e) => setUseJudge(e.target.checked)}
              />
              Constitutional Judge
            </label>
            <button
              onClick={handleCommand}
              disabled={loading || !command.trim()}
              className="px-6 py-2 rounded-lg bg-cyan-700 hover:bg-cyan-600 disabled:opacity-50 text-sm font-medium transition-colors"
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>

        {commandError && (
          <div className="mt-4 bg-red-950 border border-red-800 rounded-xl p-4">
            <p className="text-sm text-red-300">{commandError}</p>
          </div>
        )}

        {response && (
          <div className="mt-4 bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
            <p className="text-sm text-slate-300">{response.response}</p>
            {response.tool_calls?.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-1">Tool calls:</p>
                {response.tool_calls.map((tc: any, i: number) => (
                  <div key={i} className="text-xs font-mono text-cyan-300">
                    {tc.tool}({JSON.stringify(tc.args)}) → {JSON.stringify(tc.result)}
                  </div>
                ))}
              </div>
            )}
            {response.error && (
              <p className="text-xs text-amber-400">Ollama setup required — see message above</p>
            )}
            {response.blocked && (
              <p className="text-xs text-red-400">Blocked by mitigation</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
