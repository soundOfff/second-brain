import { useEffect, useState, type ReactNode } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { BrainMark } from "./BrainMark";
import { NAV_ITEMS, activeNavId } from "./nav";
import { useBrainShortcuts } from "../hooks/useBrainShortcuts";
import { cn } from "../lib/utils";

type Props = {
  /** page name — rendered as the <h1> of the top bar */
  title: string;
  /** small mono line under the title */
  subtitle?: ReactNode;
  /** slot before the title (the contextual-panel toggle on narrow screens) */
  leading?: ReactNode;
  /** slot at the right end of the top bar */
  actions?: ReactNode;
  /** false when the page manages its own scroll regions (split panes) */
  scroll?: boolean;
  children: ReactNode;
};

export function AppShell({ title, subtitle, leading, actions, scroll = true, children }: Props) {
  const location = useLocation();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const demo = params.get("demo") === "1";
  const qs = demo ? "?demo=1" : "";
  const [navOpen, setNavOpen] = useState(false);

  const active = activeNavId(location.pathname);

  // close the mobile nav whenever the route changes
  useEffect(() => setNavOpen(false), [location.pathname]);

  useEffect(() => {
    if (!navOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setNavOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navOpen]);

  // section navigation works from every screen, not just the queue
  useBrainShortcuts({
    review: () => navigate(`/feed/review${qs}`),
    stats: () => navigate(`/feed/stats${qs}`),
    settings: () => navigate(`/feed/settings${qs}`),
    wiki: () => navigate("/wiki"),
    toggleScreen: () =>
      navigate(location.pathname.includes("stats") ? `/feed/review${qs}` : `/feed/stats${qs}`),
  });

  return (
    <div className="flex h-dvh w-full overflow-hidden">
      <a href="#main" className="skip-link">
        Skip to content
      </a>

      {/* ── rail: persistent on ≥md, drawer below ── */}
      <nav
        aria-label="Sections"
        className="hidden w-[var(--rail-w)] shrink-0 flex-col items-center gap-1 border-r border-[var(--border)] bg-[var(--panel)] py-3 md:flex"
      >
        <Link
          to={`/feed/review${qs}`}
          aria-label="Second Brain — home"
          className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl border border-[rgba(var(--ac-rgb),0.24)] bg-[rgba(var(--ac-rgb),0.09)] text-[var(--ac)] transition-colors hover:bg-[rgba(var(--ac-rgb),0.16)]"
        >
          <BrainMark className="h-5 w-5" />
        </Link>

        {NAV_ITEMS.map((item) => (
          <RailLink key={item.id} item={item} active={active === item.id} qs={qs} />
        ))}

        <div className="flex-1" />
        {demo ? (
          <span className="rotate-180 font-mono text-[9px] font-bold tracking-[0.2em] text-[var(--ac)] [writing-mode:vertical-rl]">
            DEMO
          </span>
        ) : null}
      </nav>

      {/* ── main column ── */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[var(--topbar-h)] shrink-0 items-center gap-3 border-b border-[var(--border)] bg-gradient-to-b from-[#232019] to-[#1d1b17] px-3 sm:px-5">
          <button
            type="button"
            onClick={() => setNavOpen(true)}
            aria-label="Open navigation"
            aria-expanded={navOpen}
            className="btn btn-icon md:hidden"
          >
            <Menu className="h-4 w-4" aria-hidden="true" />
          </button>

          {leading}

          <div className="min-w-0 flex-1">
            <h1 className="truncate text-[14px] font-semibold tracking-tight text-[var(--ink-bright)]">
              {title}
            </h1>
            {subtitle ? <div className="meta truncate">{subtitle}</div> : null}
          </div>

          {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
        </header>

        <main
          id="main"
          key={location.pathname}
          className={cn(
            "enter flex min-h-0 flex-1",
            scroll ? "scroll flex-col overflow-y-auto" : "overflow-hidden",
          )}
        >
          {children}
        </main>
      </div>

      {/* ── mobile nav drawer ── */}
      <div
        className={cn(
          "fixed inset-0 z-50 md:hidden",
          navOpen ? "pointer-events-auto" : "pointer-events-none",
        )}
        aria-hidden={!navOpen}
      >
        <button
          type="button"
          tabIndex={-1}
          aria-hidden="true"
          onClick={() => setNavOpen(false)}
          className={cn(
            "absolute inset-0 bg-black/60 backdrop-blur-[2px] transition-opacity duration-200",
            navOpen ? "opacity-100" : "opacity-0",
          )}
        />
        <nav
          aria-label="Sections"
          className={cn(
            "absolute inset-y-0 left-0 flex w-[262px] max-w-[84vw] flex-col border-r border-[var(--border)] bg-[var(--panel)] p-3 shadow-2xl transition-transform duration-200 [transition-timing-function:var(--ease)]",
            navOpen ? "translate-x-0" : "-translate-x-full",
          )}
        >
          <div className="mb-4 flex items-center gap-2.5 px-1">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-[rgba(var(--ac-rgb),0.24)] bg-[rgba(var(--ac-rgb),0.09)] text-[var(--ac)]">
              <BrainMark className="h-[18px] w-[18px]" />
            </span>
            <span className="flex-1 font-mono text-[12px] font-semibold tracking-wide text-[var(--ink)]">
              Second Brain
            </span>
            <button
              type="button"
              onClick={() => setNavOpen(false)}
              aria-label="Close navigation"
              className="btn btn-icon"
              tabIndex={navOpen ? 0 : -1}
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>

          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = active === item.id;
            return (
              <Link
                key={item.id}
                to={item.id === "wiki" ? item.to : `${item.to}${qs}`}
                aria-current={isActive ? "page" : undefined}
                tabIndex={navOpen ? 0 : -1}
                className={cn(
                  "mb-0.5 flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-colors",
                  isActive
                    ? "bg-[var(--sel-bg)] text-[var(--ac)]"
                    : "text-[var(--ink-dim)] hover:bg-white/[0.035] hover:text-[var(--ink)]",
                )}
              >
                <Icon className="h-[18px] w-[18px]" aria-hidden="true" />
                <span className="flex-1">{item.full}</span>
                <kbd className="meta">{item.hint}</kbd>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}

function RailLink({ item, active, qs }: { item: (typeof NAV_ITEMS)[number]; active: boolean; qs: string }) {
  const Icon = item.icon;
  return (
    <Link
      to={item.id === "wiki" ? item.to : `${item.to}${qs}`}
      aria-current={active ? "page" : undefined}
      title={`${item.full} · ${item.hint}`}
      className={cn(
        "group relative flex w-[58px] flex-col items-center gap-1 rounded-xl py-2.5 transition-colors",
        active
          ? "bg-[var(--sel-bg)] text-[var(--ac)]"
          : "text-[var(--ink-dim)] hover:bg-white/[0.035] hover:text-[var(--ink)]",
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          "absolute top-1/2 -left-3 h-6 w-[2px] -translate-y-1/2 rounded-r bg-[var(--ac)] transition-opacity",
          active ? "opacity-100" : "opacity-0",
        )}
      />
      <Icon className="h-[18px] w-[18px]" aria-hidden="true" />
      <span className="font-mono text-[9.5px] font-semibold tracking-wide">{item.label}</span>
    </Link>
  );
}
