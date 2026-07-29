import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight } from "lucide-react";
import type { WikiNavEntry } from "@second-brain/types";
import { fetchWikiPages } from "../../lib/api";

const GROUP_LABELS: Record<string, string> = {
  entities: "Entities",
  concepts: "Concepts",
  recaps: "Recaps",
  digests: "Digests",
  _: "Other",
};

const GROUP_ORDER = ["concepts", "entities", "digests", "recaps", "_"];

export function WikiIndexPage() {
  const { data, isLoading } = useQuery({ queryKey: ["wikiPages"], queryFn: fetchWikiPages });
  const entries = useMemo(() => data?.entries ?? [], [data?.entries]);

  const grouped = useMemo(() => {
    const acc: Record<string, WikiNavEntry[]> = {};
    for (const e of entries) {
      if (e.slug === "index") continue;
      (acc[e.group] ??= []).push(e);
    }
    return GROUP_ORDER.filter((g) => acc[g]?.length).map((g) => [g, acc[g]] as const);
  }, [entries]);

  if (isLoading) {
    return <div className="p-8 text-[var(--ink-dim)]">Loading wiki…</div>;
  }

  const index = entries.find((e) => e.slug === "index");

  return (
    <div className="mx-auto w-full max-w-[900px]" style={{ padding: "var(--card-pad)" }}>
      <header className="mb-8 border-b border-[var(--border-soft)] pb-6">
        <p className="label mb-2">Map of content</p>
        <h2
          className="text-balance font-bold tracking-tight text-[var(--ink-bright)]"
          style={{ fontSize: "calc(var(--title-size) * 1.15)" }}
        >
          {index?.title ?? "Second Brain"}
        </h2>
        <p className="measure mt-3 text-[14px] leading-relaxed text-[var(--ink-dim)]">
          {entries.length} synthesised pages across entities, concepts, recaps and digests. Every
          claim traces back to an immutable source.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {grouped.map(([group, list]) => (
            <a key={group} href={`#g-${group}`} className="pill hover:border-[var(--ac)] hover:text-[var(--ac)]">
              {GROUP_LABELS[group] ?? group}
              <span className="tnum opacity-70">{list.length}</span>
            </a>
          ))}
        </div>
      </header>

      {grouped.map(([group, list]) => (
        <section key={group} id={`g-${group}`} className="mb-9 scroll-mt-4">
          <h3 className="label mb-3">
            {GROUP_LABELS[group] ?? group}
            <span className="ml-2 font-normal opacity-70">{list.length}</span>
          </h3>
          <div className="grid gap-2 sm:grid-cols-2">
            {list.map((e) => (
              <Link
                key={e.slug}
                to={`/wiki/${e.slug}`}
                className="group flex items-start gap-2 rounded-xl border border-[var(--border-soft)] bg-[var(--raise)] px-3.5 py-3 transition-colors hover:border-[rgba(var(--ac-rgb),0.45)] hover:bg-[var(--node)]"
              >
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13.5px] font-medium text-[var(--ink)] group-hover:text-[var(--ink-bright)]">
                    {e.title}
                  </span>
                  <span className="meta mt-0.5 block truncate">
                    {e.slug}
                    {e.status === "stub" ? " · stub" : ""}
                  </span>
                </span>
                <ArrowUpRight
                  className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--ink-fainter)] transition-colors group-hover:text-[var(--ac)]"
                  aria-hidden="true"
                />
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
