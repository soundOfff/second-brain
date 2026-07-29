import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { FileText, Link2 } from "lucide-react";
import { fetchWikiPage } from "../../lib/api";
import { Markdown, citationOrder } from "../../components/Markdown";
import { cn } from "../../lib/utils";

export function WikiPageView() {
  const params = useParams();
  const slug = (params["*"] ?? params.slug ?? "index").replace(/^\//, "");
  const { data, isLoading, error } = useQuery({
    queryKey: ["wikiPage", slug],
    queryFn: () => fetchWikiPage(slug),
    retry: false,
  });

  if (isLoading) return <div className="p-8 text-[var(--ink-dim)]">Loading…</div>;

  if (error || !data) {
    return (
      <div className="mx-auto w-full max-w-[720px] p-8">
        <h2 className="text-lg font-semibold text-[var(--ink)]">Page not found</h2>
        <p className="meta mt-2">{slug}</p>
        <Link to="/wiki" className="btn mt-5">
          Back to the map
        </Link>
      </div>
    );
  }

  const { meta } = data;
  const cites = citationOrder(data.body);

  return (
    <article className="mx-auto w-full max-w-[780px]" style={{ padding: "var(--card-pad)" }}>
      <header className="mb-7 border-b border-[var(--border-soft)] pb-5">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          {meta.type ? <span className="pill uppercase">{meta.type}</span> : null}
          {meta.status ? (
            <span className={cn("pill", meta.status !== "stub" && "pill-accent")}>{meta.status}</span>
          ) : null}
          {meta.updated ? <span className="meta">updated {meta.updated}</span> : null}
        </div>
        <h2
          className="text-balance leading-tight font-bold tracking-tight text-[var(--ink-bright)]"
          style={{ fontSize: "calc(var(--title-size) * 1.1)" }}
        >
          {meta.title ?? slug}
        </h2>
        {meta.tags?.length ? (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {meta.tags.map((t) => (
              <span key={t} className="meta rounded bg-[var(--node)] px-1.5 py-0.5">
                #{t}
              </span>
            ))}
          </div>
        ) : null}
      </header>

      <Markdown body={data.body} title={meta.title ?? slug} />

      {data.sources.length || data.backlinks.length ? (
        <div className="mt-10 grid gap-5 border-t border-[var(--border-soft)] pt-6 sm:grid-cols-2">
          {data.sources.length ? (
            <section>
              <h3 className="label mb-2.5">Sources</h3>
              <ul className="flex flex-col gap-1.5">
                {data.sources.map((s) => (
                  <li key={s.id}>
                    <Link
                      to={`/wiki/source/${s.id}`}
                      className="flex items-baseline gap-2 font-mono text-[11.5px] break-all text-[var(--ink-muted)] hover:text-[var(--ac)] hover:underline"
                    >
                      {cites.has(s.id) ? (
                        <span className="tnum shrink-0 font-semibold text-[var(--ac)]">
                          [{cites.get(s.id)}]
                        </span>
                      ) : (
                        <FileText
                          className="h-3.5 w-3.5 shrink-0 self-center text-[var(--ink-fainter)]"
                          aria-hidden="true"
                        />
                      )}
                      {s.id}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          {data.backlinks.length ? (
            <section>
              <h3 className="label mb-2.5">Backlinks</h3>
              <ul className="flex flex-col gap-1.5">
                {data.backlinks.map((b) => (
                  <li key={b.slug}>
                    <Link
                      to={`/wiki/${b.slug}`}
                      className="flex items-center gap-2 text-[13px] text-[var(--ink-muted)] hover:text-[var(--ac)]"
                    >
                      <Link2 className="h-3.5 w-3.5 shrink-0 text-[var(--ink-fainter)]" aria-hidden="true" />
                      <span className="truncate">{b.title}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}
