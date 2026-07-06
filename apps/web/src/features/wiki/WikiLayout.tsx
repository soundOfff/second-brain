import type { WikiNavEntry } from "@second-brain/types";
import { Outlet } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Link, useLocation } from "react-router-dom";
import { AppShell } from "../../components/AppShell";
import { fetchWikiPages } from "../../lib/api";
import { cn } from "../../lib/utils";

const GROUP_LABELS: Record<string, string> = {
  entities: "Entities",
  concepts: "Concepts",
  recaps: "Recaps",
  digests: "Digests",
  _: "Other",
};

export function WikiLayout() {
  const { data } = useQuery({ queryKey: ["wikiPages"], queryFn: fetchWikiPages });
  const location = useLocation();

  const grouped = (data?.entries ?? []).reduce<Record<string, WikiNavEntry[]>>((acc, e) => {
    (acc[e.group] ??= []).push(e);
    return acc;
  }, {});

  return (
    <AppShell mode="wiki">
      <div className="flex min-h-0 flex-1">
        <aside className="scroll w-56 shrink-0 overflow-y-auto border-r border-[var(--border)] bg-[var(--panel)] p-3">
          <Link
            to="/wiki"
            className={cn(
              "mb-3 block rounded-md px-2 py-1 font-mono text-[11px] font-semibold",
              location.pathname === "/wiki" ? "bg-[var(--ac)] text-[var(--ac-on)]" : "text-[var(--ink-dim)] hover:text-[var(--ink-muted)]",
            )}
          >
            Map
          </Link>
          {Object.entries(grouped).map(([group, entries]) => (
            <div key={group} className="mb-3">
              <div className="mb-1 px-2 font-mono text-[9px] font-bold uppercase tracking-wider text-[var(--ink-faint)]">
                {GROUP_LABELS[group] ?? group}
              </div>
              {entries?.map((e) => {
                const path = `/wiki/${e.slug}`;
                const active = location.pathname === path;
                return (
                  <Link
                    key={e.slug}
                    to={path}
                    className={cn(
                      "block truncate rounded px-2 py-1 text-[12px]",
                      active ? "bg-[var(--sel-bg)] text-[var(--ac)]" : "text-[var(--ink-dim)] hover:text-[var(--ink-muted)]",
                    )}
                  >
                    {e.title}
                    {e.status === "stub" ? (
                      <span className="ml-1 font-mono text-[9px] text-[var(--ink-faint)]">stub</span>
                    ) : null}
                  </Link>
                );
              })}
            </div>
          ))}
        </aside>
        <main className="scroll min-w-0 flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </AppShell>
  );
}
