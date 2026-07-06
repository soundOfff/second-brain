import type { ReactNode } from "react";
import { cn } from "../lib/utils";

export function Kbd({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <kbd
      className={cn(
        "inline-flex items-center rounded px-1.5 py-0.5 font-mono text-[10.5px] font-bold leading-normal",
        "border border-[rgba(var(--ac-rgb),0.34)] bg-[rgba(var(--ac-rgb),0.16)] text-[var(--ac)]",
        className,
      )}
    >
      {children}
    </kbd>
  );
}
