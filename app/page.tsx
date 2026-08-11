"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import ListingForm from "@/app/components/ListingForm";
import WaterfallChart from "@/app/components/WaterfallChart";
import { fetchDistricts, predict, predictBaseline } from "@/app/lib/api";
import { describeFactor } from "@/app/lib/bullets";
import type { BaselinePredictResponse, DistrictInfo, ListingInput, PredictResponse } from "@/app/lib/types";

// Leaflet toca `window` al cargar: sin esto, el build de Next intenta
// renderizarlo en el servidor y truena.
const MapPanel = dynamic(() => import("@/app/components/MapPanel"), {
  ssr: false,
  loading: () => (
    <div className="h-80 w-full animate-pulse rounded-xl bg-slate-200 sm:h-96" />
  ),
});

const LIMA_CENTER: [number, number] = [-12.1211, -77.0294]; // Miraflores, default

const DEFAULT_LISTING: ListingInput = {
  district: "Miraflores",
  area_m2: 65,
  bedrooms: 2,
  bathrooms: 1,
  floor: 8,
  has_parking: true,
  has_elevator: true,
  is_furnished: false,
  building_age_years: 10,
  latitude: LIMA_CENTER[0],
  longitude: LIMA_CENTER[1],
};

const currency = new Intl.NumberFormat("es-PE", {
  style: "currency",
  currency: "PEN",
  maximumFractionDigits: 0,
});

export default function Home() {
  const [listing, setListing] = useState<ListingInput>(DEFAULT_LISTING);
  const [districts, setDistricts] = useState<DistrictInfo[]>([]);
  const [modelMode, setModelMode] = useState<"model" | "baseline">("model");
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [baseline, setBaseline] = useState<BaselinePredictResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDistricts()
      .then(setDistricts)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setLoading(true);
      Promise.all([predict(listing), predictBaseline(listing)])
        .then(([p, b]) => {
          setPrediction(p);
          setBaseline(b);
          setError(null);
        })
        .catch((e) => setError(String(e)))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(listing)]);

  const districtMedianTotal = useMemo(() => {
    const info = districts.find((d) => d.district === listing.district);
    return info ? info.median_price_per_m2_pen * listing.area_m2 : null;
  }, [districts, listing.district, listing.area_m2]);

  const activePrice = modelMode === "model" ? prediction?.predicted_price_pen : baseline?.predicted_price_pen;

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-lg font-semibold text-navy">
          ¿Cuánto vale tu alquiler? <span className="text-slate-400">· Lima Metropolitana</span>
        </h1>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 p-6 lg:flex-row">
        <aside className="w-full shrink-0 rounded-2xl border border-slate-200 bg-white p-5 lg:w-80">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
            Características del departamento
          </h2>
          {districts.length > 0 && (
            <ListingForm value={listing} districts={districts} onChange={(patch) => setListing((prev) => ({ ...prev, ...patch }))} />
          )}
        </aside>

        <section className="flex flex-1 flex-col gap-6">
          {error && (
            <div className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
              No se pudo conectar con la API: {error}
            </div>
          )}

          <div className="rounded-2xl border border-slate-200 bg-white p-6">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">Precio estimado</span>
              <ModelToggle mode={modelMode} onChange={setModelMode} />
            </div>

            <p
              className={`text-5xl font-bold tabular-nums text-navy transition-opacity ${loading ? "opacity-40" : "opacity-100"}`}
            >
              {activePrice != null ? currency.format(activePrice) : "—"}
            </p>

            {modelMode === "model" && prediction && (
              <p className="mt-1 text-sm text-slate-500">
                Referencia: {currency.format(prediction.confidence_interval[0])} —{" "}
                {currency.format(prediction.confidence_interval[1])} (± error típico del modelo)
              </p>
            )}

            {districtMedianTotal != null && (
              <p className="mt-1 text-sm text-slate-500">
                La mediana en {listing.district} para esta área es {currency.format(districtMedianTotal)}
              </p>
            )}

            {prediction && baseline && (
              <p className="mt-3 border-t border-slate-100 pt-3 text-xs text-slate-400">
                MAE modelo tonto: ~{currency.format(baseline.mae_pen)} · MAE modelo entrenado: ~
                {currency.format(prediction.mae_pen)}
              </p>
            )}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">
              Ubicación
            </h2>
            {districts.length > 0 && (
              <MapPanel
                districts={districts}
                position={[listing.latitude, listing.longitude]}
                onPositionChange={(lat, lon) => setListing((prev) => ({ ...prev, latitude: lat, longitude: lon }))}
              />
            )}
            <p className="mt-2 text-xs text-slate-500">
              Arrastra el pin o haz clic en el mapa. Los círculos son el precio/m² mediano por
              distrito.
              {prediction && ` A ${prediction.dist_to_station_km.toFixed(2)} km de la estación más cercana.`}
            </p>
          </div>

          {modelMode === "model" && prediction && (
            <div className="rounded-2xl border border-slate-200 bg-white p-5">
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">
                ¿Por qué este precio?
              </h2>
              <WaterfallChart baseValue={prediction.base_value_pen} factors={prediction.all_factors} />
              <ul className="mt-4 flex flex-col gap-1.5 border-t border-slate-100 pt-4 text-sm text-navy">
                {prediction.top_factors.map((f) => (
                  <li key={f.feature} className="flex gap-2">
                    <span className="text-magenta">•</span>
                    {describeFactor(f, listing, prediction.dist_to_station_km)}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {modelMode === "baseline" && (
            <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-500">
              El modelo tonto no explica sus predicciones: solo usa la mediana de precio/m² del
              distrito, sin ver cochera, ascensor, distancia a estaciones ni nada más. Por eso no
              hay gráfico acá — esa es justamente la diferencia con el modelo de verdad.
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function ModelToggle({
  mode,
  onChange,
}: {
  mode: "model" | "baseline";
  onChange: (mode: "model" | "baseline") => void;
}) {
  return (
    <div className="flex rounded-full border border-slate-200 bg-slate-50 p-0.5 text-xs">
      <button
        type="button"
        onClick={() => onChange("baseline")}
        className={`rounded-full px-3 py-1 font-medium transition-colors ${
          mode === "baseline" ? "bg-navy text-white" : "text-slate-500"
        }`}
      >
        Modelo tonto
      </button>
      <button
        type="button"
        onClick={() => onChange("model")}
        className={`rounded-full px-3 py-1 font-medium transition-colors ${
          mode === "model" ? "bg-magenta text-white" : "text-slate-500"
        }`}
      >
        Modelo entrenado
      </button>
    </div>
  );
}
