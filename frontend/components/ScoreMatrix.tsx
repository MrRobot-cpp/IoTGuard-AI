"use client";

interface MatrixRow {
  mitigation: string;
  category: string;
  total: number;
  attack_successes: number;
  attack_success_rate: number;
  blocked: number;
  block_rate: number;
}

export default function ScoreMatrix({ rows }: { rows: MatrixRow[] }) {
  if (!rows.length) {
    return <p className="text-slate-500 text-sm">No evaluation data yet. Run attacks first.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="text-left text-slate-400 border-b border-slate-800">
            <th className="py-2 pr-4">Mitigation</th>
            <th className="py-2 pr-4">Category</th>
            <th className="py-2 pr-4 text-right">Total</th>
            <th className="py-2 pr-4 text-right">Succeeded</th>
            <th className="py-2 pr-4 text-right">Blocked</th>
            <th className="py-2 text-right">Block Rate</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
              <td className="py-2 pr-4 font-mono text-xs text-cyan-300">{row.mitigation}</td>
              <td className="py-2 pr-4 text-slate-300">{row.category}</td>
              <td className="py-2 pr-4 text-right">{row.total}</td>
              <td className="py-2 pr-4 text-right text-red-400">{row.attack_successes}</td>
              <td className="py-2 pr-4 text-right text-green-400">{row.blocked}</td>
              <td className="py-2 text-right">
                <span
                  className={`font-semibold ${
                    row.block_rate >= 0.8
                      ? "text-green-400"
                      : row.block_rate >= 0.5
                      ? "text-yellow-400"
                      : "text-red-400"
                  }`}
                >
                  {(row.block_rate * 100).toFixed(0)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
