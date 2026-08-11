"use client";

import type { DistrictInfo, ListingInput } from "@/app/lib/types";

type FormFields = Omit<ListingInput, "latitude" | "longitude">;

interface ListingFormProps {
  value: FormFields;
  districts: DistrictInfo[];
  onChange: (patch: Partial<FormFields>) => void;
}

function Field({
  label,
  help,
  children,
}: {
  label: string;
  help: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-navy">{label}</span>
      {children}
      <span className="mt-1 block text-xs text-slate-500">{help}</span>
    </label>
  );
}

const inputClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-navy focus:border-magenta focus:outline-none focus:ring-1 focus:ring-magenta";

export default function ListingForm({ value, districts, onChange }: ListingFormProps) {
  return (
    <div className="flex flex-col gap-4">
      <Field label="Distrito" help="Define el nivel de precio base de la zona.">
        <select
          className={inputClass}
          value={value.district}
          onChange={(e) => onChange({ district: e.target.value })}
        >
          {districts.map((d) => (
            <option key={d.district} value={d.district}>
              {d.district}
            </option>
          ))}
        </select>
      </Field>

      <Field label={`Área: ${value.area_m2} m²`} help="Área techada del departamento.">
        <input
          type="range"
          min={20}
          max={300}
          step={1}
          value={value.area_m2}
          onChange={(e) => onChange({ area_m2: Number(e.target.value) })}
          className="w-full accent-magenta"
        />
      </Field>

      <div className="grid grid-cols-2 gap-3">
        <Field label="Dormitorios" help="Entre 1 y 5.">
          <input
            type="number"
            min={1}
            max={5}
            className={inputClass}
            value={value.bedrooms}
            onChange={(e) => onChange({ bedrooms: Number(e.target.value) })}
          />
        </Field>
        <Field label="Baños" help="Entre 1 y 4.">
          <input
            type="number"
            min={1}
            max={4}
            className={inputClass}
            value={value.bathrooms}
            onChange={(e) => onChange({ bathrooms: Number(e.target.value) })}
          />
        </Field>
      </div>

      <Field label={`Piso: ${value.floor}`} help="Piso en el que está el departamento.">
        <input
          type="range"
          min={1}
          max={20}
          step={1}
          value={value.floor}
          onChange={(e) => onChange({ floor: Number(e.target.value) })}
          className="w-full accent-magenta"
        />
      </Field>

      <Field
        label={`Antigüedad: ${value.building_age_years} años`}
        help="Años desde que se construyó el edificio."
      >
        <input
          type="range"
          min={0}
          max={45}
          step={1}
          value={value.building_age_years}
          onChange={(e) => onChange({ building_age_years: Number(e.target.value) })}
          className="w-full accent-magenta"
        />
      </Field>

      <div className="flex flex-col gap-2 border-t border-slate-200 pt-3">
        <Checkbox
          label="Cochera"
          help="¿El departamento tiene cochera propia?"
          checked={value.has_parking}
          onChange={(v) => onChange({ has_parking: v })}
        />
        <Checkbox
          label="Ascensor"
          help="¿El edificio tiene ascensor?"
          checked={value.has_elevator}
          onChange={(v) => onChange({ has_elevator: v })}
        />
        <Checkbox
          label="Amoblado"
          help="¿Se alquila amoblado?"
          checked={value.is_furnished}
          onChange={(v) => onChange({ is_furnished: v })}
        />
      </div>
    </div>
  );
}

function Checkbox({
  label,
  help,
  checked,
  onChange,
}: {
  label: string;
  help: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-start gap-2" title={help}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-1 h-4 w-4 accent-magenta"
      />
      <span className="text-sm text-navy">{label}</span>
    </label>
  );
}
