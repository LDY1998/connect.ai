from abc import ABC, abstractmethod

from models.responses import Author, Paper


class PaperProvider(ABC):
    """Abstract interface that every paper data source must implement."""

    @abstractmethod
    async def resolve(self, url_or_doi: str) -> str:
        """Resolve a URL or DOI to a canonical paper ID used internally."""

    @abstractmethod
    async def get_paper(self, paper_id: str) -> Paper:
        """Fetch full metadata for a paper by its canonical ID."""

    @abstractmethod
    async def get_citations(self, paper_id: str, limit: int = 60) -> list[Paper]:
        """Return up to `limit` papers that cite the given paper."""

    @abstractmethod
    async def get_references(self, paper_id: str, limit: int = 60) -> list[Paper]:
        """Return up to `limit` papers that the given paper references."""

    async def aclose(self) -> None:
        """Optional teardown for providers that hold open connections."""


# ---------------------------------------------------------------------------
# Stub implementation — returns hardcoded data so the rest of the app can be
# built and tested without any external API access.
# ---------------------------------------------------------------------------

_STUB_PAPERS: dict[str, Paper] = {
    "stub-attention-2017": Paper(
        paperId="stub-attention-2017",
        title="Attention Is All You Need",
        year=2017,
        authors=[
            Author(name="Ashish Vaswani"),
            Author(name="Noam Shazeer"),
            Author(name="Niki Parmar"),
        ],
        abstract=(
            "We propose a new simple network architecture, the Transformer, "
            "based solely on attention mechanisms."
        ),
        citationCount=90000,
        externalIds={"ArXiv": "1706.03762"},
        url="https://arxiv.org/abs/1706.03762",
    ),
    "stub-bert-2018": Paper(
        paperId="stub-bert-2018",
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        year=2018,
        authors=[Author(name="Jacob Devlin"), Author(name="Ming-Wei Chang")],
        abstract=(
            "We introduce BERT, which stands for Bidirectional Encoder "
            "Representations from Transformers."
        ),
        citationCount=60000,
        externalIds={"ArXiv": "1810.04805"},
        url="https://arxiv.org/abs/1810.04805",
    ),
    "stub-gpt3-2020": Paper(
        paperId="stub-gpt3-2020",
        title="Language Models are Few-Shot Learners",
        year=2020,
        authors=[Author(name="Tom Brown"), Author(name="Benjamin Mann")],
        abstract=(
            "We show that scaling language models greatly improves task-agnostic, "
            "few-shot performance."
        ),
        citationCount=30000,
        externalIds={"ArXiv": "2005.14165"},
        url="https://arxiv.org/abs/2005.14165",
    ),
}

_STUB_GRAPH: dict[str, list[str]] = {
    "stub-attention-2017": ["stub-bert-2018", "stub-gpt3-2020"],
    "stub-bert-2018": ["stub-gpt3-2020"],
    "stub-gpt3-2020": [],
}

_DOI_TO_ID: dict[str, str] = {
    "1706.03762": "stub-attention-2017",
    "1810.04805": "stub-bert-2018",
    "2005.14165": "stub-gpt3-2020",
}


class StubPaperProvider(PaperProvider):
    """
    Returns hardcoded data. Use this while external API access is unavailable.
    Replace with a real provider (e.g. SemanticScholarProvider) later.
    """

    async def resolve(self, url_or_doi: str) -> str:
        text = url_or_doi.strip().lower()
        for fragment, paper_id in _DOI_TO_ID.items():
            if fragment in text:
                return paper_id
        # Fall back to first stub paper so the UI always has something to show
        return "stub-attention-2017"

    async def get_paper(self, paper_id: str) -> Paper:
        paper = _STUB_PAPERS.get(paper_id)
        if paper is None:
            raise ValueError(f"Stub paper not found: {paper_id!r}")
        return paper

    async def get_citations(self, paper_id: str, limit: int = 60) -> list[Paper]:
        ids = _STUB_GRAPH.get(paper_id, [])
        return [_STUB_PAPERS[i] for i in ids[:limit] if i in _STUB_PAPERS]

    async def get_references(self, paper_id: str, limit: int = 60) -> list[Paper]:
        refs = [
            src for src, targets in _STUB_GRAPH.items() if paper_id in targets
        ]
        return [_STUB_PAPERS[i] for i in refs[:limit] if i in _STUB_PAPERS]
