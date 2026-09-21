"""Tests that don't require an API key: gap-detection logic and the
JSON job-fetch adapter. The LLM-calling functions (extraction, drafting,
critique) are exercised via the CLI demo run instead, since mocking them
meaningfully would just test the mock.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.requirements_extractor import has_requirement_gap
from src.job_fetcher import fetch_from_json


def test_gap_when_topik_too_high():
    reqs = {"korean_language_requirement": "TOPIK 4+", "remote_ok": True}
    assert has_requirement_gap(reqs, "TOPIK 2") is not None


def test_no_gap_when_requirement_met():
    reqs = {"korean_language_requirement": "TOPIK 2", "remote_ok": True}
    assert has_requirement_gap(reqs, "TOPIK 2") is None


def test_gap_when_not_remote():
    reqs = {"korean_language_requirement": "none", "remote_ok": False}
    assert has_requirement_gap(reqs, "TOPIK 2") is not None


def test_fetch_from_json_normalizes_fields():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "jobs", "sample_postings.json")
    jobs = fetch_from_json(path)
    assert len(jobs) == 3
    assert jobs[0].source == "json"
    assert jobs[0].title == "Junior AI Engineer (Remote)"


if __name__ == "__main__":
    test_gap_when_topik_too_high()
    test_no_gap_when_requirement_met()
    test_gap_when_not_remote()
    test_fetch_from_json_normalizes_fields()
    print("All tests passed.")
