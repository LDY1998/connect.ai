import math

from models.responses import GraphData, GraphEdge, GraphNode, NodePosition, Paper


_INNER_RADIUS = 300
_OUTER_RADIUS = 600


def build_graph(
    seed: Paper,
    citations: list[Paper],
    references: list[Paper],
) -> GraphData:
    """
    Build a GraphData object with a radial layout.

    The seed paper is placed at (0, 0). Citations and references are
    distributed in concentric rings:
    - If only one group is non-empty, all nodes go on a single ring.
    - If both groups are non-empty, citations go on the inner ring and
      references on the outer ring.
    """
    nodes: list[GraphNode] = [
        GraphNode(
            id=seed.paperId,
            position=NodePosition(x=0.0, y=0.0),
            data=seed,
            type="paper",
        )
    ]
    edges: list[GraphEdge] = []

    has_citations = len(citations) > 0
    has_references = len(references) > 0

    if has_citations and has_references:
        citation_radius = _INNER_RADIUS
        reference_radius = _OUTER_RADIUS
    else:
        citation_radius = _INNER_RADIUS
        reference_radius = _INNER_RADIUS

    for i, paper in enumerate(citations):
        angle = (2 * math.pi * i) / len(citations)
        nodes.append(
            GraphNode(
                id=paper.paperId,
                position=NodePosition(
                    x=citation_radius * math.cos(angle),
                    y=citation_radius * math.sin(angle),
                ),
                data=paper,
                type="paper",
            )
        )
        edges.append(
            GraphEdge(
                id=f"{seed.paperId}-{paper.paperId}",
                source=seed.paperId,
                target=paper.paperId,
                type="citation",
            )
        )

    for i, paper in enumerate(references):
        angle = (2 * math.pi * i) / len(references)
        nodes.append(
            GraphNode(
                id=paper.paperId,
                position=NodePosition(
                    x=reference_radius * math.cos(angle),
                    y=reference_radius * math.sin(angle),
                ),
                data=paper,
                type="paper",
            )
        )
        edges.append(
            GraphEdge(
                id=f"{paper.paperId}-{seed.paperId}",
                source=paper.paperId,
                target=seed.paperId,
                type="citation",
            )
        )

    return GraphData(nodes=nodes, edges=edges, seedPaperId=seed.paperId)
