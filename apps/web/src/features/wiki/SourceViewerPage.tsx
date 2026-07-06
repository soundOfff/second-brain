import { Link } from "react-router-dom";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { fetchSource } from "../../lib/api";

export function SourceViewerPage() {
  const { id = "" } = useParams();
  const { data, isLoading, error } = useQuery({
    queryKey: ["source", id],
    queryFn: () => fetchSource(id),
    retry: false,
  });

  if (isLoading) return <div className="p-6 text-[var(--ink-dim)]">Loading source…</div>;
  if (error || !data) {
    return <div className="p-6 text-[var(--drop-ink)]">Source not found: {id}</div>;
  }

  return (
    <article className="p-6" style={{ padding: "var(--card-pad)" }}>
      <header className="mb-4 border-b border-[var(--border-soft)] pb-3">
        <h1 className="font-mono text-sm font-semibold text-[var(--ink-bright)]">{data.filename}</h1>
        <p className="mt-1 font-mono text-[10px] text-[var(--ink-faint)]">immutable source · {data.id}</p>
      </header>
      <pre className="whitespace-pre-wrap rounded-lg border border-[var(--border)] bg-[var(--raise)] p-4 font-mono text-[12px] leading-relaxed text-[var(--recap-ink)]">
        {data.raw}
      </pre>
      {data.citers.length ? (
        <section className="mt-6">
          <h2 className="mb-2 font-mono text-[10px] font-bold uppercase tracking-widest text-[var(--ink-faint)]">Cited by</h2>
          <ul className="flex flex-col gap-1">
            {data.citers.map((c) => (
              <li key={c.slug}>
                <Link to={`/wiki/${c.slug}`} className="text-[13px] text-[var(--ac)] hover:underline">
                  {c.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </article>
  );
}
