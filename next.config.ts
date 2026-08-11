import type { NextConfig } from "next";

// En Vercel, Next.js y api/main.py conviven en el mismo deployment: un fetch
// relativo a "/predict" ya llega directo a la función Python (confirmado
// desplegando un spike real — Vercel no reescribe ni recorta esas rutas).
// Localmente corren como dos procesos separados (`make app` en :3000, `make
// serve` en :8000), así que en dev reescribimos esas rutas puntuales hacia
// la API para que el mismo código de fetch funcione sin cambios en ambos
// entornos.
const API_PROXY_PATHS = ["/health", "/predict", "/predict/baseline", "/districts"];

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV !== "development") {
      return [];
    }
    const apiUrl = process.env.API_URL ?? "http://localhost:8000";
    return API_PROXY_PATHS.map((path) => ({
      source: path,
      destination: `${apiUrl}${path}`,
    }));
  },
};

export default nextConfig;
