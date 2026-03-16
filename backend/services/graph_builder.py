from models.responses import GraphData, GraphEdge, GraphNode, Paper


def build_graph(seed: Paper, related: list[Paper], *, seed_is_source: bool) -> GraphData:
    """
    seed_is_source=True  → edges: seed → related  (references: seed cites them)
    seed_is_source=False → edges: related → seed  (citations: they cite the seed)
    """
    nodes = [GraphNode(id=seed.paperId, data=seed)]
    edges = []
    for paper in related:
        nodes.append(GraphNode(id=paper.paperId, data=paper))
        src, tgt = (seed.paperId, paper.paperId) if seed_is_source else (paper.paperId, seed.paperId)
        edges.append(GraphEdge(id=f"{src}-{tgt}", source=src, target=tgt))
    return GraphData(nodes=nodes, edges=edges, seedPaperId=seed.paperId)
