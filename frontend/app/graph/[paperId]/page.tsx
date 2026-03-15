import type { Paper } from "@/types/paper";
import Link from "next/link";

async function fetchPaper(paperId: string): Promise<Paper> {
  const res = await fetch(`http://localhost:8000/api/v1/paper/${paperId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch paper: ${res.status}`);
  }
  return res.json();
}

export default async function GraphPage({
  params,
}: {
  params: { paperId: string };
}) {
  let paper: Paper;
  try {
    paper = await fetchPaper(params.paperId);
  } catch {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="text-center">
          <p className="text-destructive text-lg font-medium">Paper not found.</p>
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground mt-2 inline-block">
            ← Back to search
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background px-6 py-10">
      <div className="mx-auto max-w-3xl flex flex-col gap-8">

        {/* Back link */}
        <Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
          ← Back to search
        </Link>

        {/* Paper header */}
        <div className="flex flex-col gap-3">
          <h1 className="text-3xl font-bold text-foreground leading-tight">
            {paper.title}
          </h1>
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            {paper.year && (
              <span className="rounded-full border border-border px-3 py-0.5">
                {paper.year}
              </span>
            )}
            {paper.citationCount != null && (
              <span className="rounded-full border border-border px-3 py-0.5">
                {paper.citationCount.toLocaleString()} citations
              </span>
            )}
            {paper.url && (
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground underline underline-offset-2 transition-colors"
              >
                View paper ↗
              </a>
            )}
          </div>
        </div>

        {/* Authors */}
        {paper.authors.length > 0 && (
          <div className="flex flex-col gap-1">
            <h2 className="text-xs uppercase tracking-widest text-muted-foreground">Authors</h2>
            <p className="text-foreground text-sm">
              {paper.authors.map((a) => a.name).join(", ")}
            </p>
          </div>
        )}

        {/* Abstract */}
        {paper.abstract && (
          <div className="flex flex-col gap-2">
            <h2 className="text-xs uppercase tracking-widest text-muted-foreground">Abstract</h2>
            <p className="text-foreground text-sm leading-relaxed">{paper.abstract}</p>
          </div>
        )}

        {/* Phase 2 placeholder */}
        <div className="rounded-xl border border-border bg-card px-6 py-10 flex flex-col items-center gap-2 text-center">
          <p className="text-muted-foreground font-medium">Graph visualization coming in Phase 2</p>
          <p className="text-xs text-muted-foreground">
            Citation graph for <span className="text-foreground">{paper.title}</span> will appear here.
          </p>
        </div>

      </div>
    </main>
  );
}
