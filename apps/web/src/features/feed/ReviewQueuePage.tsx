import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import type { ReviewItem } from "@second-brain/types";
import { dropItem, fetchQueue, keepItem, undoAction } from "../../lib/api";
import { useBrainShortcuts } from "../../hooks/useBrainShortcuts";
import { Kbd } from "../../components/Kbd";
import { cn } from "../../lib/utils";

type View = "recap" | "graph";

export function ReviewQueuePage({ demo }: { demo: boolean }) {
  const qc = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  const qs = demo ? "?demo=1" : "";

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["queue", demo],
    queryFn: () => fetchQueue(demo),
  });

  const [order, setOrder] = useState<string[]>([]);
  const [selected, setSelected] = useState(0);
  const [view, setView] = useState<View>("recap");
  const [kept, setKept] = useState(0);
  const [dropped, setDropped] = useState(0);
  const [skipped, setSkipped] = useState(0);
  const [undoToken, setUndoToken] = useState<string | null>(null);

  const items: ReviewItem[] = useMemo(() => {
    const raw = data?.items ?? [];
    if (!order.length) return raw;
    const byId = new Map(raw.map((it) => [it.id, it]));
    const ordered = order.map((id) => byId.get(id)).filter(Boolean) as ReviewItem[];
    for (const it of raw) {
      if (!order.includes(it.id)) ordered.push(it);
    }
    return ordered;
  }, [data?.items, order]);

  // Sync order when queue loads
  useEffect(() => {
    if (data?.items?.length && !order.length) {
      setOrder(data.items.map((it) => it.id));
    }
  }, [data?.items, order.length]);

  const current = items[selected] ?? null;

  const keepMut = useMutation({
    mutationFn: (id: string) => keepItem(id, demo),
    onSuccess: (res) => {
      setKept((k) => k + 1);
      setUndoToken(res.undoToken);
      toast.success("Kept — placed into sources/");
      removeCurrent();
      qc.invalidateQueries({ queryKey: ["queue", demo] });
    },
    onError: (e) => toast.error(String(e)),
  });

  const dropMut = useMutation({
    mutationFn: (id: string) => dropItem(id, demo),
    onSuccess: (res) => {
      setDropped((d) => d + 1);
      setUndoToken(res.undoToken);
      toast.success("Dropped");
      removeCurrent();
      qc.invalidateQueries({ queryKey: ["queue", demo] });
    },
    onError: (e) => toast.error(String(e)),
  });

  const undoMut = useMutation({
    mutationFn: () => undoAction(undoToken!),
    onSuccess: () => {
      toast.success("Undone");
      setUndoToken(null);
      refetch();
    },
    onError: (e) => toast.error(String(e)),
  });

  function removeCurrent() {
    if (!current) return;
    setOrder((o) => o.filter((id) => id !== current.id));
    setSelected((s) => Math.min(s, Math.max(0, items.length - 2)));
  }

  const doKeep = useCallback(() => {
    if (current && !keepMut.isPending) keepMut.mutate(current.id);
  }, [current, keepMut]);

  const doDrop = useCallback(() => {
    if (current && !dropMut.isPending) dropMut.mutate(current.id);
  }, [current, dropMut]);

  const doSkip = useCallback(() => {
    if (!current) return;
    setSkipped((s) => s + 1);
    setSelected((s) => Math.min(s + 1, items.length - 1));
  }, [current, items.length]);

  const doUndo = useCallback(() => {
    if (undoToken && !undoMut.isPending) undoMut.mutate();
  }, [undoToken, undoMut]);

  const openUrl = useCallback(() => {
    if (current?.url) {
      const href = current.url.startsWith("http") ? current.url : `https://${current.url}`;
      window.open(href, "_blank", "noopener,noreferrer");
    }
  }, [current?.url]);

  useBrainShortcuts({
    keep: doKeep,
    drop: doDrop,
    skip: doSkip,
    undo: doUndo,
    open: openUrl,
    rescan: () => refetch(),
    toggleView: () => setView((v) => (v === "recap" ? "graph" : "recap")),
    next: () => setSelected((s) => Math.min(s + 1, items.length - 1)),
    prev: () => setSelected((s) => Math.max(s - 1, 0)),
    review: () => navigate(`/feed/review${qs}`),
    stats: () => navigate(`/feed/stats${qs}`),
    settings: () => navigate(`/feed/settings${qs}`),
    toggleScreen: () => navigate(location.pathname.includes("stats") ? `/feed/review${qs}` : `/feed/stats${qs}`),
  });

  const progress = items.length ? ((kept + dropped) / (kept + dropped + items.length)) * 100 : 100;

  if (isLoading) {
    return <div className="flex flex-1 items-center justify-center text-[var(--ink-dim)]">Loading queue…</div>;
  }

  if (!items.length) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3.5 p-10 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full border border-[rgba(var(--ac-rgb),0.28)] bg-[rgba(var(--ac-rgb),0.10)] font-mono text-[28px] text-[var(--ac)] shadow-[0_0_0_6px_rgba(var(--ac-rgb),0.06)]">
          ✓
        </div>
        <h2 className="text-lg font-semibold text-[var(--ink)]">Queue clear</h2>
        <p className="max-w-[340px] text-[13.5px] leading-relaxed text-[var(--ink-dim)]">
          Nothing in <code className="font-mono text-[var(--ac)]">.brain/review/</code>. Run the feeder or clip a source.
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-0 flex-1">
      {/* sidebar */}
      <aside className="flex w-[296px] shrink-0 flex-col border-r border-[var(--border)] bg-[var(--panel)]">
        <div className="flex items-end justify-between px-[18px] pt-4 pb-3">
          <div>
            <h1 className="text-[13px] font-semibold tracking-wide text-[var(--ink)]">Review Queue</h1>
            <p className="mt-0.5 font-mono text-[10.5px] tracking-wide text-[var(--ink-faint)]">
              {demo ? "demo mode" : "live queue"}
            </p>
          </div>
          <span className="rounded-md border border-[rgba(var(--ac-rgb),0.25)] bg-[rgba(var(--ac-rgb),0.12)] px-2 py-0.5 font-mono text-[11px] font-semibold text-[var(--ac)]">
            {items.length}
          </span>
        </div>

        <div className="px-[18px] pb-2.5">
          <div className="h-[3px] overflow-hidden rounded bg-[var(--border-soft)]">
            <div
              className="h-full rounded bg-[var(--ac)] shadow-[0_0_8px_rgba(var(--ac-rgb),0.45)] transition-[width] duration-[420ms]"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="scroll min-h-0 flex-1 overflow-y-auto px-3 pb-3">
          {items.map((it, idx) => (
            <button
              key={it.id}
              type="button"
              onClick={() => setSelected(idx)}
              className={cn(
                "btn-press relative w-full rounded-lg py-[var(--row-pt)] pr-2.5 pb-[var(--row-pb)] pl-11 text-left transition-colors",
                idx === selected ? "bg-[var(--sel-bg)]" : "hover:bg-white/[0.035]",
              )}
            >
              <span
                className={cn(
                  "absolute top-[calc(var(--node-c)-11px)] left-[9px] z-[2] flex h-[22px] w-[22px] items-center justify-center rounded-full border font-mono text-[10px] font-bold",
                  idx === selected
                    ? "border-transparent bg-[var(--ac)] text-[var(--ac-on)] shadow-[0_0_0_4px_rgba(var(--ac-rgb),0.16),0_0_10px_rgba(var(--ac-rgb),0.35)]"
                    : "border-[var(--rail-neutral)] bg-[var(--node)] text-[var(--ink-dim)]",
                )}
              >
                {idx + 1}
              </span>
              <div className="flex min-w-0 flex-col gap-1">
                <div className="flex min-w-0 items-center gap-1.5">
                  <span className="line-clamp-2 flex-1 text-[12.5px] font-medium leading-snug text-[var(--ink)]">
                    {it.title}
                  </span>
                  {idx === selected ? (
                    <span className="rounded px-1 py-0.5 font-mono text-[8.5px] font-bold tracking-wider text-[var(--ac)] bg-[rgba(var(--ac-rgb),0.14)]">
                      NOW
                    </span>
                  ) : null}
                </div>
                <div className="flex items-center gap-1.5">
                  <span className={cn("font-mono text-[10px] font-semibold tracking-wide", idx === selected ? "text-[var(--ac)]" : "text-[var(--ink-dim2)]")}>
                    {it.via}
                  </span>
                  <span className="font-mono text-[9.5px] uppercase tracking-wider text-[var(--ink-faint)]">{it.type}</span>
                </div>
              </div>
            </button>
          ))}
        </div>

        <footer className="flex h-[var(--footer-h)] shrink-0 items-center justify-between border-t border-[var(--border-soft)] px-4">
          <span className="font-mono text-[10.5px] tracking-wide text-[var(--ink-faint)]">
            {kept} kept · {dropped} dropped · {skipped} skipped
          </span>
        </footer>
      </aside>

      {/* main pane */}
      <div className="flex min-w-0 flex-1 flex-col">
        {current ? (
          <>
            <header className="border-b border-[var(--border-soft)] px-7 py-5" style={{ padding: "var(--head-pad)" }}>
              {current.reason ? (
                <span className="mb-3 inline-block rounded border border-[rgba(var(--ac-rgb),0.22)] bg-[var(--reason-bg)] px-2 py-0.5 font-mono text-[10.5px] font-semibold text-[var(--ac)]">
                  {current.reason}
                </span>
              ) : null}
              <h2 className="text-balance font-bold leading-tight tracking-tight text-[var(--ink-bright)]" style={{ fontSize: "var(--title-size)" }}>
                {current.title}
              </h2>
              <div className="mt-3 flex flex-wrap items-center gap-3.5 font-mono text-[11.5px]">
                <span className="text-[var(--ac)]">{current.via}</span>
                <span className="text-[var(--hair)]">·</span>
                <span className="uppercase tracking-wider text-[var(--ink-dim)]">{current.type}</span>
                {current.url ? (
                  <>
                    <span className="text-[var(--hair)]">·</span>
                    <span className="max-w-[340px] truncate text-[var(--ink-faint)]">{current.url}</span>
                  </>
                ) : null}
              </div>
            </header>

            <div className="scroll min-h-0 flex-1 overflow-y-auto" style={{ padding: "var(--card-pad)" }}>
              <div className="mb-3.5 flex items-center justify-between">
                <span className="font-mono text-[10px] font-semibold uppercase tracking-widest text-[var(--ink-faint)]">
                  {view === "recap" ? "Recap" : "Outline"}
                </span>
                <div className="flex gap-0.5 rounded-lg border border-[var(--border)] bg-[var(--raise)] p-0.5">
                  {(["recap", "graph"] as const).map((v) => (
                    <button
                      key={v}
                      type="button"
                      onClick={() => setView(v)}
                      className={cn(
                        "btn-press rounded-md px-3 py-1 font-mono text-[11px] font-semibold",
                        view === v ? "bg-[var(--ac)] text-[var(--ac-on)]" : "text-[var(--ink-dim)]",
                      )}
                    >
                      {v}
                      <span className="ml-1.5 opacity-55">{v === "recap" ? "default" : "g"}</span>
                    </button>
                  ))}
                </div>
              </div>

              {view === "recap" ? (
                <RecapView item={current} />
              ) : (
                <GraphView item={current} />
              )}
            </div>

            <ActionBar
              onKeep={doKeep}
              onDrop={doDrop}
              onSkip={doSkip}
              onUndo={doUndo}
              onOpen={openUrl}
              undoDisabled={!undoToken}
              busy={keepMut.isPending || dropMut.isPending}
            />
          </>
        ) : null}
      </div>
    </div>
  );
}

