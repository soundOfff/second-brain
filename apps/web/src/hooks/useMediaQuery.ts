import { useEffect, useState } from "react";

/** Subscribes to a media query. SSR-safe-ish: starts false, syncs on mount. */
export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(
    () => typeof window !== "undefined" && window.matchMedia(query).matches,
  );

  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = (e: MediaQueryListEvent) => setMatches(e.matches);
    setMatches(mql.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, [query]);

  return matches;
}

/** `lg` in Tailwind's default scale — where contextual panels stop being drawers. */
export const useIsDesktop = () => useMediaQuery("(min-width: 1024px)");
