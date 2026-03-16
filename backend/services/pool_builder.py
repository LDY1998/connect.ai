import asyncio

from models.responses import GraphData, GraphEdge, GraphNode, Paper
from services.paper_provider import PaperProvider
from services.similarity import bibliographic_coupling, co_citation_score


async def _safe(coro) -> set[str]:
    """Run a coroutine; return empty set on any exception."""
    try:
        return await coro
    except Exception:
        return set()


def _assign_pool(combined: float) -> str:
    if combined >= 0.15:
        return "core"
    if combined >= 0.05:
        return "related"
    return "peripheral"


async def build_pools_graph(
    seed: Paper,
    citations: list[Paper],
    references: list[Paper],
    provider: PaperProvider,
) -> GraphData:
    # 1. Deduplicate candidates (exclude seed itself)
    candidates: dict[str, Paper] = {}
    for paper in citations + references:
        if paper.paperId != seed.paperId:
            candidates[paper.paperId] = paper

    candidate_ids = list(candidates.keys())

    # 2. Fetch ID sets in parallel
    tasks = [
        _safe(provider.get_reference_ids(seed.paperId)),
        _safe(provider.get_citation_ids(seed.paperId)),
        *[_safe(provider.get_reference_ids(pid)) for pid in candidate_ids],
        *[_safe(provider.get_citation_ids(pid)) for pid in candidate_ids],
    ]
    results = await asyncio.gather(*tasks)

    n = len(candidate_ids)
    seed_ref_ids: set[str] = results[0]
    seed_citer_ids: set[str] = results[1]
    candidate_ref_ids: list[set[str]] = list(results[2 : 2 + n])
    candidate_citer_ids: list[set[str]] = list(results[2 + n :])

    # 3. Score each candidate
    scores: list[float] = []
    for i in range(n):
        bc = bibliographic_coupling(seed_ref_ids, candidate_ref_ids[i])
        cc = co_citation_score(seed_citer_ids, candidate_citer_ids[i])
        scores.append(0.5 * bc + 0.5 * cc)

    # 4. Assign pools (with fallback when all scores are zero)
    all_zero = all(s == 0.0 for s in scores)
    if all_zero and candidate_ids:
        # Rank by citationCount; top tertile → "related", rest → "peripheral"
        indexed = sorted(
            range(n),
            key=lambda i: candidates[candidate_ids[i]].citationCount or 0,
            reverse=True,
        )
        cutoff = max(1, n // 3)
        pool_map = {
            candidate_ids[idx]: ("related" if rank < cutoff else "peripheral")
            for rank, idx in enumerate(indexed)
        }
    else:
        pool_map = {
            candidate_ids[i]: _assign_pool(scores[i]) for i in range(n)
        }

    # 5. Build GraphData
    nodes: list[GraphNode] = [GraphNode(id=seed.paperId, data=seed, pool=None)]
    for pid, paper in candidates.items():
        nodes.append(GraphNode(id=pid, data=paper, pool=pool_map[pid]))

    # Edges: citation → seed is (paper → seed), reference is (seed → paper)
    # Track already-added edges to deduplicate papers in both sets
    citation_set = {p.paperId for p in citations}
    reference_set = {p.paperId for p in references}

    edges: list[GraphEdge] = []
    seen_edges: set[tuple[str, str]] = set()

    for paper in citations:
        if paper.paperId == seed.paperId:
            continue
        key = (paper.paperId, seed.paperId)
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append(
                GraphEdge(
                    id=f"{paper.paperId}->{seed.paperId}",
                    source=paper.paperId,
                    target=seed.paperId,
                )
            )

    for paper in references:
        if paper.paperId == seed.paperId:
            continue
        key = (seed.paperId, paper.paperId)
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append(
                GraphEdge(
                    id=f"{seed.paperId}->{paper.paperId}",
                    source=seed.paperId,
                    target=paper.paperId,
                )
            )

    return GraphData(nodes=nodes, edges=edges, seedPaperId=seed.paperId)
