import type { Accent, Density, Intensity, Settings } from "@second-brain/types";

export const ACCENTS: Record<Accent, { h: string; on: string; rgb: string }> = {
  amber: { h: "#d8a04a", on: "#1a1916", rgb: "216,160,74" },
  indigo: { h: "#8aa0ff", on: "#10131f", rgb: "138,160,255" },
  emerald: { h: "#56c98e", on: "#0d1a12", rgb: "86,201,142" },
  mono: { h: "#cfc9bd", on: "#1a1916", rgb: "207,201,189" },
};

export function applyTheme(settings: Pick<Settings, "accent" | "density" | "intensity">) {
  const root = document.documentElement;
  const ac = ACCENTS[settings.accent] ?? ACCENTS.amber;
  root.style.setProperty("--ac", ac.h);
  root.style.setProperty("--ac-on", ac.on);
  root.style.setProperty("--ac-rgb", ac.rgb);
  root.dataset.density = settings.density;
  root.dataset.intensity = settings.intensity;
}

export const DEFAULT_SETTINGS: Settings = {
  default_cap: 5,
  model: "",
  accent: "amber",
  density: "comfortable",
  intensity: "calm",
};

export type { Accent, Density, Intensity };
