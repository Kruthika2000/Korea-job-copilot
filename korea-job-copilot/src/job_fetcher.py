"""Adapters that pull job postings from different sources and normalize
them into a single Job shape, so the rest of the pipeline doesn't care
whether a posting came from RSS or a manually curated JSON file.
"""
from dataclasses import dataclass
import json


@dataclass
class Job:
    title: str
    company: str
    url: str
    description: str
    source: str


def fetch_from_json(path: str) -> list[Job]:
    """Load postings from a local JSON file. Useful for the demo, for
    manually curated postings, or for sites with no RSS/API access."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [
        Job(
            title=item["title"],
            company=item["company"],
            url=item.get("url", ""),
            description=item["description"],
            source="json",
        )
        for item in raw
    ]


def fetch_from_rss(feed_url: str, limit: int = 20) -> list[Job]:
    """Pull postings from a job board's RSS feed. Many boards (Indeed,
    WeWorkRemotely, RemoteOK, etc.) expose one — this keeps the fetcher
    generic instead of hardcoding a single paid API."""
    import feedparser

    parsed = feedparser.parse(feed_url)
    jobs = []
    for entry in parsed.entries[:limit]:
        jobs.append(
            Job(
                title=entry.get("title", "Untitled"),
                company=entry.get("author", "Unknown"),
                url=entry.get("link", ""),
                description=entry.get("summary", ""),
                source="rss",
            )
        )
    return jobs
