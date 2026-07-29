import { useEffect, useRef, type ReactNode } from "react";
import { PanelLeft, X } from "lucide-react";
import { useIsDesktop } from "../hooks/useMediaQuery";
import { cn } from "../lib/utils";

type Props = {
  open: boolean;
  onClose: () => void;
  /** accessible name for the region */
  label: string;
  children: ReactNode;
};

/**
 * Contextual list column (queue, wiki tree). A static column from `lg` up, a
 * slide-over drawer below it. Must be placed inside a `relative` container.
 */
export function SidePanel({ open, onClose, label, children }: Props) {
  const isDesktop = useIsDesktop();
  const ref = useRef<HTMLElement>(null);
  const drawerOpen = open && !isDesktop;

  useEffect(() => {
    if (!drawerOpen) return;
    ref.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawerOpen, onClose]);

  return (
    <>
      {!isDesktop ? (
        <div
          onClick={onClose}
          aria-hidden="true"
          className={cn(
            "absolute inset-0 z-30 bg-black/55 backdrop-blur-[2px] transition-opacity duration-200",
            drawerOpen ? "opacity-100" : "pointer-events-none opacity-0",
          )}
        />
      ) : null}

      <aside
        ref={ref}
        tabIndex={-1}
        aria-label={label}
        inert={!isDesktop && !open}
        className={cn(
          "absolute inset-y-0 left-0 z-40 flex w-[min(var(--panel-w),86vw)] flex-col border-r border-[var(--border)] bg-[var(--panel)] shadow-2xl outline-none transition-transform duration-200 [transition-timing-function:var(--ease)]",
          "lg:static lg:z-auto lg:w-[var(--panel-w)] lg:shrink-0 lg:translate-x-0 lg:shadow-none",
          drawerOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <button
          type="button"
          onClick={onClose}
          className="btn btn-icon absolute top-2.5 right-2.5 z-10 lg:hidden"
          aria-label={`Close ${label}`}
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
        {children}
      </aside>
    </>
  );
}

/** Top-bar control that reveals the panel below `lg`. */
export function SidePanelToggle({
  onClick,
  label,
  count,
}: {
  onClick: () => void;
  label: string;
  count?: number;
}) {
  return (
    <button type="button" onClick={onClick} className="btn shrink-0 lg:hidden" aria-label={`Open ${label}`}>
      <PanelLeft className="h-4 w-4" aria-hidden="true" />
      {count != null ? <span className="tnum font-mono text-[11px]">{count}</span> : null}
    </button>
  );
}
