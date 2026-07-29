import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import type { Accent, Density, Intensity } from "@second-brain/types";
import { useSettings } from "../../hooks/useSettings";
import { SHORTCUT_REFERENCE } from "../../hooks/useBrainShortcuts";
import { AppShell } from "../../components/AppShell";
import { ACCENTS } from "../../lib/theme";
import { cn } from "../../lib/utils";

export function SettingsPage() {
  const { settings, update } = useSettings();
  const [cap, setCap] = useState(String(settings.default_cap));
  const [model, setModel] = useState(settings.model);
  const [capStatus, setCapStatus] = useState("");
  const [capErr, setCapErr] = useState(false);
  const [modelStatus, setModelStatus] = useState("");

  async function saveCap() {
    const n = Number(cap);
    if (!Number.isInteger(n) || n < 0) {
      setCapStatus("Cap must be a whole number ≥ 0.");
      setCapErr(true);
      return;
    }
    try {
      await update({ default_cap: n });
      setCapStatus(`Saved — feeds without their own n now cap at ${n}/day.`);
      setCapErr(false);
      toast.success(`default_cap = ${n}`);
    } catch (e) {
      setCapStatus(String(e));
      setCapErr(true);
    }
  }

  async function saveModel() {
    try {
      await update({ model: model.trim() });
      setModelStatus("Saved to .brain/config.json");
      toast.success("Model saved");
    } catch (e) {
      setModelStatus(String(e));
    }
  }

  return (
    <AppShell
      title="Settings"
      subtitle="feeds.toml · .brain/config.json · .brain/gui-prefs.json"
    >
      <div
        className="mx-auto flex w-full max-w-[720px] flex-col gap-4"
        style={{ padding: "var(--card-pad)" }}
      >
        <SettingsCard title="Feeder" desc="The global daily cap bounds how many items each feed may deposit per day.">
          <label className="block">
            <span className="label mb-1 block">Global daily cap</span>
            <input
              value={cap}
              inputMode="numeric"
              aria-invalid={capErr || undefined}
              aria-describedby="cap-status"
              onChange={(e) => setCap(e.target.value)}
              className="field max-w-[160px]"
            />
          </label>
          <CardFooter status={capStatus} error={capErr} id="cap-status" onSave={saveCap} label="Save cap" />
        </SettingsCard>

        <SettingsCard
          title="Claude model"
          desc="Model for unattended sync / digest / capture agents (bin/brain-run.sh)."
        >
          <label className="block">
            <span className="label mb-1 block">Model</span>
            <input
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="sonnet · opus · haiku — empty = default"
              aria-describedby="model-status"
              className="field max-w-[380px]"
            />
          </label>
          <CardFooter status={modelStatus} id="model-status" onSave={saveModel} label="Save model" />
        </SettingsCard>

        <SettingsCard title="Appearance" desc="Applies immediately and is saved for the next launch.">
          <div className="flex flex-col gap-3">
            <fieldset>
              <legend className="label mb-1.5">Accent</legend>
              <div className="flex flex-wrap gap-2">
                {(Object.keys(ACCENTS) as Accent[]).map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    aria-pressed={settings.accent === opt}
                    onClick={() => update({ accent: opt })}
                    className={cn(
                      "btn-press flex items-center gap-2 rounded-lg border px-3 py-1.5 font-mono text-[11px] font-semibold capitalize transition-colors",
                      settings.accent === opt
                        ? "border-[var(--ac)] bg-[rgba(var(--ac-rgb),0.12)] text-[var(--ink-bright)]"
                        : "border-[var(--border)] text-[var(--ink-dim)] hover:border-[var(--hair)] hover:text-[var(--ink)]",
                    )}
                  >
                    <span
                      aria-hidden="true"
                      className="h-3 w-3 rounded-full"
                      style={{ background: ACCENTS[opt].h }}
                    />
                    {opt}
                  </button>
                ))}
              </div>
            </fieldset>

            <SegmentRow<Density>
              label="Density"
              value={settings.density}
              options={["comfortable", "compact"]}
              onChange={(v) => update({ density: v })}
            />
            <SegmentRow<Intensity>
              label="Intensity"
              value={settings.intensity}
              options={["calm", "vivid"]}
              onChange={(v) => update({ intensity: v })}
            />
          </div>
        </SettingsCard>

        <SettingsCard title="Shortcuts" desc="Global — inert while typing in a form field.">
          <dl className="grid gap-2.5 sm:grid-cols-2">
            {SHORTCUT_REFERENCE.map(({ cap: key, desc }) => (
              <div key={key} className="flex items-start gap-2.5">
                <dt>
                  <kbd className="inline-flex shrink-0 rounded border border-[rgba(var(--ac-rgb),0.34)] bg-[rgba(var(--ac-rgb),0.16)] px-1.5 py-0.5 font-mono text-[10.5px] font-bold text-[var(--ac)]">
                    {key}
                  </kbd>
                </dt>
                <dd className="text-[12.5px] leading-snug text-[var(--ink-dim)]">{desc}</dd>
              </div>
            ))}
          </dl>
        </SettingsCard>
      </div>
    </AppShell>
  );
}

function SettingsCard({
  title,
  desc,
  children,
}: {
  title: string;
  desc?: string;
  children: ReactNode;
}) {
  return (
    <section className="surface p-4 sm:p-5">
      <h2 className="text-[13px] font-semibold tracking-tight text-[var(--ink-bright)]">{title}</h2>
      {desc ? <p className="mt-1 mb-4 text-[12.5px] leading-relaxed text-[var(--ink-dim2)]">{desc}</p> : null}
      {children}
    </section>
  );
}

function CardFooter({
  status,
  error,
  id,
  onSave,
  label,
}: {
  status: string;
  error?: boolean;
  id: string;
  onSave: () => void;
  label: string;
}) {
  return (
    <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
      <span
        id={id}
        role="status"
        className={cn("meta", error && "text-[var(--drop-ink)]")}
      >
        {status}
      </span>
      <button type="button" onClick={onSave} className="btn ml-auto">
        {label}
      </button>
    </div>
  );
}

function SegmentRow<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T;
  options: T[];
  onChange: (v: T) => void;
}) {
  return (
    <fieldset className="flex flex-wrap items-center gap-3">
      <legend className="label mb-1.5">{label}</legend>
      <div className="flex gap-0.5 rounded-lg border border-[var(--border)] bg-[var(--bg)] p-0.5">
        {options.map((opt) => (
          <button
            key={opt}
            type="button"
            aria-pressed={value === opt}
            onClick={() => onChange(opt)}
            className={cn(
              "btn-press rounded-md px-3 py-1.5 font-mono text-[11px] font-semibold capitalize transition-colors",
              value === opt
                ? "bg-[var(--ac)] text-[var(--ac-on)]"
                : "text-[var(--ink-dim)] hover:text-[var(--ink)]",
            )}
          >
            {opt}
          </button>
        ))}
      </div>
    </fieldset>
  );
}
