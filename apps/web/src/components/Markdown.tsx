import { Link } from "react-router-dom";
import { useMemo, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchWikiPages } from "../lib/api";
import { cn } from "../lib/utils";

/**
 * Small markdown renderer tuned for what the brain actually writes: headings,
 * lists, blockquotes, fenced code, pipe tables, wikilinks and source citations.
 * Host titles are <h2>, so `#` starts at <h3> to keep the outline sane.
 *
 * Used for both wiki bodies (blank-line separated, hard-wrapped) and clipped
 * article bodies from the feeder (no blank lines, one paragraph per line) —
 * see `parseBlocks` for how the two are told apart.
 */
export function Markdown({
  body,
  title,
  linkPages = true,
  className,
}: {
  body: string;
  /** a leading heading repeating this is dropped as a duplicate */
  title?: string;
  /** resolve [[slug]] to the page's title — off outside the wiki */
  linkPages?: boolean;
  className?: string;
}) {
  // page titles let [[entities/andrej-karpathy]] render as "Andrej Karpathy"
  const { data: nav } = useQuery({
    queryKey: ["wikiPages"],
    queryFn: fetchWikiPages,
    enabled: linkPages,
  });
  const titles = useMemo(
    () => new Map((nav?.entries ?? []).map((e) => [e.slug, e.title])),
    [nav?.entries],
  );

  const { blocks, cites } = useMemo(() => {
    const parsed = parseBlocks(body);
    // clipped bodies open with the publication and the article title again
    while (
      title &&
      parsed[0]?.kind === "heading" &&
      norm(parsed[0].text) === norm(title)
    ) {
      parsed.shift();
    }
    return { blocks: parsed, cites: citationOrder(body) };
  }, [body, title]);

  return (
    <div
      className={cn(
        "flex flex-col text-[14.5px] leading-[1.75] text-[var(--recap-ink)]",
        className,
      )}
    >
      {blocks.map((block, i) => renderBlock(block, i, { cites, titles }))}
    </div>
  );
}

const norm = (s: string) => s.trim().toLowerCase().replace(/\s+/g, " ");

