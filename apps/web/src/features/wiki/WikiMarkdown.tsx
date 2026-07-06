import { Link } from "react-router-dom";
import type { ReactNode } from "react";

const WIKILINK = /\[\[([^\]]+)\]\]/g;
const CITATION = /\[(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\]/g;

/** Minimal markdown-ish renderer: paragraphs + wikilinks + source citations. */
export function WikiMarkdown({ body }: { body: string }) {
  const blocks = body.split(/\n\n+/);

  return (
    <div className="prose-brain max-w-none text-[14px] leading-relaxed text-[var(--recap-ink)]">
      {blocks.map((block, i) => {
        const trimmed = block.trim();
        if (!trimmed) return null;
        if (trimmed.startsWith("# ")) {
          return (
            <h2 key={i} className="mb-2 mt-4 text-lg font-semibold text-[var(--ink-bright)]">
              {renderInline(trimmed.slice(2))}
            </h2>
          );
        }
        if (trimmed.startsWith("## ")) {
          return (
            <h3 key={i} className="mb-2 mt-3 text-base font-semibold text-[var(--ink)]">
              {renderInline(trimmed.slice(3))}
            </h3>
          );
        }
        if (trimmed.startsWith("- ")) {
          const items = trimmed.split("\n").filter((l) => l.startsWith("- "));
          return (
            <ul key={i} className="my-2 list-disc pl-5">
              {items.map((li, j) => (
                <li key={j}>{renderInline(li.slice(2))}</li>
              ))}
            </ul>
          );
        }
        return (
          <p key={i} className="my-2 text-pretty">
            {renderInline(trimmed)}
          </p>
        );
      })}
    </div>
  );
}

function renderInline(text: string): ReactNode[] {
  const parts: React.ReactNode[] = [];
  let last = 0;
  const re = new RegExp(`${WIKILINK.source}|${CITATION.source}`, "g");
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[0].startsWith("[[")) {
      const slug = m[1].replace(/^\//, "");
      parts.push(
        <Link key={`${m.index}-wl`} to={`/wiki/${slug}`} className="font-mono text-[var(--ac)] hover:underline">
          {m[1]}
        </Link>,
      );
    } else {
      const sid = m[1];
      parts.push(
        <Link key={`${m.index}-c`} to={`/wiki/source/${sid}`} className="font-mono text-[12px] text-[var(--ink-faint)] hover:text-[var(--ac)]">
          [{sid}]
        </Link>,
      );
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}
