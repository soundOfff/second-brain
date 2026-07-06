// Shared JSON contracts between apps/api (FastAPI) and apps/web (React).
// Mirrors the Item model in bin/brain_feed_items.py and the wiki payload
// shape in bin/brain_wiki_data.py — keep them in sync when either side changes.

export type ItemKind =
  | "article"
  | "transcript"
  | "note"
  | "paper"
  | "video"
  | "pdf"
  | "screenshot"
  | "data"
  | "";

export interface Overlap {
  page: string;
  note: string;
}

export interface Breakdown {
  at: string;
  label: string;
  target: string;
}

export interface ReviewItem {
  id: string;
  title: string;
  via: string;
  type: ItemKind | string;
  url: string;
  reason: string;
  summary: string;
  tags: string[];
  overlaps: Overlap[];
  breakdown: Breakdown[];
  queued: string;
  length: string;
  tokens: string;
  // Present for real items (backend uses it to locate the file); absent in demo mode.
  path?: string;
}

export interface QueueResponse {
  items: ReviewItem[];
  demo: boolean;
}

export interface KeepResponse {
  placed: string; // path relative to vault
  undoToken: string;
}

export interface DropResponse {
  undoToken: string;
}

export interface UndoRequest {
  undoToken: string;
}

export interface FeedStatsRow {
  id: string;
  adapter: string;
  trust: "auto" | "queue";
  cap: number;
  total_seen: number;
  today_seen: number;
  queued: number;
  keep_rate: number | null;
}

export interface FeedRunJob {
  jobId: string;
  status: "running" | "done" | "error";
  summary?: string;
  error?: string;
}

export type Accent = "amber" | "indigo" | "emerald" | "mono";
export type Density = "comfortable" | "compact";
export type Intensity = "calm" | "vivid";

export interface Settings {
  default_cap: number;
  model: string;
  accent: Accent;
  density: Density;
  intensity: Intensity;
}

export type SettingsPatch = Partial<Settings>;

// New source form (webpage).
export interface NewWebpageRequest {
  title?: string;
  url?: string;
  body?: string;
  tags?: string[];
}

// Feed subscription (rss | yt | api).
export interface NewFeedRequest {
  kind: "rss" | "yt" | "api";
  title?: string;
  url: string;
  tags?: string[];
  id?: string;
  cap?: number | null;
  trust?: "auto" | "queue";
  mode?: "url" | "text";
  items_path?: string;
  url_field?: string;
  title_field?: string;
  guid_field?: string;
  body_field?: string;
  user_agent?: string;
}

// Wiki payloads.
export interface WikiPageMeta {
  type?: string;
  title?: string;
  created?: string;
  updated?: string;
  status?: "stub" | "active" | "stable" | string;
  sources?: string[];
  tags?: string[];
  aliases?: string[];
}

export interface WikiNavEntry {
  slug: string;
  title: string;
  status?: string;
  group: string; // "entities" | "concepts" | "recaps" | "digests" | "_"
}

export interface WikiIndexResponse {
  entries: WikiNavEntry[];
}

export interface WikiSourceLink {
  id: string;
  exists: boolean;
  title?: string;
}

export interface WikiBacklink {
  slug: string;
  title: string;
}

export interface WikiPageResponse {
  slug: string;
  meta: WikiPageMeta;
  body: string; // raw markdown after frontmatter
  backlinks: WikiBacklink[];
  sources: WikiSourceLink[];
  exists: boolean;
}

export interface SourceCiter {
  slug: string;
  title: string;
}

export interface SourceResponse {
  id: string;
  filename: string;
  raw: string;
  citers: SourceCiter[];
}
