// Clip to Brain — popup logic. POSTs to the localhost helper (brain-clip-server.py),
// which shells out to bin/brain-clip.sh. The helper must be running (launchd agent
// com.secondbrain.clipserver, installed by bin/brain-clip-gui.sh browser).
const ENDPOINT = "http://127.0.0.1:8766/clip";

const $ = (id) => document.getElementById(id);
let current = { url: "", title: "" };

async function loadTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  current.url = tab?.url || "";
  current.title = tab?.title || "";
  $("title").textContent = current.title || "(untitled tab)";
  $("url").textContent = current.url;
  const clippable = /^https?:\/\//.test(current.url);
  $("clipPage").disabled = !clippable;
  if (!clippable) setStatus("This tab isn't a web page — use “Clip note only”.", "err");
}

function setStatus(msg, cls) {
  const s = $("status");
  s.textContent = msg;
  s.className = cls || "";
}

async function post(payload) {
  setStatus("Clipping…");
  try {
    const r = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    if (data.ok) {
      setStatus("✓ " + data.message, "ok");
      setTimeout(() => window.close(), 1200);
    } else {
      setStatus("✗ " + (data.message || "clip failed"), "err");
    }
  } catch (e) {
    setStatus("✗ Can't reach the clip helper on :8766. Is it running?", "err");
  }
}

$("clipPage").addEventListener("click", () => {
  const note = $("note").value.trim();
  post(note ? { url: current.url, text: note } : { url: current.url, title: current.title });
});

$("clipNote").addEventListener("click", () => {
  const note = $("note").value.trim();
  if (!note) return setStatus("Type a note first.", "err");
  post({ text: note, url: current.url });
});

loadTab();
