/** Second-brain monogram: three linked nodes. Inherits currentColor. */
export function BrainMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" focusable="false">
      <path
        d="M6.5 8.5 17.5 8.5 12 17.5Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.25"
        strokeLinejoin="round"
        opacity="0.45"
      />
      <circle cx="6.5" cy="8.5" r="2.15" fill="currentColor" />
      <circle cx="17.5" cy="8.5" r="2.15" fill="currentColor" />
      <circle cx="12" cy="17.5" r="2.15" fill="currentColor" />
    </svg>
  );
}
