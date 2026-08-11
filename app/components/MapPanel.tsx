"use client";

import { useMemo } from "react";
import { CircleMarker, MapContainer, Marker, TileLayer, Tooltip, useMapEvents } from "react-leaflet";
import L from "leaflet";
import type { DistrictInfo } from "@/app/lib/types";

const LIMA_CENTER: [number, number] = [-12.05, -77.03];

const pinIcon = L.divIcon({
  className: "",
  html: `<div style="
    width: 22px; height: 22px; border-radius: 50% 50% 50% 0;
    background: #E6115E; border: 2px solid white;
    transform: rotate(-45deg);
    box-shadow: 0 1px 4px rgba(0,0,0,0.4);
  "></div>`,
  iconSize: [22, 22],
  iconAnchor: [11, 22],
});

function priceColor(value: number, min: number, max: number): string {
  const t = max > min ? (value - min) / (max - min) : 0.5;
  // Navy (barato) -> Magenta (caro), interpolación simple en RGB.
  const from = [10, 37, 89]; // #0A2559
  const to = [230, 17, 94]; // #E6115E
  const rgb = from.map((c, i) => Math.round(c + (to[i] - c) * t));
  return `rgb(${rgb.join(",")})`;
}

function ClickToMove({ onMove }: { onMove: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onMove(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

interface MapPanelProps {
  districts: DistrictInfo[];
  position: [number, number];
  onPositionChange: (lat: number, lon: number) => void;
}

export default function MapPanel({ districts, position, onPositionChange }: MapPanelProps) {
  const [min, max] = useMemo(() => {
    const values = districts.map((d) => d.median_price_per_m2_pen);
    return [Math.min(...values), Math.max(...values)];
  }, [districts]);

  return (
    <MapContainer
      center={LIMA_CENTER}
      zoom={11}
      scrollWheelZoom={false}
      className="h-80 w-full rounded-xl sm:h-96"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickToMove onMove={onPositionChange} />
      {districts.map((d) => (
        <CircleMarker
          key={d.district}
          center={[d.centroid_lat, d.centroid_lon]}
          radius={10}
          pathOptions={{
            color: "white",
            weight: 1,
            fillColor: priceColor(d.median_price_per_m2_pen, min, max),
            fillOpacity: 0.55,
          }}
        >
          <Tooltip>
            {d.district}: S/ {d.median_price_per_m2_pen.toFixed(0)} / m²
          </Tooltip>
        </CircleMarker>
      ))}
      <Marker
        position={position}
        icon={pinIcon}
        draggable
        eventHandlers={{
          dragend: (e) => {
            const marker = e.target as L.Marker;
            const { lat, lng } = marker.getLatLng();
            onPositionChange(lat, lng);
          },
        }}
      />
    </MapContainer>
  );
}
