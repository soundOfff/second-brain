import { useMemo, useState } from "react";
import type { WikiNavEntry } from "@second-brain/types";
import { Link, Outlet, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { AppShell } from "../../components/AppShell";
import { SidePanel, SidePanelToggle } from "../../components/SidePanel";
import { fetchWikiPages } from "../../lib/api";
import { cn } from "../../lib/utils";

const GROUP_LABELS: Record<string, string> = {
  entities: "Entities",
  concepts: "Concepts",
  recaps: "Recaps",
  digests: "Digests",
  _: "Other",
};

const GROUP_ORDER = ["_", "concepts", "entities", "digests", "recaps"];

export function WikiLayout() {
  const { data } = useQuery({ queryKey: ["wikiPages"], queryFn: fetchWikiPages });
  const location = useLocation();
  const [panelOpen, setPanelOpen] = useState(false);
  const [filter, setFilter] = useState("");

  const entries = useMemo(() => data?.entries ?? [], [data?.entries]);
  const slug = location.pathname.replace(/^\/wiki\/?/, "");

  const matches = useMemo(() => {
    // `index` has its own "Map of content" entry above the tree
    const listed = entries.filter((e) => e.slug !== "index");
    const q = filter.trim().toLowerCase();
    if (!q) return listed;
    return listed.filter(
      (e) => e.title.toLowerCase().includes(q) || e.slug.toLowerCase().includes(q),
    );
  }, [entries, filter]);

  const grouped = useMemo(() => {
    const acc: Record<string, WikiNavEntry[]> = {};
    for (const e of matches) (acc[e.group] ??= []).push(e);
    return Object.entries(acc).sort(
      ([a], [b]) =>
        (GROUP_ORDER.indexOf(a) + 1 || 99) - (GROUP_ORDER.indexOf(b) + 1 || 99) || a.localeCompare(b),
    );
  }, [matches]);

  const active = entries.find((e) => e.slug === slug);
  const title = !slug
    ? "Wiki"
    : (active?.title ?? (slug.startsWith("source/") ? "Source" : slug.split("/").pop() ?? "Wiki"));
  const subtitle = !slug ? `${entries.length} pages` : slug;

  return (
    <AppShell
      title={title}
      subtitle={subtitle}
      scroll={false}
      leading={<SidePanelToggle onClick={() => setPanelOpen(true)} label="wiki pages" count={entries.length} />}
    >
      <div className="relative flex min-h-0 w-full">
        <SidePanel open={panelOpen} onClose={() => setPanelOpen(false)} label="Wiki pages">
          <div className="border-b border-[var(--border-soft)] p-3 pr-14 lg:pr-3">
            <div className="relative">
              <Search
                className="pointer-events-none absolute top-1/2 left-2.5 h-3.5 w-3.5 -translate-y-1/2 text-[var(--ink-faint)]"
                aria-hidden="true"
              />
              <input
                type="search"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Filter pages…"
                aria-label="Filter wiki pages"
                className="field pl-8"
              />
            </div>
          </div>

          <nav aria-label="Wiki pages" className="scroll min-h-0 flex-1 overflow-y-auto p-3">
            <Link
              to="/wiki"
              aria-current={location.pathname === "/wiki" ? "page" : undefined}
              onClick={() => setPanelOpen(false)}
              className={cn(
                "mb-3 block rounded-md px-2 py-1.5 font-mono text-[11px] font-semibold transition-colors",
                location.pathname === "/wiki"
                  ? "bg-[var(--ac)] text-[var(--ac-on)]"
                  : "text-[var(--ink-dim)] hover:text-[var(--ink)]",
              )}
            >
              Map of content
            </Link>

            {grouped.length ? (
              grouped.map(([group, list]) => (
                <div key={group} className="mb-4">
                  <div className="label mb-1.5 flex items-baseline justify-between px-2">
                    <span>{GROUP_LABELS[group] ?? group}</span>
                    <span className="tnum font-normal opacity-70">{list.length}</span>
                  </div>
                  {list.map((e) => {
                    const path = `/wiki/${e.slug}`;
                    const isActive = location.pathname === path;
                    return (
                      <Link
                        key={e.slug}
                        to={path}
                        aria-current={isActive ? "page" : undefined}
                        onClick={() => setPanelOpen(false)}
                        className={cn(
                          "flex items-center gap-1.5 rounded px-2 py-1.5 text-[12.5px] transition-colors",
                          isActive
                            ? "bg-[var(--sel-bg)] text-[var(--ac)]"
                            : "text-[var(--ink-dim)] hover:bg-white/[0.03] hover:text-[var(--ink)]",
                        )}
                      >
                        <span className="truncate">{e.title}</span>
                        {e.status === "stub" ? (
                          <span className="meta shrink-0 opacity-80">stub</span>
                        ) : null}
                      </Link>
                    );
                  })}
                </div>
              ))
            ) : (
              <p className="px-2 py-6 text-center text-[12.5px] text-[var(--ink-dim)]">
                No pages match “{filter}”.
              </p>
            )}
          </nav>
        </SidePanel>

        <div className="scroll min-w-0 flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </div>
    </AppShell>
  );
}
