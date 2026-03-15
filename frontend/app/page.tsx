"use client";

import Image from "next/image";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { ResolveResponse } from "@/types/paper";

const EXAMPLES = [
  { label: "Attention Is All You Need", doi: "10.48550/arXiv.1706.03762" },
  { label: "BERT", doi: "10.48550/arXiv.1810.04805" },
  { label: "GPT-3", doi: "10.48550/arXiv.2005.14165" },
];

export default function Home() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function resolve(urlOrDoi: string) {
    if (!urlOrDoi.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/resolve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urlOrDoi: urlOrDoi.trim() }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      const { paperId }: ResolveResponse = await res.json();
      router.push(`/graph/${paperId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    resolve(input);
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="w-full max-w-2xl flex flex-col items-center gap-8">
        {/* Logo / Title */}
        <div className="flex flex-col items-center gap-4 text-center">
          <Image
            src="/assets/logo.png"
            alt="connect.ai logo"
            width={160}
            height={160}
            priority
          />
          <div className="flex flex-col items-center gap-2">
            <h1 className="text-5xl font-bold tracking-tight text-foreground">
              connect<span className="text-muted-foreground">.ai</span>
            </h1>
            <p className="text-muted-foreground text-lg">
              Explore research paper citation graphs, powered by AI
            </p>
          </div>
        </div>

        {/* URL / DOI Input */}
        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-3">
          <div className="flex w-full gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Paste a paper URL or DOI (e.g. https://arxiv.org/abs/1706.03762)"
              disabled={loading}
              className="flex-1 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-lg bg-primary text-primary-foreground px-5 py-3 text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Resolving…" : "Explore"}
            </button>
          </div>
          {error && (
            <p className="text-xs text-destructive text-center">{error}</p>
          )}
          {!error && (
            <p className="text-xs text-muted-foreground text-center">
              Supports arXiv, DOI, and direct paper URLs
            </p>
          )}
        </form>

        {/* Example seeds */}
        <div className="flex flex-col items-center gap-3 w-full">
          <p className="text-xs text-muted-foreground uppercase tracking-widest">
            Try an example
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {EXAMPLES.map((paper) => (
              <button
                key={paper.doi}
                onClick={() => resolve(paper.doi)}
                disabled={loading}
                className="rounded-full border border-border bg-card px-4 py-1.5 text-xs text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {paper.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
