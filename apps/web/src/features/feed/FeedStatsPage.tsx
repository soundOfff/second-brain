import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Play, Plus, X } from "lucide-react";
import type { FeedStatsRow, NewFeedRequest } from "@second-brain/types";
import {
  createWebpage,
  fetchFeedStats,
  pollFeedRun,
  runFeeder,
  subscribeFeed,
} from "../../lib/api";
import { AppShell } from "../../components/AppShell";
import { cn } from "../../lib/utils";

type SourceKind = "webpage" | "rss" | "yt" | "api";

const BLURBS: Record<SourceKind, string> = {
  webpage: "Clip a URL or jot a note straight into sources/ — the next /sync folds it into the wiki.",
  rss: "Subscribe to an RSS/Atom feed — appends a [[feed]] to feeds.toml.",
  yt: "Subscribe to a YouTube channel — appends a [[feed]] to feeds.toml.",
  api: "Subscribe to a public JSON endpoint via a declarative mapping.",
};

const COLUMNS = ["Feed", "Adapter", "Trust", "Cap", "Seen", "Today", "Queued", "Keep-rate"] as const;

export function FeedStatsPage() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["feedStats"],
    queryFn: fetchFeedStats,
  });
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobMsg, setJobMsg] = useState("");
  const [jobErr, setJobErr] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const runMut = useMutation({
    mutationFn: runFeeder,
    onSuccess: (res) => {
      setJobId(res.jobId);
      setJobMsg("running… network fetches can take a while");
      setJobErr(false);
    },
    onError: (e) => {
      setJobMsg(String(e));
      setJobErr(true);
    },
  });

  useEffect(() => {
    if (!jobId) return;
    const t = setInterval(async () => {
      try {
        const st = await pollFeedRun(jobId);
        if (st.status === "done") {
          setJobId(null);
          setJobMsg(st.summary ?? "done");
          setJobErr(false);
          refetch();
          toast.success(st.summary ?? "Feeder done");
        } else if (st.status === "error") {
          setJobId(null);
          setJobMsg(st.error ?? "run failed");
          setJobErr(true);
        }
      } catch {
        /* keep polling */
      }
    }, 1500);
    return () => clearInterval(t);
  }, [jobId, refetch]);

  const rows = data?.rows ?? [];
  const running = !!jobId || runMut.isPending;
  const totals = rows.reduce(
    (acc, r) => ({
      queued: acc.queued + (r.queued ?? 0),
      today: acc.today + (r.today_seen ?? 0),
      seen: acc.seen + (r.total_seen ?? 0),
    }),
    { queued: 0, today: 0, seen: 0 },
  );

  return (
    <AppShell
      title="Feed Stats"
      subtitle="feeds.toml · keep-rate tracked going forward"
      actions={
        <button type="button" disabled={running} onClick={() => runMut.mutate()} className="btn btn-accent">
          <Play className="h-3.5 w-3.5" aria-hidden="true" />
          <span className="hidden sm:inline">{running ? "Running…" : "Run feeder"}</span>
          <span className="sm:hidden">{running ? "…" : "Run"}</span>
        </button>
      }
    >
      <div className="mx-auto w-full max-w-[1000px]" style={{ padding: "var(--card-pad)" }}>
        <p
          className={cn(
            "meta mb-5",
            jobErr && "text-[var(--drop-ink)]",
            running && "text-[var(--ac)]",
          )}
          role="status"
        >
          {jobMsg || "pulls every feed once — same as the 01:30 agent"}
        </p>

        <div className="mb-6 grid grid-cols-3 gap-2 sm:gap-3">
          <StatTile label="feeds" value={rows.length} />
          <StatTile label="queued" value={totals.queued} accent />
          <StatTile label="seen today" value={totals.today} />
        </div>

        <div className="label mb-2">Per feed</div>

        {/* cards below md, table from md up */}
        <div className="flex flex-col gap-2 md:hidden">
          {isLoading ? (
            <p className="text-[13px] text-[var(--ink-dim)]">Loading…</p>
          ) : rows.length ? (
            rows.map((row) => <FeedCard key={row.id} row={row} />)
          ) : (
            <EmptyFeeds />
          )}
        </div>

        <div className="hidden overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--raise)] md:block">
          <table className="w-full min-w-[680px] border-collapse font-mono text-[11.5px]">
            <caption className="sr-only">Per-feed ingestion statistics</caption>
            <thead>
              <tr className="border-b border-[var(--border)] text-left">
                {COLUMNS.map((h, i) => (
                  <th
                    key={h}
                    scope="col"
                    className={cn(
                      "px-3 py-2.5 text-[10px] font-bold tracking-[0.12em] text-[var(--ink-faint)] uppercase",
                      i > 0 && "text-center",
                    )}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-3 py-6 text-[var(--ink-dim)]">
                    Loading…
                  </td>
                </tr>
              ) : rows.length ? (
                rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-t border-[var(--border-soft)] transition-colors hover:bg-white/[0.02]"
                  >
                    <th scope="row" className="px-3 py-2 text-left font-medium text-[var(--ink)]">
                      {row.id}
                    </th>
                    <Cell>{row.adapter}</Cell>
                    <Cell>{row.trust}</Cell>
                    <Cell>{row.cap}</Cell>
                    <Cell>{row.total_seen}</Cell>
                    <Cell>{row.today_seen}</Cell>
                    <Cell>{row.queued}</Cell>
                    <td className="tnum px-3 py-2 text-center">
                      {row.keep_rate == null ? (
                        <span className="text-[var(--ink-dim2)]">N/A</span>
                      ) : (
                        <span className="font-semibold text-[var(--ac)]">
                          {Math.round(row.keep_rate * 100)}%
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8}>
                    <EmptyFeeds bare />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <p className="measure mt-4 text-[12.5px] leading-relaxed text-[var(--ink-dim2)]">
          <span className="label mr-2">Why N/A</span>
          Keep-rate is tracked going forward: a feed needs at least 10 keep/drop decisions before a
          number is shown.
        </p>

        <div className="mt-7">
          {!showForm ? (
            <button type="button" onClick={() => setShowForm(true)} className="btn">
              <Plus className="h-4 w-4" aria-hidden="true" />
              Add source
            </button>
          ) : (
            <NewSourceForm onClose={() => setShowForm(false)} />
          )}
        </div>
      </div>
    </AppShell>
  );
}

function Cell({ children }: { children: React.ReactNode }) {
  return <td className="tnum px-3 py-2 text-center text-[var(--ink-muted)]">{children}</td>;
}

function StatTile({ label, value, accent }: { label: string; value: number; accent?: boolean }) {
  return (
    <div className="surface px-3 py-2.5">
      <div
        className={cn(
          "tnum font-mono text-[20px] leading-none font-bold",
          accent ? "text-[var(--ac)]" : "text-[var(--ink-bright)]",
        )}
      >
        {value}
      </div>
      <div className="meta mt-1.5">{label}</div>
    </div>
  );
}

function FeedCard({ row }: { row: FeedStatsRow }) {
  return (
    <div className="surface p-3">
      <div className="flex items-baseline justify-between gap-2">
        <span className="truncate font-mono text-[12px] font-semibold text-[var(--ink)]">{row.id}</span>
        <span className="tnum font-mono text-[11px] font-semibold text-[var(--ac)]">
          {row.keep_rate == null ? (
            <span className="text-[var(--ink-dim2)]">N/A</span>
          ) : (
            `${Math.round(row.keep_rate * 100)}%`
          )}
        </span>
      </div>
      <dl className="mt-2 grid grid-cols-3 gap-y-2">
        {(
          [
            ["adapter", row.adapter],
            ["trust", row.trust],
            ["cap", row.cap],
            ["seen", row.total_seen],
            ["today", row.today_seen],
            ["queued", row.queued],
          ] as const
        ).map(([k, v]) => (
          <div key={k}>
            <dt className="meta">{k}</dt>
            <dd className="tnum font-mono text-[12px] text-[var(--ink-muted)]">{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

function EmptyFeeds({ bare }: { bare?: boolean }) {
  return (
    <div className={cn("px-3 py-8 text-center", !bare && "surface")}>
      <p className="text-[13px] text-[var(--ink-dim)]">No feeds configured.</p>
      <p className="meta mt-1">add one to feeds.toml, or use “Add source” below</p>
    </div>
  );
}

function NewSourceForm({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [kind, setKind] = useState<SourceKind>("webpage");
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [body, setBody] = useState("");
  const [tags, setTags] = useState("");
  const [feedId, setFeedId] = useState("");
  const [cap, setCap] = useState("");
  const [trust, setTrust] = useState<"auto" | "queue">("queue");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      const tagList = tags.split(/[\s,]+/).filter(Boolean);
      if (kind === "webpage") {
        await createWebpage({
          title: title || undefined,
          url: url || undefined,
          body: body || undefined,
          tags: tagList,
        });
        toast.success("Source deposited");
      } else {
        const req: NewFeedRequest = {
          kind: kind === "yt" ? "yt" : kind,
          title: title || undefined,
          url,
          tags: tagList,
          id: feedId || undefined,
          cap: cap ? Number(cap) : null,
          trust,
        };
        const res = await subscribeFeed(req);
        toast.success(`Subscribed feed ${res.id}`);
      }
      qc.invalidateQueries({ queryKey: ["feedStats"] });
      onClose();
    } catch (err) {
      toast.error(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="surface enter measure p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="label">New source</h2>
        <button type="button" onClick={onClose} className="btn btn-icon" aria-label="Hide the new-source form">
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <div
        className="mb-3 flex flex-wrap gap-0.5 rounded-lg border border-[var(--border)] bg-[var(--bg)] p-0.5"
        role="tablist"
        aria-label="Source kind"
      >
        {(["webpage", "rss", "yt", "api"] as const).map((k) => (
          <button
            key={k}
            type="button"
            role="tab"
            aria-selected={kind === k}
            onClick={() => setKind(k)}
            className={cn(
              "btn-press flex-1 rounded-md px-2.5 py-1.5 font-mono text-[10.5px] font-semibold capitalize transition-colors",
              kind === k
                ? "bg-[var(--ac)] text-[var(--ac-on)]"
                : "text-[var(--ink-dim)] hover:text-[var(--ink)]",
            )}
          >
            {k === "yt" ? "youtube" : k}
          </button>
        ))}
      </div>

      <p className="mb-4 text-[12.5px] leading-relaxed text-[var(--ink-dim2)]">{BLURBS[kind]}</p>

      <div className="grid gap-3">
        <Field label="Title" value={title} onChange={setTitle} />
        <Field
          label="URL"
          value={url}
          onChange={setUrl}
          type="url"
          required={kind !== "webpage"}
          placeholder="https://…"
        />
        {kind === "webpage" ? <Field label="Body (note)" value={body} onChange={setBody} multiline /> : null}
        <Field label="Tags" value={tags} onChange={setTags} hint="space-separated" />
        {kind !== "webpage" ? (
          <>
            <Field label="Feed id" value={feedId} onChange={setFeedId} hint="optional" />
            <Field label="Daily cap" value={cap} onChange={setCap} hint="optional override" inputMode="numeric" />
            <label className="block">
              <span className="label mb-1 block">Trust</span>
              <select
                value={trust}
                onChange={(e) => setTrust(e.target.value as "auto" | "queue")}
                className="field max-w-[180px]"
              >
                <option value="queue">queue</option>
                <option value="auto">auto</option>
              </select>
            </label>
          </>
        ) : null}
      </div>

      <button type="submit" disabled={busy} className="btn btn-accent mt-4">
        {busy ? "Working…" : kind === "webpage" ? "Deposit source" : "Subscribe feed"}
      </button>
    </form>
  );
}

function Field({
  label,
  value,
  onChange,
  hint,
  multiline,
  type = "text",
  required,
  placeholder,
  inputMode,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  hint?: string;
  multiline?: boolean;
  type?: string;
  required?: boolean;
  placeholder?: string;
  inputMode?: "numeric";
}) {
  return (
    <label className="block">
      <span className="label mb-1 block">
        {label}
        {required ? <span className="ml-1 text-[var(--drop-ink)]">*</span> : null}
      </span>
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={4}
          className="field resize-y"
          placeholder={placeholder}
        />
      ) : (
        <input
          value={value}
          type={type}
          required={required}
          inputMode={inputMode}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className="field"
        />
      )}
      {hint ? <span className="meta mt-1 block">{hint}</span> : null}
    </label>
  );
}
