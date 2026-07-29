import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Lock } from "lucide-react";
import { fetchSource } from "../../lib/api";

export function SourceViewerPage() {
  const { id = "" } = useParams();
  const { data, isLoading, error } = useQuery({
    queryKey: ["source", id],
    queryFn: () => fetchSource(id),
    retry: false,
  });

  if (isLoading) return <div className="p-8 text-[var(--ink-dim)]">Loading source…</div>;

  if (error || !data) {
    return (
      <div className="mx-auto w-full max-w-[720px] p-8">
        <h2 className="text-lg font-semibold text-[var(--drop-ink)]">Source not found</h2>
        <p className="meta mt-2 break-all">{id}</p>
        <Link to="/wiki" className="btn mt-5">
          Back to the map
        </Link>
      </div>
    );
  }

  return (
    <article className="mx-auto w-full max-w-[860px]" style={{ padding: "var(--card-pad)" }}>
      <header className="mb-5 border-b border-[var(--border-soft)] pb-4">
        <span className="pill mb-3">
          <Lock className="h-3 w-3" aria-hidden="true" />
          immutable source
        </span>
        <h2 className="font-mono text-[15px] font-semibold break-all text-[var(--ink-bright)]">
          {data.filename}
        </h2>
        <p className="meta mt-1.5 break-all">{data.id}</p>
      </header>

      <pre className="scroll surface overflow-x-auto p-4 font-mono text-[12px] leading-relaxed whitespace-pre-wrap text-[var(--recap-ink)]">
        {data.raw}
      </pre>

      {data.citers.length ? (
        <section className="mt-7 border-t border-[var(--border-soft)] pt-5">
          <h3 className="label mb-2.5">Cited by</h3>
          <ul className="grid gap-1.5 sm:grid-cols-2">
            {data.citers.map((c) => (
              <li key={c.slug}>
                <Link
                  to={`/wiki/${c.slug}`}
                  className="block truncate text-[13px] text-[var(--ink-muted)] hover:text-[var(--ac)] hover:underline"
                >
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
