import type {
  DropResponse,
  FeedRunJob,
  FeedStatsRow,
  KeepResponse,
  NewFeedRequest,
  NewWebpageRequest,
  QueueResponse,
  Settings,
  SettingsPatch,
  SourceResponse,
  WikiIndexResponse,
  WikiPageResponse,
} from "@second-brain/types";
import { api } from "./utils";

export function fetchQueue(demo = false) {
  return api<QueueResponse>(`/api/review/queue?demo=${demo ? "1" : "0"}`);
}

export function keepItem(id: string, demo = false) {
  return api<KeepResponse>("/api/review/keep", {
    method: "POST",
    body: JSON.stringify({ id, demo }),
  });
}

export function dropItem(id: string, demo = false) {
  return api<DropResponse>("/api/review/drop", {
    method: "POST",
    body: JSON.stringify({ id, demo }),
  });
}

export function undoAction(undoToken: string) {
  return api<{ ok: boolean }>("/api/review/undo", {
    method: "POST",
    body: JSON.stringify({ undoToken }),
  });
}

export function fetchFeedStats() {
  return api<{ rows: FeedStatsRow[] }>("/api/feeds/stats");
}

export function runFeeder() {
  return api<FeedRunJob>("/api/feeds/run", { method: "POST" });
}

export function pollFeedRun(jobId: string) {
  return api<FeedRunJob>(`/api/feeds/run/${jobId}`);
}

export function subscribeFeed(body: NewFeedRequest) {
  return api<{ ok: boolean; id: string }>("/api/feeds/subscribe", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function createWebpage(body: NewWebpageRequest) {
  return api<{ placed: string }>("/api/sources/webpage", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchSettings() {
  return api<Settings>("/api/settings");
}

export function patchSettings(body: SettingsPatch) {
  return api<Settings>("/api/settings", {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function fetchWikiPages() {
  return api<WikiIndexResponse>("/api/wiki/pages");
}

export function fetchWikiPage(slug: string) {
  return api<WikiPageResponse>(`/api/wiki/page/${slug}`);
}

export function fetchSource(id: string) {
  return api<SourceResponse>(`/api/sources/${id}`);
}
