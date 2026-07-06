import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { fetchWikiPages } from "../../lib/api";

export function WikiIndexPage() {
  const { data, isLoading } = useQuery({ queryKey: ["wikiPages"], queryFn: fetchWikiPages });

  if (isLoading) return <div className="p-6 text-[var(--ink-dim)]">Loading wiki…</div>;

  const entries = data?.entries ?? [];
  const index = entries.find((e) => e.slug === "index");

  return (
    <div className="p-6" style={{ padding: "var(--card-pad)" }}>
      <h1 className="mb-2 font-bold text-[var(--ink-bright)]" style={{ fontSize: "var(--title-size)" }}>
        {index?.title ?? "Wiki"}
      </h1>
      <p className="mb-6 max-w-xl text-[14px] leading-relaxed text-[var(--ink-dim)]">
        {entries.length} pages across entities, concepts, recaps, and digests. Pick a page from the sidebar or browse below.
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        {entries
          .filter((e) => e.slug !== "index")
          .slice(0, 24)
          .map((e) => (
            <Link
              key={e.slug}
              to={`/wiki/${e.slug}`}
              className="rounded-lg border border-[var(--border-soft)] bg-[var(--raise)] px-3 py-2 text-[13px] text-[var(--ink-muted)] hover:border-[var(--ac)] hover:text-[var(--ac)]"
            >
              <span className="font-mono text-[10px] text-[var(--ink-faint)]">{e.group}</span>
              <div className="font-medium text-[var(--ink)]">{e.title}</div>
            </Link>
          ))}
      </div>
    </div>
  );
}
