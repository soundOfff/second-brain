import { BookOpen, Inbox, Rss, SlidersHorizontal, type LucideIcon } from "lucide-react";

export type NavItem = {
  id: string;
  /** short label under the rail icon */
  label: string;
  /** full label used in the mobile drawer and page titles */
  full: string;
  to: string;
  icon: LucideIcon;
  hint: string;
  /** matches when the pathname starts with this */
  match: string;
};

export const NAV_ITEMS: NavItem[] = [
  { id: "review", label: "Queue", full: "Review Queue", to: "/feed/review", icon: Inbox, hint: "r", match: "/feed/review" },
  { id: "stats", label: "Feeds", full: "Feed Stats", to: "/feed/stats", icon: Rss, hint: "f", match: "/feed/stats" },
  { id: "wiki", label: "Wiki", full: "Wiki", to: "/wiki", icon: BookOpen, hint: "w", match: "/wiki" },
  { id: "settings", label: "Settings", full: "Settings", to: "/feed/settings", icon: SlidersHorizontal, hint: "s", match: "/feed/settings" },
];

export function activeNavId(pathname: string): string | undefined {
  return NAV_ITEMS.find((item) => pathname.startsWith(item.match))?.id;
}
