export type District = string;

export interface ListingInput {
  district: District;
  area_m2: number;
  bedrooms: number;
  bathrooms: number;
  floor: number;
  has_parking: boolean;
  has_elevator: boolean;
  is_furnished: boolean;
  building_age_years: number;
  latitude: number;
  longitude: number;
}

export interface Factor {
  feature: string;
  label: string;
  contribution_pen: number;
}

export interface PredictResponse {
  predicted_price_pen: number;
  model_version: string;
  confidence_interval: [number, number];
  base_value_pen: number;
  dist_to_station_km: number;
  top_factors: Factor[];
  all_factors: Factor[];
  mae_pen: number;
}

export interface BaselinePredictResponse {
  predicted_price_pen: number;
  model_version: string;
  mae_pen: number;
}

export interface DistrictInfo {
  district: string;
  median_price_per_m2_pen: number;
  centroid_lat: number;
  centroid_lon: number;
}
