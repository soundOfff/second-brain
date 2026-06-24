// Clip to Brain — popup logic. POSTs to the localhost helper (brain-clip-server.py),
// which shells out to bin/brain-clip.sh. The helper must be running (launchd agent
// com.secondbrain.clipserver, installed by `bin/brain-clip-gui.sh browser`).
//
// The popup only ever sends the active tab's URL (+ optional note/tags) — the backend
// does the fetch + extraction. Suggested tags and the size estimate are read from the
// live page via a one-shot content-script injection (activeTab grant), and are folded
// into the note text the backend prepends above the extracted page body.
const ENDPOINT = "http://127.0.0.1:8766/clip";

// Video hosts the clipper pulls as a captions transcript (mirrors is_video_url in
// brain-clip.sh). Kept in sync by hand — both are tiny host allowlists.
const VIDEO_RE = /^https?:\/\/((www\.|m\.|music\.)*youtube\.com\/|youtu\.be\/|(www\.)*vimeo\.com\/)/i;
const HTTP_RE = /^https?:\/\//i;

const $ = (id) => document.getElementById(id);

const state = {
  url: "",
  title: "",
  kind: "article",   // article | video | local
  clippable: false,
  tags: new Map(),    // name -> selected(bool)
};

// --- load the active tab ---------------------------------------------------
async function loadTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  state.url = tab?.url || "";
  state.title = tab?.title || "";
  state.clippable = HTTP_RE.test(state.url);
  state.kind = !state.clippable ? "local" : VIDEO_RE.test(state.url) ? "video" : "article";

  $("title").textContent = state.title || "(untitled tab)";
  $("url").textContent = state.url;
  renderFavicon(tab?.favIconUrl);
  renderDetection();

  if (state.kind === "local") {
    $("warn").classList.remove("hidden");
    const b = $("clipPage");
    b.classList.add("disabled");
    b.disabled = true;
    $("clipPageLabel").textContent = "Clip to sources";
  } else if (state.kind === "video") {
    $("clipPageLabel").textContent = "Clip transcript";
  }

  if (state.clippable) readPageMeta(tab.id);
}

function renderFavicon(src) {
  const el = $("favicon");
  if (src && /^https?:|^data:/.test(src)) {
    const img = document.createElement("img");
    img.src = src;
    img.onerror = () => { el.textContent = "◆"; };
    el.textContent = "";
    el.appendChild(img);
  } else {
    el.textContent = state.kind === "video" ? "▶" : state.kind === "local" ? "⧉" : "◆";
  }
}

function renderDetection() {
  const labels = { article: "Article", video: "Video", local: "Local file" };
  $("kind").textContent = labels[state.kind];
}

// --- one-shot page read (activeTab grant): meta keywords + body size -------
async function readPageMeta(tabId) {
  if (!tabId || !chrome.scripting) return;
  try {
    const [res] = await chrome.scripting.executeScript({ target: { tabId }, func: extractMeta });
    const meta = res?.result;
    if (!meta) return;
    if (typeof meta.textLen === "number" && meta.textLen > 0) showSize(meta.textLen);
    seedTags(meta.keywords || []);
  } catch (_) {
    // page disallows injection (e.g. the web store, a PDF) — degrade silently.
  }
}

// Runs in the page. Pulls keyword-ish meta tags and a rough text length.
function extractMeta() {
  const kw = [];
  for (const m of document.querySelectorAll("meta")) {
    const k = (m.getAttribute("property") || m.getAttribute("name") || "").toLowerCase();
    const c = (m.getAttribute("content") || "").trim();
    if (!c) continue;
    if (k === "keywords") kw.push(...c.split(","));
    else if (k === "article:tag" || k === "og:tag" || k === "article:section") kw.push(c);
  }
  const text = document.body ? document.body.innerText : "";
  return { keywords: kw, textLen: text.length };
}

function showSize(chars) {
  // ~4 chars per token is the usual rough rule of thumb.
  const tokens = Math.round(chars / 4);
  const label = tokens >= 1000 ? "~" + (tokens / 1000).toFixed(tokens >= 10000 ? 0 : 1) + "k tokens"
                               : "~" + tokens + " tokens";
  $("size").textContent = label;
  $("size").classList.remove("hidden");
  $("sizeDot").classList.remove("hidden");
}