function RecapView({ item }: { item: ReviewItem }) {
  return (
    <>
      <div
        className={cn(
          "rounded-[10px] border border-[var(--border)] bg-[var(--raise)] text-[var(--recap-ink)] leading-relaxed",
          document.documentElement.dataset.intensity === "vivid" && "border-l-[3px] border-l-[var(--ac)]",
        )}
        style={{ padding: "var(--recap-pad)", fontSize: "var(--recap-size)" }}
      >
        {item.summary.split("\n\n").map((p, i) => (
          <p key={i} className={i ? "mt-3" : ""}>
            {p}
          </p>
        ))}
      </div>
      {item.tags.length ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {item.tags.map((tag) => (
            <span key={tag} className="rounded-md border border-[var(--border)] bg-[var(--node)] px-2 py-1 font-mono text-[11px] text-[var(--ink-muted)]">
              {tag}
            </span>
          ))}
        </div>
      ) : null}
      {item.overlaps.length ? (
        <div className="mt-5">
          <div className="mb-2.5 font-mono text-[10px] font-semibold uppercase tracking-widest text-[var(--ink-faint)]">
            Overlaps
          </div>
          <div className="flex flex-col gap-2">
            {item.overlaps.map((o) => (
              <div key={o.page} className="flex items-center gap-3 rounded-lg border border-[var(--border-soft)] bg-[var(--sunk)] px-3.5 py-2.5">
                <span className="font-mono text-xs font-medium text-[var(--ac)]">{o.page}</span>
                <span className="h-3.5 w-px bg-[var(--rail-neutral)]" />
                <span className="flex-1 text-[12.5px] text-[var(--ink-dim)]">{o.note}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      <div className="mt-6 flex gap-6 font-mono text-[10.5px] text-[var(--ink-faint)]">
        {item.queued ? <span>queued {item.queued}</span> : null}
        {item.length ? <span>{item.length}</span> : null}
        {item.tokens ? <span>{item.tokens}</span> : null}
      </div>
    </>
  );
}

function GraphView({ item }: { item: ReviewItem }) {
  return (
    <div>
      <div className="flex items-center gap-2.5 pb-0.5">
        <span className="h-[11px] w-[11px] shrink-0 rounded-full bg-[var(--ac)] shadow-[0_0_0_4px_rgba(var(--ac-rgb),0.16),0_0_10px_rgba(var(--ac-rgb),0.3)]" />
        <span className="max-w-[420px] truncate text-sm font-semibold text-[var(--ink-bright)]">{item.title}</span>
        <span className="whitespace-nowrap rounded border border-[var(--border)] bg-[var(--raise)] px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-[var(--ink-dim)]">
          {item.type}
        </span>
      </div>
      {item.breakdown.length ? (
        <div className="mt-4">
          <div className="mb-0.5 pl-9 font-mono text-[10px] font-semibold uppercase tracking-widest text-[var(--ink-faint)]">
            Breakdown
          </div>
          {item.breakdown.map((b, i) => (
            <div key={i} className="relative py-2 pl-9">
              <div className="flex flex-wrap items-baseline gap-2.5">
                <span className="min-w-12 font-mono text-xs font-semibold text-[var(--ac)]">{b.at}</span>
                <span className="text-[13.5px] font-medium text-[var(--ink)]">{b.label}</span>
              </div>
              <div className="mt-1 font-mono text-xs text-[var(--ink-faint)]">{b.target}</div>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-4 text-sm text-[var(--ink-dim)]">No outline breakdown for this item.</p>
      )}
    </div>
  );
}

function ActionBar({
  onKeep,
  onDrop,
  onSkip,
  onUndo,
  onOpen,
  undoDisabled,
  busy,
}: {
  onKeep: () => void;
  onDrop: () => void;
  onSkip: () => void;
  onUndo: () => void;
  onOpen: () => void;
  undoDisabled: boolean;
  busy: boolean;
}) {
  return (
    <footer
      className="flex shrink-0 items-center gap-2.5 border-t border-[var(--border)] bg-[var(--panel)]"
      style={{ padding: "var(--bar-pad)" }}
    >
      <button
        type="button"
        disabled={busy}
        onClick={onKeep}
        className="btn-press flex h-[var(--btn-h)] items-center gap-2 rounded-lg border border-[var(--ac)] bg-[var(--ac)] px-3.5 text-[var(--btn-f)] font-semibold text-[var(--ac-on)] transition-[filter] hover:brightness-110 disabled:opacity-55"
      >
        Keep <Kbd className="!border-black/20 !bg-black/30 !text-[var(--ac-on)]">k</Kbd>
      </button>
      <button
        type="button"
        disabled={busy}
        onClick={onDrop}
        className="btn-press flex h-[var(--btn-h)] items-center gap-2 rounded-lg border border-[var(--rail-neutral)] px-3.5 text-[var(--btn-f)] font-semibold text-[var(--ink-muted)] hover:border-[var(--drop-border)] hover:text-[var(--drop-ink)] disabled:opacity-55"
      >
        Drop <Kbd>d</Kbd>
      </button>
      <button
        type="button"
        onClick={onSkip}
        className="btn-press flex h-[var(--btn-h)] items-center gap-2 rounded-lg border border-[var(--rail-neutral)] px-3.5 text-[var(--btn-f)] font-semibold text-[var(--ink-muted)] hover:border-[var(--hair)] hover:text-[var(--ink)]"
      >
        Skip <Kbd>→</Kbd>
      </button>
      <span className="mx-1 h-[22px] w-px bg-[var(--border)]" />
      <button type="button" onClick={onOpen} className="btn-press flex h-[var(--btn-h)] items-center gap-2 rounded-lg border border-[var(--rail-neutral)] px-3.5 text-[var(--btn-f)] font-semibold text-[var(--ink-muted)] hover:border-[var(--hair)] hover:text-[var(--ink)]">
        Open <Kbd>o</Kbd>
      </button>
      <button
        type="button"
        disabled={undoDisabled}
        onClick={onUndo}
        className="btn-press flex h-[var(--btn-h)] items-center gap-2 rounded-lg border border-[var(--rail-neutral)] px-3.5 text-[var(--btn-f)] font-semibold text-[var(--ink-muted)] disabled:cursor-default disabled:opacity-55"
      >
        Undo <Kbd>u</Kbd>
      </button>
    </footer>
  );
}
