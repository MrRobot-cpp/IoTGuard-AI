"use client";

interface MatrixRow {
  mitigation: string;
  category: string;
  total: number;
  expected_total?: number;
  attack_successes: number;
  attack_success_rate: number;
  blocked?: number;
  block_rate?: number;
  mitigation_blocked?: number;
  llm_refused?: number;
  /** @deprecated API alias */
  defended?: number;
  defend_rate?: number;
  resisted?: number;
}

export default function ScoreMatrix({ rows }: { rows: MatrixRow[] }) {
  if (!rows.length) {
    return <p className="text-slate-500 text-sm">No evaluation data yet. Run attacks first.</p>;
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-500">
        Each row sums to Runs:{" "}
        <span className="text-green-400">Blocked</span> (mitigation + LLM refused) +{" "}
        <span className="text-red-400">Attacks OK</span> (injection worked). Hover Blocked for
        breakdown. One result per payload (latest run).
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="text-left text-slate-400 border-b border-slate-800">
              <th className="py-2 pr-4">Mitigation</th>
              <th className="py-2 pr-4">Category</th>
              <th className="py-2 pr-4 text-right">Runs</th>
              <th className="py-2 pr-4 text-right">Blocked</th>
              <th className="py-2 pr-4 text-right">Attacks OK</th>
              <th className="py-2 pr-4 text-right">Attack %</th>
              <th className="py-2 text-right">Block %</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => {
              const expected = row.expected_total ?? row.total;
              const runsLabel =
                row.total === expected ? String(row.total) : `${row.total}/${expected}`;
              const mitigationBlocked = row.mitigation_blocked ?? 0;
              const llmRefused =
                row.llm_refused ??
                row.resisted ??
                Math.max(0, row.total - mitigationBlocked - row.attack_successes);
              const blocked =
                row.blocked ??
                row.defended ??
                mitigationBlocked + llmRefused;
              const blockRate =
                row.block_rate ?? row.defend_rate ?? (row.total ? blocked / row.total : 0);
              const attackRate = row.attack_success_rate ?? 0;

              return (
                <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="py-2 pr-4 font-mono text-xs text-cyan-300">{row.mitigation}</td>
                  <td className="py-2 pr-4 text-slate-300">{row.category}</td>
                  <td className="py-2 pr-4 text-right">{runsLabel}</td>
                  <td
                    className="py-2 pr-4 text-right text-green-400"
                    title={`Mitigation blocked: ${mitigationBlocked} · LLM refused: ${llmRefused}`}
                  >
                    {blocked}
                  </td>
                  <td className="py-2 pr-4 text-right text-red-400">{row.attack_successes}</td>
                  <td className="py-2 pr-4 text-right text-red-400/80">
                    {(attackRate * 100).toFixed(0)}%
                  </td>
                  <td className="py-2 text-right">
                    <span
                      className={`font-semibold ${
                        blockRate >= 0.8
                          ? "text-green-400"
                          : blockRate >= 0.5
                            ? "text-yellow-400"
                            : "text-red-400"
                      }`}
                    >
                      {(blockRate * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
