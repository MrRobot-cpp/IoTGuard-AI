import Link from "next/link";

const cards = [
  {
    href: "/devices",
    title: "Devices",
    description: "View live IoT device states and send commands to the gateway agent.",
    color: "border-cyan-500",
  },
  {
    href: "/attacks",
    title: "Attacks",
    description: "Run prompt injection payloads from the attack library against the agent.",
    color: "border-red-500",
  },
  {
    href: "/mitigations",
    title: "Mitigations",
    description: "Toggle input filtering, privilege separation, and LLM detection.",
    color: "border-yellow-500",
  },
  {
    href: "/results",
    title: "Results",
    description: "View attack logs and the before/after mitigation evaluation matrix.",
    color: "border-green-500",
  },
];

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Prompt Injection Attack Lab</h1>
      <p className="text-slate-400 mb-10">
        IoT Smart Home Gateway — security research environment
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className={`block rounded-xl border-l-4 ${card.color} bg-slate-900 p-6 hover:bg-slate-800 transition-colors`}
          >
            <h2 className="text-lg font-semibold mb-1">{card.title}</h2>
            <p className="text-sm text-slate-400">{card.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