/** Source ids in order of first appearance, so citations can render as [1], [2]… */
export function citationOrder(body: string): Map<string, number> {
  const order = new Map<string, number>();
  for (const m of body.matchAll(/\[(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\]/g)) {
    if (!order.has(m[1])) order.set(m[1], order.size + 1);
  }
  return order;
}

type Block =
  | { kind: "heading"; level: number; text: string }
  | { kind: "para"; text: string }
  | { kind: "quote"; lines: string[] }
  | { kind: "ul"; items: string[] }
  | { kind: "ol"; items: string[] }
  | { kind: "code"; text: string }
  | { kind: "table"; head: string[]; rows: string[][] }
  | { kind: "hr" };

const HEADING = /^(#{1,6})\s+(.*)$/;
const UL = /^[-*]\s+(.*)$/;
const OL = /^\d+[.)]\s+(.*)$/;
const QUOTE = /^>\s?(.*)$/;
const TABLE_ROW = /^\|(.+)\|\s*$/;
const TABLE_SEP = /^\|[\s:|-]+\|\s*$/;

function parseBlocks(body: string): Block[] {
  const lines = body.replace(/\r\n/g, "\n").split("\n");
  const blocks: Block[] = [];
  let para: string[] = [];

  // Wiki bodies separate paragraphs with a blank line and hard-wrap within one,
  // so consecutive lines are joined. Clipped article bodies have no blank lines
  // at all — there, every line is its own paragraph and joining them produces
  // one unreadable wall of text.
  const lineIsParagraph = !/\n[ \t]*\n/.test(body) && lines.length > 3;

  const flush = () => {
    if (para.length) {
      blocks.push({ kind: "para", text: para.join(" ").trim() });
      para = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("```")) {
      flush();
      const buf: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```"))
        buf.push(lines[i++]);
      blocks.push({ kind: "code", text: buf.join("\n") });
      continue;
    }

    if (!line.trim()) {
      flush();
      continue;
    }

    if (/^(---|\*\*\*|___)\s*$/.test(line)) {
      flush();
      blocks.push({ kind: "hr" });
      continue;
    }

    const heading = HEADING.exec(line);
    if (heading) {
      flush();
      blocks.push({
        kind: "heading",
        level: heading[1].length,
        // clipped headings arrive as "## Summary**" — drop the dangling marker
        text: heading[2].replace(/^[\s*_]+/, "").replace(/[\s*_]+$/, ""),
      });
      continue;
    }

    if (TABLE_ROW.test(line) && TABLE_SEP.test(lines[i + 1] ?? "")) {
      flush();
      const cells = (l: string) =>
        l
          .replace(/^\||\|\s*$/g, "")
          .split("|")
          .map((c) => c.trim());
      const head = cells(line);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && TABLE_ROW.test(lines[i]))
        rows.push(cells(lines[i++]));
      i--;
      blocks.push({ kind: "table", head, rows });
      continue;
    }

    if (QUOTE.test(line)) {
      flush();
      const buf: string[] = [];
      while (i < lines.length && QUOTE.test(lines[i]))
        buf.push(QUOTE.exec(lines[i++])![1]);
      i--;
      blocks.push({ kind: "quote", lines: buf });
      continue;
    }

    if (UL.test(line)) {
      flush();
      const items: string[] = [];
      while (i < lines.length && UL.test(lines[i]))
        items.push(UL.exec(lines[i++])![1]);
      i--;
      blocks.push({ kind: "ul", items });
      continue;
    }

    if (OL.test(line)) {
      flush();
      const items: string[] = [];
      while (i < lines.length && OL.test(lines[i]))
        items.push(OL.exec(lines[i++])![1]);
      i--;
      blocks.push({ kind: "ol", items });
      continue;
    }

    para.push(line.trim());
    if (lineIsParagraph) flush();
  }

  flush();
  return blocks;
}

type Ctx = { cites: Map<string, number>; titles: Map<string, string> };

function renderBlock(block: Block, key: number, ctx: Ctx): ReactNode {
  switch (block.kind) {
    case "heading": {
      if (block.level === 1) {
        return (
          <h3
            key={key}
            className="mt-7 mb-2 text-[17px] font-semibold tracking-tight text-[var(--ink-bright)] first:mt-0"
          >
            {renderInline(block.text, ctx)}
          </h3>
        );
      }
      if (block.level === 2) {
        return (
          <h4
            key={key}
            className="mt-6 mb-1.5 text-[15px] font-semibold text-[var(--ink)] first:mt-0"
          >
            {renderInline(block.text, ctx)}
          </h4>
        );
      }
      return (
        <h5 key={key} className="label mt-5 mb-1.5 text-[11px] first:mt-0">
          {renderInline(block.text, ctx)}
        </h5>
      );
    }
    case "para":
      return (
        <p key={key} className="my-2 text-pretty">
          {renderInline(block.text, ctx)}
        </p>
      );
    case "quote":
      return (
        <blockquote
          key={key}
          className="my-3 border-l-2 border-[rgba(var(--ac-rgb),0.5)] bg-[var(--sunk)] py-2.5 pr-3 pl-4 text-[var(--ink-muted)] italic"
        >
          {block.lines.map((l, i) => (
            <p key={i} className={i ? "mt-1.5" : ""}>
              {renderInline(l, ctx)}
            </p>
          ))}
        </blockquote>
      );
    case "ul":
      return (
        <ul
          key={key}
          className="my-2 flex list-disc flex-col gap-1 pl-5 marker:text-[var(--ink-fainter)]"
        >
          {block.items.map((it, i) => (
            <li key={i}>{renderInline(it, ctx)}</li>
          ))}
        </ul>
      );
    case "ol":
      return (
        <ol
          key={key}
          className="my-2 flex list-decimal flex-col gap-1 pl-5 marker:font-mono marker:text-[var(--ink-fainter)]"
        >
          {block.items.map((it, i) => (
            <li key={i}>{renderInline(it, ctx)}</li>
          ))}
        </ol>
      );
    case "code":
      return (
        <pre
          key={key}
          className="scroll surface my-3 overflow-x-auto p-3.5 font-mono text-[12px] leading-relaxed text-[var(--ink-muted)]"
        >
          {block.text}
        </pre>
      );
    case "table":
      return (
        <div key={key} className="scroll surface my-4 overflow-x-auto">
          <table className="w-full border-collapse text-[12.5px]">
            <thead>
              <tr className="border-b border-[var(--border)]">
                {block.head.map((h, i) => (
                  <th
                    key={i}
                    scope="col"
                    className="px-3 py-2 text-left font-semibold text-[var(--ink)]"
                  >
                    {renderInline(h, ctx)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, i) => (
                <tr key={i} className="border-t border-[var(--border-soft)]">
                  {row.map((c, j) => (
                    <td
                      key={j}
                      className="px-3 py-2 align-top text-[var(--ink-dim)]"
                    >
                      {renderInline(c, ctx)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    case "hr":
      return (
        <hr
          key={key}
          className="my-6 border-0 border-t border-[var(--border)]"
        />
      );
  }
}

// code | bold | italic | md-link | wikilink | source citation
const INLINE =
  /`([^`]+)`|\*\*([^*]+)\*\*|\*([^*\n]+)\*|_([^_\n]+)_|\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)|\[\[([^\]]+)\]\]|\[(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\]/g;

function renderInline(text: string, ctx: Ctx): ReactNode[] {
  const parts: ReactNode[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  INLINE.lastIndex = 0;

  while ((m = INLINE.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    const k = m.index;

    if (m[1] !== undefined) {
      parts.push(
        <code
          key={`${k}-c`}
          className="rounded bg-[var(--node)] px-1.5 py-0.5 font-mono text-[0.87em] text-[var(--ink)]"
        >
          {m[1]}
        </code>,
      );
    } else if (m[2] !== undefined) {
      parts.push(
        <strong
          key={`${k}-b`}
          className="font-semibold text-[var(--ink-bright)]"
        >
          {m[2]}
        </strong>,
      );
    } else if (m[3] !== undefined || m[4] !== undefined) {
      parts.push(<em key={`${k}-i`}>{m[3] ?? m[4]}</em>);
    } else if (m[5] !== undefined) {
      parts.push(
        <a
          key={`${k}-a`}
          href={m[6]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[var(--ac)] underline decoration-[rgba(var(--ac-rgb),0.4)] underline-offset-2 hover:decoration-[var(--ac)]"
        >
          {m[5]}
        </a>,
      );
    } else if (m[7] !== undefined) {
      // [[slug]] or [[slug|label]] — fall back to the page title, then the slug
      const [target, alias] = m[7].split("|");
      const slug = target.trim().replace(/^\//, "");
      const label = alias?.trim() || ctx.titles.get(slug);
      parts.push(
        <Link
          key={`${k}-wl`}
          to={`/wiki/${slug}`}
          title={slug}
          className={cn(
            "text-[var(--ac)] decoration-[rgba(var(--ac-rgb),0.4)] underline-offset-2 hover:underline",
            !label && "font-mono text-[0.92em]",
          )}
        >
          {label || slug}
        </Link>,
      );
    } else if (m[8] !== undefined) {
      const n = ctx.cites.get(m[8]);
      parts.push(
        <Link
          key={`${k}-cite`}
          to={`/wiki/source/${m[8]}`}
          title={m[8]}
          className="ml-0.5 align-super font-mono text-[0.7em] font-semibold text-[var(--ink-faint)] hover:text-[var(--ac)]"
        >
          [{n ?? m[8]}]
        </Link>,
      );
    }
    last = m.index + m[0].length;
  }

  if (last < text.length) parts.push(text.slice(last));
  return parts;
}
