import math


def _salton_cosine(set_a: set[str], set_b: set[str]) -> float:
    """Cosine similarity between two sets. Returns 0.0 if either is empty."""
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / math.sqrt(len(set_a) * len(set_b))


def bibliographic_coupling(refs_a: set[str], refs_b: set[str]) -> float:
    """BC score: high when two papers share the same references."""
    return _salton_cosine(refs_a, refs_b)


def co_citation_score(citers_a: set[str], citers_b: set[str]) -> float:
    """Co-citation score: high when two papers are cited by the same papers."""
    return _salton_cosine(citers_a, citers_b)
