import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { fetchWikiPage } from "../../lib/api";
import { WikiMarkdown } from "./WikiMarkdown";

export function WikiPageView() {
  const params = useParams();
  const slug = (params["*"] ?? params.slug ?? "index").replace(/^\//, "");
  const { data, isLoading, error } = useQuery({
    queryKey: ["wikiPage", slug],
    queryFn: () => fetchWikiPage(slug),
    retry: false,
  });

  if (isLoading) return <div className="p-6 text-[var(--ink-dim)]">Loading…</div>;
  if (error || !data) {
    return (
      <div className="p-6">
        <h1 className="text-lg font-semibold text-[var(--ink)]">Page not found</h1>
        <p className="mt-2 text-[var(--ink-dim)]">{slug}</p>
      </div>
    );
  }

  return (
    <article className="p-6" style={{ padding: "var(--card-pad)" }}>
      <header className="mb-5 border-b border-[var(--border-soft)] pb-4">
        <div className="mb-2 flex flex-wrap gap-2">
          {data.meta.type ? (
            <span className="rounded border border-[var(--border)] px-2 py-0.5 font-mono text-[10px] uppercase text-[var(--ink-faint)]">
              {data.meta.type}
            </span>
          ) : null}
          {data.meta.status ? (
            <span className="rounded border border-[var(--border)] px-2 py-0.5 font-mono text-[10px] text-[var(--ac)]">
              {data.meta.status}
            </span>
          ) : null}
        </div>
        <h1 className="font-bold text-[var(--ink-bright)]" style={{ fontSize: "var(--title-size)" }}>
          {data.meta.title ?? slug}
        </h1>
        {data.meta.updated ? (
          <p className="mt-1 font-mono text-[10px] text-[var(--ink-faint)]">updated {data.meta.updated}</p>
        ) : null}
      </header>

      <WikiMarkdown body={data.body} />

      {data.sources.length ? (
        <section className="mt-8">
          <h2 className="mb-2 font-mono text-[10px] font-bold uppercase tracking-widest text-[var(--ink-faint)]">Sources</h2>
          <ul className="flex flex-col gap-1">
            {data.sources.map((s) => (
              <li key={s.id}>
                <Link
                  to={`/wiki/source/${s.id}`}
                  className="font-mono text-[12px] text-[var(--ac)] hover:underline"
                >
                  {s.id}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {data.backlinks.length ? (
        <section className="mt-6">
          <h2 className="mb-2 font-mono text-[10px] font-bold uppercase tracking-widest text-[var(--ink-faint)]">Backlinks</h2>
          <ul className="flex flex-col gap-1">
            {data.backlinks.map((b) => (
              <li key={b.slug}>
                <Link to={`/wiki/${b.slug}`} className="text-[13px] text-[var(--ink-muted)] hover:text-[var(--ac)]">
                  {b.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </article>
  );
}
