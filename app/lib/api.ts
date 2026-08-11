import type {
  BaselinePredictResponse,
  DistrictInfo,
  ListingInput,
  PredictResponse,
} from "./types";

// Rutas relativas a propósito: en Vercel, Next.js y api/main.py comparten
// dominio (confirmado con un deploy real, ver next.config.ts). En local,
// next.config.ts las reescribe hacia la API vía rewrites.
async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${path} -> ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchDistricts(): Promise<DistrictInfo[]> {
  const res = await fetch("/districts");
  if (!res.ok) throw new Error(`/districts -> ${res.status}`);
  return res.json() as Promise<DistrictInfo[]>;
}

export function predict(listing: ListingInput): Promise<PredictResponse> {
  return postJson<PredictResponse>("/predict", listing);
}

export function predictBaseline(listing: ListingInput): Promise<BaselinePredictResponse> {
  return postJson<BaselinePredictResponse>("/predict/baseline", listing);
}
