import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "IoTGuard-AI",
  description: "Prompt Injection Attack Lab for IoT AI Agents",
};

const nav = [
  { href: "/", label: "Dashboard" },
  { href: "/devices", label: "Devices" },
  { href: "/attacks", label: "Attacks" },
  { href: "/mitigations", label: "Mitigations" },
  { href: "/results", label: "Results" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 min-h-screen">
        <nav className="border-b border-slate-800 px-6 py-3 flex items-center gap-8">
          <span className="font-bold text-lg tracking-tight text-cyan-400">IoTGuard-AI</span>
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
