import { useEffect, useRef } from "react";

export type ShortcutAction =
  | "keep"
  | "drop"
  | "skip"
  | "open"
  | "undo"
  | "rescan"
  | "toggleView"
  | "next"
  | "prev"
  | "review"
  | "stats"
  | "settings"
  | "wiki"
  | "toggleScreen";

const SHORTCUTS: Array<{ key: string; action: ShortcutAction; when?: "shift" }> = [
  { key: "k", action: "keep" },
  { key: "Enter", action: "keep" },
  { key: "d", action: "drop" },
  { key: "ArrowRight", action: "skip" },
  { key: "o", action: "open" },
  { key: "u", action: "undo" },
  { key: "r", action: "rescan", when: "shift" },
  { key: "g", action: "toggleView" },
  { key: "ArrowDown", action: "next" },
  { key: "ArrowUp", action: "prev" },
  { key: "r", action: "review" },
  { key: "f", action: "stats" },
  { key: "s", action: "settings" },
  { key: "w", action: "wiki" },
  { key: "t", action: "toggleScreen" },
];

function isTypingTarget(el: EventTarget | null) {
  if (!(el instanceof HTMLElement)) return false;
  const tag = el.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || el.isContentEditable;
}

/**
 * Binds the global key map. Several components may call this at once — each
 * only claims the actions it actually handles, so the shell can own navigation
 * while a page owns its item-level actions.
 */
export function useBrainShortcuts(
  handlers: Partial<Record<ShortcutAction, () => void>>,
  enabled = true,
) {
  // latest-value ref keeps the listener stable across the page's re-renders
  const ref = useRef(handlers);
  useEffect(() => {
    ref.current = handlers;
  });

  useEffect(() => {
    if (!enabled) return;

    const onKey = (e: KeyboardEvent) => {
      if (isTypingTarget(e.target)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      for (const sc of SHORTCUTS) {
        const shift = sc.when === "shift";
        if (shift && !e.shiftKey) continue;
        if (!shift && e.shiftKey && sc.key === "r" && sc.action === "review") continue;
        if (e.key.toLowerCase() === sc.key.toLowerCase() || e.key === sc.key) {
          const fn = ref.current[sc.action];
          if (fn) {
            e.preventDefault();
            fn();
            return;
          }
        }
      }
    };

    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [enabled]);
}

export const SHORTCUT_REFERENCE: Array<{ cap: string; desc: string }> = [
  { cap: "k / ⏎", desc: "keep — place the item into sources/" },
  { cap: "d", desc: "drop the queued candidate" },
  { cap: "→", desc: "skip — leave it queued, advance" },
  { cap: "o", desc: "open the source url" },
  { cap: "u", desc: "undo the last keep / drop" },
  { cap: "⇧r", desc: "rescan the queue from disk" },
  { cap: "g", desc: "toggle recap / outline" },
  { cap: "↓", desc: "select the next queued item" },
  { cap: "↑", desc: "select the previous queued item" },
  { cap: "r", desc: "go to Review Queue" },
  { cap: "f", desc: "go to Feed Stats" },
  { cap: "w", desc: "go to the Wiki" },
  { cap: "s", desc: "go to Settings" },
  { cap: "t", desc: "toggle review ↔ stats" },
];