function slugTag(s) {
  return s.toLowerCase().trim()
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 24);
}

function seedTags(raw) {
  const seen = new Set();
  for (const r of raw) {
    const t = slugTag(r);
    if (t && !seen.has(t)) seen.add(t);
    if (seen.size >= 3) break;
  }
  if (!seen.size) return;
  const tagsEl = $("tags");
  let i = 0;
  for (const name of seen) {
    state.tags.set(name, i < 2);   // first two pre-selected, like the design
    const chip = document.createElement("span");
    chip.className = "chip" + (i < 2 ? " on" : "");
    chip.textContent = "#" + name;
    chip.addEventListener("click", () => {
      const next = !state.tags.get(name);
      state.tags.set(name, next);
      chip.classList.toggle("on", next);
    });
    tagsEl.appendChild(chip);
    i++;
  }
  $("tagsWrap").classList.remove("hidden");
}

function selectedTags() {
  return [...state.tags.entries()].filter(([, on]) => on).map(([n]) => n);
}

// --- status / errors -------------------------------------------------------
function setStatus(msg, cls) {
  const s = $("status");
  s.textContent = msg || "";
  s.className = "status" + (cls ? " " + cls : "");
}

// --- POST to the helper ----------------------------------------------------
async function post(payload, mode) {
  setStatus("Clipping…");
  $("clipPage").disabled = true;
  $("clipNote").disabled = true;
  try {
    const r = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    if (data.ok) {
      showDone(mode, data.message);
    } else {
      setStatus("✗ " + (data.message || "clip failed"), "err");
      reenable();
    }
  } catch (e) {
    setStatus("✗ Can’t reach the clip helper on :8766. Is it running?", "err");
    reenable();
  }
}

function reenable() {
  $("clipNote").disabled = false;
  if (state.kind !== "local") $("clipPage").disabled = false;
}

function showDone(mode, message) {
  // message is the backend's "wrote sources/<id>.md" line; show just the path.
  const path = (message || "").replace(/^wrote\s+/, "").trim() || "sources/…";
  $("savedPath").textContent = path;
  if (mode === "note") {
    $("doneTitle").textContent = "Note saved";
    $("doneSub").textContent = "Standalone note added — it’ll surface in your next /sync.";
  } else {
    $("doneTitle").textContent = state.kind === "video" ? "Transcript clipped" : "Clipped to sources";
    $("doneSub").textContent = "Queued for review. The wiki folds it in on the nightly /sync.";
  }
  $("form").classList.add("hidden");
  $("done").classList.remove("hidden");
}

// --- actions ---------------------------------------------------------------
function clipPage() {
  if (state.kind === "local") return;
  const note = $("note").value.trim();
  const tags = selectedTags();
  // A page/transcript clip: backend fetches the URL and extracts it; the note + tags
  // ride above the extracted body (server passes them as --note).
  const payload = { url: state.url };
  if (note) payload.note = note;
  if (tags.length) payload.tags = tags;
  post(payload, "page");
}

function clipNote() {
  const note = $("note").value.trim();
  if (!note) return setStatus("Type a note first.", "err");
  const tags = selectedTags();
  // A standalone note: the text IS the source body; the url is attached for reference.
  const payload = { text: note, url: state.url };
  if (tags.length) payload.tags = tags;
  post(payload, "note");
}

$("clipPage").addEventListener("click", clipPage);
$("clipNote").addEventListener("click", clipNote);
$("clipAnother").addEventListener("click", () => {
  $("note").value = "";
  setStatus("");
  reenable();
  $("done").classList.add("hidden");
  $("form").classList.remove("hidden");
  $("note").focus();
});

// ⌘S / Ctrl+S clips the page while the popup is focused.
window.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") {
    e.preventDefault();
    if (!$("done").classList.contains("hidden")) return;
    if (state.kind !== "local") clipPage();
  }
});

loadTab();
