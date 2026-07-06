import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { NewFeedRequest } from "@second-brain/types";
import {
  createWebpage,
  fetchFeedStats,
  pollFeedRun,
  runFeeder,
  subscribeFeed,
} from "../../lib/api";
import { cn } from "../../lib/utils";

type SourceKind = "webpage" | "rss" | "yt" | "api";

const BLURBS: Record<SourceKind, string> = {
  webpage: "Clip a URL or jot a note straight into sources/ — the next /sync folds it into the wiki.",
  rss: "Subscribe to an RSS/Atom feed — appends a [[feed]] to feeds.toml.",
  yt: "Subscribe to a YouTube channel — appends a [[feed]] to feeds.toml.",
  api: "Subscribe to a public JSON endpoint via a declarative mapping.",
};

export function FeedStatsPage({ demo: _demo }: { demo: boolean }) {
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

  return (
    <div className="scroll min-h-0 flex-1 overflow-y-auto">
      <header className="flex items-start justify-between px-7 py-5" style={{ padding: "var(--head-pad)" }}>
        <div>
          <h2 className="font-bold text-[var(--ink-bright)]" style={{ fontSize: "var(--title-size)" }}>
            Feed Stats
          </h2>
          <p className="mt-1 font-mono text-[10px] text-[var(--ink-faint)]">all feeds · keep-rate tracked going forward</p>
        </div>
        <div className="text-right">
          <button
            type="button"
            disabled={!!jobId || runMut.isPending}
            onClick={() => runMut.mutate()}
            className="btn-press rounded-lg border border-[var(--rail-neutral)] px-3 py-1.5 font-mono text-[11px] font-semibold text-[var(--ink-muted)] hover:border-[var(--ac)] hover:text-[var(--ac)] disabled:opacity-55"
          >
            Run feeder now
          </button>
          <p className={cn("mt-1 font-mono text-[9px]", jobErr ? "text-[var(--drop-ink)]" : "text-[var(--ink-faint)]")}>
            {jobMsg || "pulls every feed once — same as the 01:30 agent"}
          </p>
        </div>
      </header>

      <div style={{ padding: "0 var(--card-pad) var(--card-pad)" }}>
        <div className="mb-2 font-mono text-[10px] font-bold text-[var(--ink-faint)]">PER-FEED</div>
        <div className="overflow-x-auto rounded-lg border border-[var(--border)] bg-[var(--raise)]">
          <table className="w-full min-w-[640px] border-collapse font-mono text-[11px]">
            <thead>
              <tr className="text-left text-[var(--ink-faint)]">
                {["FEED", "ADAPTER", "TRUST", "CAP", "SEEN", "TODAY", "QUEUED", "KEEP-RATE"].map((h) => (
                  <th key={h} className="px-2 py-2 font-bold">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-2 py-6 text-[var(--ink-dim)]">
                    Loading…
                  </td>
                </tr>
              ) : rows.length ? (
                rows.map((row) => (
                  <tr key={row.id} className="border-t border-[var(--border-soft)]">
                    <td className="px-2 py-1.5 text-[var(--ink)]">{row.id}</td>
                    <td className="px-2 py-1.5 text-center text-[var(--ink-muted)]">{row.adapter}</td>
                    <td className="px-2 py-1.5 text-center text-[var(--ink-muted)]">{row.trust}</td>
                    <td className="px-2 py-1.5 text-center text-[var(--ink-muted)]">{row.cap}</td>
                    <td className="px-2 py-1.5 text-center text-[var(--ink-muted)]">{row.total_seen}</td>
                    <td className="px-2 py-1.5 text-center text-[var(--ink-muted)]">{row.today_seen}</td>
                    <td className="px-2 py-1.5 text-center text-[var(--ink-muted)]">{row.queued}</td>
                    <td className="px-2 py-1.5 text-center">
                      {row.keep_rate == null ? (
                        <span className="text-[var(--ink-dim2)]">N/A</span>
                      ) : (
                        <span className="text-[var(--ac)]">{Math.round(row.keep_rate * 100)}%</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-2 py-6 text-[var(--ink-dim)]">
                    No feeds configured (feeds.toml).
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-4 text-[12px] leading-relaxed text-[var(--ink-dim2)]">
          <div className="mb-1.5 font-mono text-[10px] font-bold text-[var(--ink-faint)]">WHY SOME SHOW N/A</div>
          Keep-rate is tracked going forward: a feed needs at least 10 keep/drop decisions before a number is shown.
        </div>

        <div className="mt-5">
          {!showForm ? (
            <button
              type="button"
              onClick={() => setShowForm(true)}
              className="btn-press font-mono text-[11px] font-semibold text-[var(--ac)] hover:underline"
            >
              + Add source
            </button>
          ) : (
            <NewSourceForm onClose={() => setShowForm(false)} />
          )}
        </div>
      </div>
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
        await createWebpage({ title: title || undefined, url: url || undefined, body: body || undefined, tags: tagList });
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
    <form onSubmit={submit} className="rounded-lg border border-[var(--border)] bg-[var(--raise)] p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="font-mono text-[10px] font-bold text-[var(--ink-faint)]">NEW SOURCE</span>
        <div className="flex gap-0.5 rounded-lg border border-[var(--border)] bg-[var(--bg)] p-0.5">
          {(["webpage", "rss", "yt", "api"] as const).map((k) => (
            <button
              key={k}
              type="button"
              onClick={() => setKind(k)}
              className={cn(
                "btn-press rounded-md px-2.5 py-1 font-mono text-[10px] font-semibold capitalize",
                kind === k ? "bg-[var(--ac)] text-[var(--ac-on)]" : "text-[var(--ink-dim)]",
              )}
            >
              {k === "yt" ? "youtube" : k}
            </button>
          ))}
        </div>
        <button type="button" onClick={onClose} className="font-mono text-[9px] font-bold text-[var(--ink-faint)]">
          hide ✕
        </button>
      </div>
      <p className="mb-3 text-[12px] text-[var(--ink-dim2)]">{BLURBS[kind]}</p>
      <div className="grid gap-2">
        <Field label="Title" value={title} onChange={setTitle} />
        <Field label="URL" value={url} onChange={setUrl} />
        {kind === "webpage" ? <Field label="Body (note)" value={body} onChange={setBody} multiline /> : null}
        <Field label="Tags" value={tags} onChange={setTags} hint="space-separated" />
        {kind !== "webpage" ? (
          <>
            <Field label="Feed id" value={feedId} onChange={setFeedId} hint="optional" />
            <Field label="Daily cap" value={cap} onChange={setCap} hint="optional override" />
            <label className="flex items-center gap-2 text-[12px] text-[var(--ink-dim)]">
              Trust
              <select
                value={trust}
                onChange={(e) => setTrust(e.target.value as "auto" | "queue")}
                className="rounded border border-[var(--border)] bg-[var(--bg)] px-2 py-1 font-mono text-[11px]"
              >
                <option value="queue">queue</option>
                <option value="auto">auto</option>
              </select>
            </label>
          </>
        ) : null}
      </div>
      <button
        type="submit"
        disabled={busy}
        className="btn-press mt-4 rounded-lg bg-[var(--ac)] px-4 py-2 font-mono text-[11px] font-semibold text-[var(--ac-on)] disabled:opacity-55"
      >
        {kind === "webpage" ? "Deposit source" : "Subscribe feed"}
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
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  hint?: string;
  multiline?: boolean;
}) {
  const cls =
    "w-full rounded border border-[var(--border)] bg-[var(--bg)] px-2.5 py-1.5 font-mono text-[11px] text-[var(--ink)] outline-none focus:border-[var(--ac)]";
  return (
    <label className="block text-[11px] text-[var(--ink-dim)]">
      <span className="mb-0.5 block font-mono text-[9px] font-bold uppercase text-[var(--ink-faint)]">{label}</span>
      {multiline ? (
        <textarea value={value} onChange={(e) => onChange(e.target.value)} rows={4} className={cls} />
      ) : (
        <input value={value} onChange={(e) => onChange(e.target.value)} className={cls} />
      )}
      {hint ? <span className="mt-0.5 block font-mono text-[9px] text-[var(--ink-fainter)]">{hint}</span> : null}
    </label>
  );
}
