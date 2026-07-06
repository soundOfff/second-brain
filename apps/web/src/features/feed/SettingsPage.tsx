import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import type { Accent, Density, Intensity } from "@second-brain/types";
import { useSettings } from "../../hooks/useSettings";
import { SHORTCUT_REFERENCE } from "../../hooks/useBrainShortcuts";
import { cn } from "../../lib/utils";

export function SettingsPage() {
  const { settings, update } = useSettings();
  const [cap, setCap] = useState(String(settings.default_cap));
  const [model, setModel] = useState(settings.model);
  const [capStatus, setCapStatus] = useState("");
  const [modelStatus, setModelStatus] = useState("");

  async function saveCap() {
    const n = Number(cap);
    if (!Number.isInteger(n) || n < 0) {
      setCapStatus("Cap must be a whole number ≥ 0.");
      return;
    }
    try {
      await update({ default_cap: n });
      setCapStatus(`Saved — feeds without their own n now cap at ${n}/day.`);
      toast.success(`default_cap = ${n}`);
    } catch (e) {
      setCapStatus(String(e));
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
    <div className="scroll min-h-0 flex-1 overflow-y-auto" style={{ padding: "var(--card-pad)" }}>
      <header className="mb-5" style={{ padding: "var(--head-pad)" }}>
        <h2 className="font-bold text-[var(--ink-bright)]" style={{ fontSize: "var(--title-size)" }}>
          Settings
        </h2>
        <p className="mt-1 font-mono text-[10px] text-[var(--ink-faint)]">
          feeds.toml (feeder) · .brain/config.json (model) · .brain/gui-prefs.json (appearance)
        </p>
      </header>

      <SettingsCard title="FEEDER">
        <p className="mb-3 text-[12px] leading-relaxed text-[var(--ink-dim2)]">
          The global daily cap bounds how many items each feed may deposit per day.
        </p>
        <label className="block text-[11px] text-[var(--ink-dim)]">
          <span className="mb-1 block font-mono text-[9px] font-bold text-[var(--ink-faint)]">Global daily cap</span>
          <input
            value={cap}
            onChange={(e) => setCap(e.target.value)}
            className="w-full max-w-xs rounded border border-[var(--border)] bg-[var(--bg)] px-2.5 py-1.5 font-mono text-[11px] outline-none focus:border-[var(--ac)]"
          />
        </label>
        <div className="mt-3 flex items-center justify-between gap-4">
          <span className="font-mono text-[10px] text-[var(--ink-faint)]">{capStatus}</span>
          <button type="button" onClick={saveCap} className="btn-press rounded-lg border border-[var(--rail-neutral)] px-3 py-1.5 font-mono text-[11px] font-semibold text-[var(--ink-muted)] hover:border-[var(--ac)] hover:text-[var(--ac)]">
            Save cap
          </button>
        </div>
      </SettingsCard>

      <SettingsCard title="CLAUDE MODEL">
        <p className="mb-3 text-[12px] leading-relaxed text-[var(--ink-dim2)]">
          Model for unattended sync / digest / capture agents (bin/brain-run.sh).
        </p>
        <input
          value={model}
          onChange={(e) => setModel(e.target.value)}
          placeholder="sonnet · opus · haiku · empty = default"
          className="w-full max-w-md rounded border border-[var(--border)] bg-[var(--bg)] px-2.5 py-1.5 font-mono text-[11px] outline-none focus:border-[var(--ac)]"
        />
        <div className="mt-3 flex items-center justify-between gap-4">
          <span className="font-mono text-[10px] text-[var(--ink-faint)]">{modelStatus}</span>
          <button type="button" onClick={saveModel} className="btn-press rounded-lg border border-[var(--rail-neutral)] px-3 py-1.5 font-mono text-[11px] font-semibold text-[var(--ink-muted)] hover:border-[var(--ac)] hover:text-[var(--ac)]">
            Save model
          </button>
        </div>
      </SettingsCard>

      <SettingsCard title="APPEARANCE">
        <p className="mb-2 font-mono text-[9px] text-[var(--ink-fainter)]">applies immediately · saved for the next launch</p>
        <SegmentRow<Accent>
          label="ACCENT"
          value={settings.accent}
          options={["amber", "indigo", "emerald", "mono"]}
          onChange={(v) => update({ accent: v })}
        />
        <SegmentRow<Density>
          label="DENSITY"
          value={settings.density}
          options={["comfortable", "compact"]}
          onChange={(v) => update({ density: v })}
        />
        <SegmentRow<Intensity>
          label="INTENSITY"
          value={settings.intensity}
          options={["calm", "vivid"]}
          onChange={(v) => update({ intensity: v })}
        />
      </SettingsCard>

      <SettingsCard title="SHORTCUTS">
        <p className="mb-2 font-mono text-[9px] text-[var(--ink-fainter)]">global · inert while typing in a form field</p>
        <div className="grid gap-2 sm:grid-cols-2">
          {SHORTCUT_REFERENCE.map(({ cap, desc }) => (
            <div key={cap} className="flex items-start gap-2">
              <kbd className="shrink-0 rounded border border-[rgba(var(--ac-rgb),0.34)] bg-[rgba(var(--ac-rgb),0.16)] px-1.5 py-0.5 font-mono text-[10px] font-bold text-[var(--ac)]">
                {cap}
              </kbd>
              <span className="text-[12px] text-[var(--ink-dim)]">{desc}</span>
            </div>
          ))}
        </div>
      </SettingsCard>
    </div>
  );
}

function SettingsCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="mb-5 rounded-lg border border-[var(--border)] bg-[var(--raise)] p-4">
      <h3 className="mb-2 font-mono text-[10px] font-bold text-[var(--ink-faint)]">{title}</h3>
      {children}
    </section>
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
    <div className="mt-2 flex items-center gap-3">
      <span className="w-20 font-mono text-[9px] font-bold text-[var(--ink-faint)]">{label}</span>
      <div className="flex gap-0.5 rounded-lg border border-[var(--border)] bg-[var(--bg)] p-0.5">
        {options.map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => onChange(opt)}
            className={cn(
              "btn-press rounded-md px-2.5 py-1 font-mono text-[10px] font-semibold capitalize",
              value === opt ? "bg-[var(--ac)] text-[var(--ac-on)]" : "text-[var(--ink-dim)]",
            )}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}
