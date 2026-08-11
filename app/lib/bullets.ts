import type { Factor, ListingInput } from "./types";

const currency = new Intl.NumberFormat("es-PE", {
  style: "currency",
  currency: "PEN",
  maximumFractionDigits: 0,
});

/** Traduce un factor de SHAP a una oración en español, con el valor real del aviso. */
export function describeFactor(factor: Factor, listing: ListingInput, distKm: number): string {
  const verb = factor.contribution_pen >= 0 ? "suma" : "resta";
  const amount = currency.format(Math.abs(factor.contribution_pen));

  switch (factor.feature) {
    case "district":
      return `Estar en ${listing.district} ${verb} ${amount}`;
    case "area_m2":
      return `El área (${listing.area_m2} m²) ${verb} ${amount}`;
    case "bedrooms":
      return `Tener ${listing.bedrooms} dormitorio${listing.bedrooms === 1 ? "" : "s"} ${verb} ${amount}`;
    case "bathrooms":
      return `Tener ${listing.bathrooms} baño${listing.bathrooms === 1 ? "" : "s"} ${verb} ${amount}`;
    case "floor":
      return `Estar en el piso ${listing.floor} ${verb} ${amount}`;
    case "has_parking":
      return `${listing.has_parking ? "Tener" : "No tener"} cochera ${verb} ${amount}`;
    case "has_elevator":
      return `${listing.has_elevator ? "Tener" : "No tener"} ascensor ${verb} ${amount}`;
    case "is_furnished":
      return `${listing.is_furnished ? "Estar" : "No estar"} amoblado ${verb} ${amount}`;
    case "building_age_years":
      return `La antigüedad (${listing.building_age_years} años) ${verb} ${amount}`;
    case "dist_to_station_km": {
      const distLabel =
        distKm < 1 ? `${Math.round(distKm * 1000)} m` : `${distKm.toFixed(1)} km`;
      return `Estar a ${distLabel} de una estación de transporte ${verb} ${amount}`;
    }
    default:
      return `${factor.label} ${verb} ${amount}`;
  }
}
