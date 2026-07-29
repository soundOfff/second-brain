import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  RefreshCw,
  Undo2,
  Waypoints,
  X,
} from "lucide-react";
import type { ReviewItem } from "@second-brain/types";
import { dropItem, fetchQueue, keepItem, undoAction } from "../../lib/api";
import { useBrainShortcuts } from "../../hooks/useBrainShortcuts";
import { AppShell } from "../../components/AppShell";
import { SidePanel, SidePanelToggle } from "../../components/SidePanel";
import { Kbd } from "../../components/Kbd";
import { Markdown } from "../../components/Markdown";
import { cn } from "../../lib/utils";

type View = "recap" | "graph";

export function ReviewQueuePage({ demo }: { demo: boolean }) {
  const qc = useQueryClient();
  const navigate = useNavigate();
  const qs = demo ? "?demo=1" : "";

  const { data, isLoading, isFetching, refetch } = useQuery({
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
  const [panelOpen, setPanelOpen] = useState(false);
  const listRef = useRef<HTMLUListElement>(null);

  const items: ReviewItem[] = useMemo(() => {
    const raw = data?.items ?? [];
    if (!order.length) return raw;
    const byId = new Map(raw.map((it) => [it.id, it]));
    const ordered = order
      .map((id) => byId.get(id))
      .filter(Boolean) as ReviewItem[];
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

  // keep the keyboard cursor visible in the list
  useEffect(() => {
    listRef.current
      ?.querySelector<HTMLElement>('[data-selected="true"]')
      ?.scrollIntoView({
        block: "nearest",
      });
  }, [selected]);

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
      const href = current.url.startsWith("http")
        ? current.url
        : `https://${current.url}`;
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
  });

  const reviewed = kept + dropped;
  const progress = items.length
    ? (reviewed / (reviewed + items.length)) * 100
    : 100;

  function pick(idx: number) {
    setSelected(idx);
    setPanelOpen(false);
  }

  const shellProps = {
    title: "Review Queue",
    subtitle: (
      <>
        {demo ? "demo mode" : "live queue"} · {items.length} pending
      </>
    ),
    leading: (
      <SidePanelToggle
        onClick={() => setPanelOpen(true)}
        label="review queue"
        count={items.length}
      />
    ),
    actions: (
      <button
        type="button"
        onClick={() => refetch()}
        className="btn"
        aria-label="Rescan the queue from disk"
      >
        <RefreshCw
          className={cn("h-3.5 w-3.5", isFetching && "animate-spin")}
          aria-hidden="true"
        />
        <span className="hidden sm:inline">Rescan</span>
        <Kbd className="hidden md:inline-flex">⇧r</Kbd>
      </button>
    ),
  };

  if (isLoading) {
    return (
      <AppShell {...shellProps}>
        <div className="flex flex-1 items-center justify-center p-10 text-[var(--ink-dim)]">
          Loading queue…
        </div>
      </AppShell>
    );
  }

  if (!items.length) {
    return (
      <AppShell {...shellProps}>
        <div className="flex flex-1 flex-col items-center justify-center gap-4 p-10 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-[rgba(var(--ac-rgb),0.28)] bg-[rgba(var(--ac-rgb),0.10)] text-[var(--ac)] shadow-[0_0_0_8px_rgba(var(--ac-rgb),0.05)]">
            <Check className="h-7 w-7" aria-hidden="true" />
          </div>
          <h2 className="text-lg font-semibold text-[var(--ink)]">
            Queue clear
          </h2>
          <p className="max-w-[360px] text-[13.5px] leading-relaxed text-[var(--ink-dim)]">
            Nothing in{" "}
            <code className="font-mono text-[var(--ac)]">.brain/review/</code>.
            Run the feeder or clip a source.
          </p>
          <div className="mt-1 flex flex-wrap justify-center gap-2">
            <button
              type="button"
              onClick={() => navigate(`/feed/stats${qs}`)}
              className="btn"
            >
              Go to feeds
            </button>
            <button type="button" onClick={() => refetch()} className="btn">
              <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" /> Rescan
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell {...shellProps} scroll={false}>
      <div className="relative flex min-h-0 w-full">
        <SidePanel
          open={panelOpen}
          onClose={() => setPanelOpen(false)}
          label="Review queue"
        >
          <div className="flex items-center justify-between px-[18px] pt-4 pr-14 pb-3 lg:pr-[18px]">
            <h2 className="label">Queue</h2>
            <span className="pill pill-accent tnum">{items.length}</span>
          </div>

          <div className="px-[18px] pb-2.5">
            <div
              className="h-[3px] overflow-hidden rounded bg-[var(--border-soft)]"
              role="progressbar"
              aria-label="Session progress"
              aria-valuenow={Math.round(progress)}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <div
                className="h-full rounded bg-[var(--ac)] shadow-[0_0_8px_rgba(var(--ac-rgb),0.45)] transition-[width] duration-[420ms]"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <ul
            ref={listRef}
            className="scroll min-h-0 flex-1 overflow-y-auto px-3 pb-3"
          >
            {items.map((it, idx) => {
              const isCurrent = idx === selected;
              return (
                <li key={it.id}>
                  <button
                    type="button"
                    data-selected={isCurrent}
                    aria-current={isCurrent ? "true" : undefined}
                    onClick={() => pick(idx)}
                    className={cn(
                      "btn-press relative w-full rounded-lg py-[var(--row-pt)] pr-2.5 pb-[var(--row-pb)] pl-11 text-left transition-colors",
                      isCurrent
                        ? "bg-[var(--sel-bg)]"
                        : "hover:bg-white/[0.035]",
                    )}
                  >
                    <span
                      aria-hidden="true"
                      className={cn(
                        "absolute top-[calc(var(--node-c)-11px)] left-[9px] z-[2] flex h-[22px] w-[22px] items-center justify-center rounded-full border font-mono text-[10px] font-bold",
                        isCurrent
                          ? "border-transparent bg-[var(--ac)] text-[var(--ac-on)] shadow-[0_0_0_4px_rgba(var(--ac-rgb),0.16),0_0_10px_rgba(var(--ac-rgb),0.35)]"
                          : "border-[var(--rail-neutral)] bg-[var(--node)] text-[var(--ink-dim)]",
                      )}
                    >
                      {idx + 1}
                    </span>
                    <div className="flex min-w-0 flex-col gap-1">
                      <div className="flex min-w-0 items-start gap-1.5">
                        <span className="line-clamp-2 flex-1 text-[12.5px] leading-snug font-medium text-[var(--ink)]">
                          {it.title}
                        </span>
                        {isCurrent ? (
                          <span className="mt-[1px] shrink-0 rounded bg-[rgba(var(--ac-rgb),0.14)] px-1 py-0.5 font-mono text-[8.5px] font-bold tracking-wider text-[var(--ac)]">
                            NOW
                          </span>
                        ) : null}
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span
                          className={cn(
                            "font-mono text-[10px] font-semibold tracking-wide",
                            isCurrent
                              ? "text-[var(--ac)]"
                              : "text-[var(--ink-dim2)]",
                          )}
                        >
                          {it.via}
                        </span>
                        <span className="font-mono text-[9.5px] tracking-wider text-[var(--ink-faint)] uppercase">
                          {it.type}
                        </span>
                      </div>
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>

          <footer className="flex h-[var(--footer-h)] shrink-0 items-center gap-3 border-t border-[var(--border-soft)] px-4">
            <Tally label="kept" value={kept} accent />
            <Tally label="dropped" value={dropped} />
            <Tally label="skipped" value={skipped} />
          </footer>
        </SidePanel>

        {/* detail pane */}
        <section
          className="flex min-w-0 flex-1 flex-col"
          aria-label="Selected item"
        >
          {current ? (
            <>
              <div className="scroll min-h-0 flex-1 overflow-y-auto">
                <div className="mx-auto w-full max-w-[820px]">
                  <header
                    className="border-b border-[var(--border-soft)]"
                    style={{ padding: "var(--head-pad)" }}
                  >
                    {current.reason ? (
                      <span className="mb-3 inline-block rounded border border-[rgba(var(--ac-rgb),0.22)] bg-[var(--reason-bg)] px-2 py-0.5 font-mono text-[10.5px] font-semibold text-[var(--ac)]">
                        {current.reason}
                      </span>
                    ) : null}
                    <h2
                      className="text-balance leading-tight font-bold tracking-tight text-[var(--ink-bright)]"
                      style={{ fontSize: "var(--title-size)" }}
                    >
                      {current.title}
                    </h2>
                    <div className="mt-3 flex flex-wrap items-center gap-x-3.5 gap-y-2 font-mono text-[11.5px]">
                      <span className="text-[var(--ac)]">{current.via}</span>
                      <span className="text-[var(--hair)]" aria-hidden="true">
                        ·
                      </span>
                      <span className="tracking-wider text-[var(--ink-dim)] uppercase">
                        {current.type}
                      </span>
                      {current.url ? (
                        <>
                          <span
                            className="text-[var(--hair)]"
                            aria-hidden="true"
                          >
                            ·
                          </span>
                          <a
                            href={
                              current.url.startsWith("http")
                                ? current.url
                                : `https://${current.url}`
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex max-w-full min-w-0 items-center gap-1.5 text-[var(--ink-faint)] hover:text-[var(--ac)] hover:underline"
                          >
                            <span className="truncate">{current.url}</span>
                            <ExternalLink
                              className="h-3 w-3 shrink-0"
                              aria-hidden="true"
                            />
                          </a>
                        </>
                      ) : null}
                    </div>
                  </header>

                  <div style={{ padding: "var(--card-pad)" }}>
                    <div className="mb-3.5 flex items-center justify-between gap-3">
                      <span className="label">
                        {view === "recap" ? "Recap" : "Outline"}
                      </span>
                      <div
                        className="flex gap-0.5 rounded-lg border border-[var(--border)] bg-[var(--raise)] p-0.5"
                        role="tablist"
                        aria-label="Detail view"
                      >
                        {(["recap", "graph"] as const).map((v) => (
                          <button
                            key={v}
                            type="button"
                            role="tab"
                            aria-selected={view === v}
                            onClick={() => setView(v)}
                            className={cn(
                              "btn-press rounded-md px-3 py-1 font-mono text-[11px] font-semibold transition-colors",
                              view === v
                                ? "bg-[var(--ac)] text-[var(--ac-on)]"
                                : "text-[var(--ink-dim)] hover:text-[var(--ink)]",
                            )}
                          >
                            {v}
                            {v === "graph" ? (
                              <span className="ml-1.5 opacity-55">g</span>
                            ) : null}
                          </button>
                        ))}
                      </div>
                    </div>

                    {view === "recap" ? (
                      <RecapView key={current.id} item={current} />
                    ) : (
                      <GraphView item={current} />
                    )}
                  </div>
                </div>
              </div>

              <ActionBar
                onKeep={doKeep}
                onDrop={doDrop}
                onSkip={doSkip}
                onUndo={doUndo}
                onOpen={openUrl}
                openDisabled={!current.url}
                undoDisabled={!undoToken}
                busy={keepMut.isPending || dropMut.isPending}
              />
            </>
          ) : null}
        </section>
      </div>
    </AppShell>
  );
}

function Tally({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: boolean;
}) {
  return (
    <span className="flex items-baseline gap-1">
      <span
        className={cn(
          "tnum font-mono text-[12px] font-bold",
          accent && value > 0 ? "text-[var(--ac)]" : "text-[var(--ink-muted)]",
        )}
      >
        {value}
      </span>
      <span className="meta">{label}</span>
    </span>
  );
}

/** Recaps run from a two-line clip note to a 15k-character article dump. */
const LONG_RECAP = 2600;

function RecapView({ item }: { item: ReviewItem }) {
  const [expanded, setExpanded] = useState(false);
  const long = item.summary.length > LONG_RECAP;
  const clipped = long && !expanded;

  return (
    <>
      <div
        className={cn(
          "recap-slab relative",
          clipped && "max-h-[540px] overflow-hidden",
        )}
      >
        <Markdown body={item.summary} title={item.title} linkPages={false} />
        {clipped ? (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-[var(--raise)] via-[var(--raise)]/85 to-transparent"
          />
        ) : null}
      </div>

      {long ? (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="btn mt-3"
        >
          {expanded ? (
            <>
              <ChevronUp className="h-4 w-4" aria-hidden="true" /> Collapse
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" aria-hidden="true" /> Show full
              text
              <span className="meta">
                {item.length ||
                  `${Math.round(item.summary.length / 1000)}k chars`}
              </span>
            </>
          )}
        </button>
      ) : null}

      {item.tags.length ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {item.tags.map((tag) => (
            <span key={tag} className="pill">
              {tag}
            </span>
          ))}
        </div>
      ) : null}

      <div className="mt-6 flex flex-wrap gap-x-6 gap-y-1">
        {item.queued ? (
          <span className="meta">queued {item.queued}</span>
        ) : null}
        {item.length ? <span className="meta">{item.length}</span> : null}
        {item.tokens ? <span className="meta">{item.tokens}</span> : null}
      </div>
    </>
  );
}

/**
 * The structural view: the clipped article's own section headings plus the
 * pages it already touches in the wiki. The feeder leaves `at`/`target` empty
 * for articles and fills them only for timestamped video breakdowns, so both
 * columns are rendered conditionally rather than as empty gutters.
 */
/**
 * Headings arrive from the clipper with half-stripped emphasis ("Summary**"),
 * so trim stray markers rather than rendering them.
 */
const cleanLabel = (s: string) =>
  (s ?? "")
    .replace(/^[\s*_#`>]+/, "")
    .replace(/[\s*_`]+$/, "")
    .trim();

function GraphView({ item }: { item: ReviewItem }) {
  const sections = item.breakdown
    .map((b) => ({ ...b, label: cleanLabel(b.label) }))
    .filter((b) => b.label || b.at?.trim());
  const timed = sections.some((b) => b.at?.trim());

  if (!sections.length && !item.overlaps.length) {
    return (
      <div className="surface flex flex-col items-center gap-2 px-6 py-10 text-center">
        <Waypoints
          className="h-6 w-6 text-[var(--ink-fainter)]"
          aria-hidden="true"
        />
        <p className="text-[13.5px] text-[var(--ink-dim)]">
          No structure extracted for this item.
        </p>
        <p className="meta max-w-[320px]">
          Outlines come from the clipped headings; overlaps appear once the item
          touches an existing wiki page.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-7">
      {sections.length ? (
        <section>
          <div className="label mb-2.5">
            {timed ? "Timeline" : "Sections"}
            <span className="ml-2 font-normal opacity-70">
              {sections.length}
            </span>
          </div>
          <ol className="relative flex flex-col">
            <span
              aria-hidden="true"
              className="absolute top-3 bottom-3 left-[3.5px] w-px bg-[var(--border)]"
            />
            {sections.map((b, i) => (
              <li key={i} className="relative py-1.5 pl-7">
                <span
                  aria-hidden="true"
                  className="absolute top-[11px] left-0 h-2 w-2 rounded-full border border-[var(--rail-neutral)] bg-[var(--node)]"
                />
                <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                  {b.at?.trim() ? (
                    <span className="tnum shrink-0 font-mono text-[11.5px] font-semibold text-[var(--ac)]">
                      {b.at}
                    </span>
                  ) : null}
                  <span className="min-w-0 flex-1 text-[13.5px] leading-snug text-[var(--ink)]">
                    {b.label}
                  </span>
                </div>
                {b.target?.trim() ? (
                  <a
                    href={b.target}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="meta mt-0.5 block break-all hover:text-[var(--ac)]"
                  >
                    {b.target}
                  </a>
                ) : null}
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      {item.overlaps.length ? (
        <section>
          <div className="label mb-2.5">
            Overlaps
            <span className="ml-2 font-normal opacity-70">
              {item.overlaps.length}
            </span>
          </div>
          <div className="flex flex-col gap-2">
            {item.overlaps.map((o) => (
              <Link
                key={o.page}
                to={`/wiki/${o.page.replace(/^\//, "")}`}
                className="group flex flex-wrap items-center gap-x-3 gap-y-1 rounded-lg border border-[var(--border-soft)] bg-[var(--sunk)] px-3.5 py-2.5 transition-colors hover:border-[rgba(var(--ac-rgb),0.45)]"
              >
                <span className="font-mono text-xs font-medium text-[var(--ac)]">
                  {o.page}
                </span>
                <span
                  className="hidden h-3.5 w-px bg-[var(--rail-neutral)] sm:block"
                  aria-hidden="true"
                />
                <span className="min-w-0 flex-1 text-[12.5px] text-[var(--ink-dim)]">
                  {o.note}
                </span>
                <ArrowUpRight
                  className="h-3.5 w-3.5 shrink-0 text-[var(--ink-fainter)] transition-colors group-hover:text-[var(--ac)]"
                  aria-hidden="true"
                />
              </Link>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}

function ActionBar({
  onKeep,
  onDrop,
  onSkip,
  onUndo,
  onOpen,
  openDisabled,
  undoDisabled,
  busy,
}: {
  onKeep: () => void;
  onDrop: () => void;
  onSkip: () => void;
  onUndo: () => void;
  onOpen: () => void;
  openDisabled: boolean;
  undoDisabled: boolean;
  busy: boolean;
}) {
  return (
    <footer className="shrink-0 border-t border-[var(--border)] bg-[var(--panel)] pb-[max(env(safe-area-inset-bottom),0px)]">
      <div
        className="mx-auto grid w-full max-w-[820px] grid-cols-3 items-center gap-2 sm:flex sm:flex-wrap"
        style={{ padding: "var(--bar-pad)" }}
      >
        <button
          type="button"
          disabled={busy}
          onClick={onKeep}
          className="btn btn-accent"
        >
          <Check className="h-4 w-4" aria-hidden="true" />
          Keep
          <Kbd className="!border-black/20 !bg-black/25 !text-[var(--ac-on)] max-[380px]:hidden">
            k
          </Kbd>
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={onDrop}
          className="btn btn-danger"
        >
          <X className="h-4 w-4" aria-hidden="true" />
          Drop
          <Kbd className="max-[380px]:hidden">d</Kbd>
        </button>
        <button type="button" onClick={onSkip} className="btn">
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
          Skip
        </button>

        <span
          className="mx-1 hidden h-[22px] w-px bg-[var(--border)] sm:block"
          aria-hidden="true"
        />

        <button
          type="button"
          onClick={onOpen}
          disabled={openDisabled}
          className="btn"
        >
          <ExternalLink className="h-4 w-4" aria-hidden="true" />
          Open
          <Kbd className="max-[380px]:hidden">o</Kbd>
        </button>
        <button
          type="button"
          disabled={undoDisabled}
          onClick={onUndo}
          className="btn"
        >
          <Undo2 className="h-4 w-4" aria-hidden="true" />
          Undo
          <Kbd className="max-[380px]:hidden">u</Kbd>
        </button>
      </div>
    </footer>
  );
}
