"use client";

import type { Factor } from "@/app/lib/types";

const currency = new Intl.NumberFormat("es-PE", {
  style: "currency",
  currency: "PEN",
  maximumFractionDigits: 0,
});

interface WaterfallChartProps {
  baseValue: number;
  factors: Factor[];
}

export default function WaterfallChart({ baseValue, factors }: WaterfallChartProps) {
  const maxAbs = Math.max(...factors.map((f) => Math.abs(f.contribution_pen)), 1);

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs text-slate-500">
        Punto de partida: precio promedio de todos los avisos ({currency.format(baseValue)}).
        Cada barra muestra cuánto suma o resta esa característica.
      </p>
      {factors.map((f) => {
        const pct = (Math.abs(f.contribution_pen) / maxAbs) * 50;
        const isPositive = f.contribution_pen >= 0;
        return (
          <div key={f.feature} className="flex items-center gap-3 text-sm">
            <span className="w-28 shrink-0 truncate text-navy">{f.label}</span>
            <div className="relative h-5 flex-1 bg-slate-100 rounded">
              <div className="absolute inset-y-0 left-1/2 w-px bg-slate-300" />
              <div
                className={`absolute inset-y-0 rounded ${
                  isPositive ? "bg-magenta left-1/2" : "bg-blue right-1/2"
                }`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span
              className={`w-20 shrink-0 text-right font-medium ${
                isPositive ? "text-magenta" : "text-blue"
              }`}
            >
              {isPositive ? "+" : ""}
              {currency.format(f.contribution_pen)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
