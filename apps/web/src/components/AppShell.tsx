import type { ReactNode } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { cn } from "../lib/utils";

type Props = {
  mode: "feed" | "wiki";
  children: ReactNode;
  sessionStat?: string;
};

const FEED_TABS = [
  { id: "review", label: "Review Queue", key: "r", path: "review" },
  { id: "stats", label: "Feed Stats", key: "f", path: "stats" },
  { id: "settings", label: "Settings", key: "s", path: "settings" },
] as const;

export function AppShell({ mode, children, sessionStat }: Props) {
  const location = useLocation();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const demo = params.get("demo") === "1";
  const qs = demo ? "?demo=1" : "";

  const screen = location.pathname.split("/").pop() ?? "review";
  const title =
    mode === "feed"
      ? `Brain Feed — ${FEED_TABS.find((t) => t.path === screen)?.label ?? "Review Queue"}`
      : "Second Brain — Wiki";

  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-[22px] p-5 md:p-10">
      <div
        className="enter flex h-[720px] w-full max-w-[1080px] flex-col overflow-hidden rounded-xl border border-[var(--frame)] bg-[var(--bg)] shadow-[0_40px_90px_-20px_rgba(0,0,0,0.65),0_12px_30px_-12px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.04)]"
        data-density={document.documentElement.dataset.density}
        data-intensity={document.documentElement.dataset.intensity}
      >
        {/* title bar */}
        <header className="relative flex h-12 shrink-0 items-center border-b border-[var(--border)] bg-gradient-to-b from-[#262320] to-[#211e1b] px-3.5">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
            <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
            <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          </div>
          <div className="pointer-events-none absolute inset-x-0 text-center font-mono text-[12.5px] font-medium tracking-wide text-[var(--ink-muted)]">
            {title}
          </div>
          {sessionStat ? (
            <div className="tnum z-[1] ml-auto font-mono text-[10.5px] tracking-wide text-[var(--ink-faint)]">
              {sessionStat}
            </div>
          ) : null}
        </header>

        {/* top tab bar */}
        <nav className="flex shrink-0 items-center gap-1 border-b border-[var(--border-soft)] bg-[var(--panel)] px-4 py-2">
          {mode === "feed" ? (
            <>
              {FEED_TABS.map((tab) => (
                <Link
                  key={tab.id}
                  to={`/feed/${tab.path}${qs}`}
                  className={cn(
                    "btn-press rounded-md px-3 py-1.5 font-mono text-[11px] font-semibold transition-colors",
                    screen === tab.path
                      ? "bg-[var(--ac)] text-[var(--ac-on)]"
                      : "text-[var(--ink-dim)] hover:text-[var(--ink-muted)]",
                  )}
                >
                  {tab.label}
                  <span className="ml-1.5 opacity-55">{tab.key}</span>
                </Link>
              ))}
              <div className="flex-1" />
              <Link
                to="/wiki"
                className="btn-press rounded-md border border-[var(--rail-neutral)] px-2.5 py-1 font-mono text-[10.5px] font-semibold text-[var(--ink-muted)] hover:border-[var(--ac)] hover:text-[var(--ac)]"
              >
                Wiki
              </Link>
            </>
          ) : (
            <>
              <span className="font-mono text-[11px] font-semibold text-[var(--ac)]">Wiki</span>
              <div className="flex-1" />
              <button
                type="button"
                onClick={() => navigate(`/feed/review${qs}`)}
                className="btn-press rounded-md border border-[var(--rail-neutral)] px-2.5 py-1 font-mono text-[10.5px] font-semibold text-[var(--ink-muted)] hover:border-[var(--ac)] hover:text-[var(--ac)]"
              >
                Feed
              </button>
            </>
          )}
        </nav>

        <div className="flex min-h-0 flex-1 flex-col">{children}</div>
      </div>
    </div>
  );
}
