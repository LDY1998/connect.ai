from abc import ABC, abstractmethod
import re

import httpx

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

    @abstractmethod
    async def get_reference_ids(self, paper_id: str) -> set[str]:
        """IDs of papers this paper references. One API call, no metadata."""

    @abstractmethod
    async def get_citation_ids(self, paper_id: str, limit: int = 100) -> set[str]:
        """IDs of papers that cite this paper. One API call, no metadata."""

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

    async def get_reference_ids(self, paper_id: str) -> set[str]:
        return set(_STUB_GRAPH.get(paper_id, []))

    async def get_citation_ids(self, paper_id: str, limit: int = 100) -> set[str]:
        return {src for src, targets in _STUB_GRAPH.items() if paper_id in targets}


# ---------------------------------------------------------------------------
# OpenAlex implementation — free, no API key required.
# Pass your email to join the "polite pool" (higher rate limits).
# Docs: https://docs.openalex.org
# ---------------------------------------------------------------------------

class OpenAlexProvider(PaperProvider):
    """
    Paper provider backed by the OpenAlex API (https://openalex.org).
    Completely free — no API key required.
    Supply an email to use the polite pool for higher rate limits.
    """

    _BASE_URL = "https://api.openalex.org"
    _WORK_SELECT = (
        "id,doi,title,publication_year,authorships,"
        "abstract_inverted_index,cited_by_count,ids,primary_location"
    )

    def __init__(self, email: str = ""):
        user_agent = f"connect.ai/0.1 (mailto:{email})" if email else "connect.ai/0.1"
        self._client = httpx.AsyncClient(
            base_url=self._BASE_URL,
            headers={"User-Agent": user_agent},
            timeout=30.0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def resolve(self, url_or_doi: str) -> str:
        identifier = self._build_identifier(url_or_doi)
        resp = await self._client.get(f"/works/{identifier}", params={"select": "id"})
        resp.raise_for_status()
        return self._short_id(resp.json()["id"])

    async def get_paper(self, paper_id: str) -> Paper:
        resp = await self._client.get(
            f"/works/{paper_id}", params={"select": self._WORK_SELECT}
        )
        resp.raise_for_status()
        return self._parse_work(resp.json())

    async def get_citations(self, paper_id: str, limit: int = 60) -> list[Paper]:
        """Papers that cite the given work, sorted by citation count descending."""
        resp = await self._client.get(
            "/works",
            params={
                "filter": f"cites:{paper_id}",
                "sort": "cited_by_count:desc",
                "per-page": min(limit, 200),
                "select": self._WORK_SELECT,
            },
        )
        resp.raise_for_status()
        return [self._parse_work(w) for w in resp.json().get("results", [])]

    async def get_reference_ids(self, paper_id: str) -> set[str]:
        """IDs of papers this work references. Single API call, no metadata."""
        resp = await self._client.get(
            f"/works/{paper_id}", params={"select": "referenced_works"}
        )
        resp.raise_for_status()
        return {self._short_id(u) for u in resp.json().get("referenced_works", [])}

    async def get_citation_ids(self, paper_id: str, limit: int = 100) -> set[str]:
        """IDs of papers that cite this work. Single API call, no metadata."""
        resp = await self._client.get(
            "/works",
            params={
                "filter": f"cites:{paper_id}",
                "per-page": min(limit, 200),
                "select": "id",
            },
        )
        resp.raise_for_status()
        return {self._short_id(w["id"]) for w in resp.json().get("results", [])}

    async def get_references(self, paper_id: str, limit: int = 60) -> list[Paper]:
        """Papers referenced by the given work."""
        resp = await self._client.get(
            f"/works/{paper_id}", params={"select": "referenced_works"}
        )
        resp.raise_for_status()
        ref_urls: list[str] = resp.json().get("referenced_works", [])[:limit]

        if not ref_urls:
            return []

        # Batch-fetch metadata using an openalex ID filter (max 50 per call)
        short_ids = [self._short_id(u) for u in ref_urls[:50]]
        filter_str = "|".join(short_ids)
        resp = await self._client.get(
            "/works",
            params={
                "filter": f"openalex:{filter_str}",
                "per-page": len(short_ids),
                "select": self._WORK_SELECT,
            },
        )
        resp.raise_for_status()
        return [self._parse_work(w) for w in resp.json().get("results", [])]

    # ------------------------------------------------------------------
    # Private helpers — OpenAlex-specific, not part of the public interface
    # ------------------------------------------------------------------

    @staticmethod
    def _short_id(openalex_url: str) -> str:
        """Extract short work ID (e.g. 'W2741809807') from a full OpenAlex URL."""
        return openalex_url.rstrip("/").split("/")[-1]

    @staticmethod
    def _build_identifier(url_or_doi: str) -> str:
        """
        Convert an arbitrary URL/DOI string into an identifier that OpenAlex
        accepts directly in the /works/{identifier} path.

        OpenAlex supports two path identifier forms:
          - Short OpenAlex ID: W2741809807
          - Full DOI URL:      https://doi.org/10.xxx/yyy

        arXiv IDs are converted to their DOI (10.48550/arXiv.NNNN.NNNNN).
        """
        text = url_or_doi.strip()

        # Already a short OpenAlex ID
        if re.fullmatch(r"W\d+", text):
            return text

        # Full OpenAlex URL — extract short ID
        if "openalex.org" in text:
            return OpenAlexProvider._short_id(text)

        # arXiv shorthand e.g. "arxiv:1706.03762"
        if text.lower().startswith("arxiv:"):
            arxiv_id = text.split(":", 1)[1].split("v")[0]
            return f"https://doi.org/10.48550/arXiv.{arxiv_id}"

        # Bare arXiv ID e.g. "1706.03762" or "1706.03762v2"
        if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", text):
            arxiv_id = text.split("v")[0]
            return f"https://doi.org/10.48550/arXiv.{arxiv_id}"

        # arXiv URL e.g. "https://arxiv.org/abs/1706.03762"
        if "arxiv.org" in text:
            m = re.search(r"(\d{4}\.\d{4,5})", text)
            if m:
                return f"https://doi.org/10.48550/arXiv.{m.group(1)}"

        # Bare DOI starting with "10."
        if text.startswith("10."):
            return f"https://doi.org/{text}"

        # doi: prefixed
        if text.lower().startswith("doi:"):
            return f"https://doi.org/{text[4:].strip()}"

        # DOI embedded in any URL e.g. "https://doi.org/10.xxx" or redirect URLs
        m = re.search(r"(10\.\d{4,}/\S+)", text)
        if m:
            return f"https://doi.org/{m.group(1).rstrip('.,;)')}"

        return text

    @staticmethod
    def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
        """Rebuild plain text from OpenAlex's inverted-index abstract format."""
        if not inverted_index:
            return None
        pairs: list[tuple[int, str]] = []
        for word, positions in inverted_index.items():
            for pos in positions:
                pairs.append((pos, word))
        pairs.sort()
        return " ".join(w for _, w in pairs)

    def _parse_work(self, data: dict) -> Paper:
        authors = [
            Author(name=a["author"].get("display_name", ""))
            for a in data.get("authorships", [])
            if a.get("author")
        ]

        doi_url: str | None = data.get("doi")
        doi = doi_url.removeprefix("https://doi.org/") if doi_url else None

        url = doi_url
        primary = data.get("primary_location") or {}
        if not url and primary.get("landing_page_url"):
            url = primary["landing_page_url"]

        external_ids: dict[str, str] = {}
        if doi:
            external_ids["DOI"] = doi
        raw_ids = data.get("ids", {})
        if raw_ids.get("arxiv"):
            arxiv = raw_ids["arxiv"].removeprefix("https://arxiv.org/abs/")
            external_ids["ArXiv"] = arxiv
        full_openalex = data.get("id", "")
        if full_openalex:
            external_ids["OpenAlex"] = self._short_id(full_openalex)

        return Paper(
            paperId=self._short_id(full_openalex) if full_openalex else data.get("id", ""),
            title=data.get("title") or "",
            year=data.get("publication_year"),
            authors=authors,
            abstract=self._reconstruct_abstract(data.get("abstract_inverted_index")),
            citationCount=data.get("cited_by_count"),
            externalIds=external_ids or None,
            url=url,
        )
