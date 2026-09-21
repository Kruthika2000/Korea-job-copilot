"""Orchestrates the full pipeline: fetch postings, extract requirements,
skip postings with a blocking gap, retrieve relevant resume chunks,
draft a cover letter, self-critique it (re-drafting once if ungrounded),
then save the draft and log the outcome.

Run:
    python -m src.agent --source data/jobs/sample_postings.json
    python -m src.agent --source-type rss --source "<feed_url>"
"""
import argparse
import csv
import os
import sys

from . import config
from .job_fetcher import fetch_from_json, fetch_from_rss, Job
from .requirements_extractor import extract_requirements, has_requirement_gap
from .retriever import ResumeRetriever
from .drafter import draft_cover_letter
from .critique import check_grounding


def _ensure_log():
    os.makedirs(config.APPLICATIONS_DIR, exist_ok=True)
    if not os.path.exists(config.LOG_PATH):
        with open(config.LOG_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["title", "company", "status", "reason", "draft_file"])


def _log(title: str, company: str, status: str, reason: str, draft_file: str = ""):
    with open(config.LOG_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([title, company, status, reason, draft_file])


def process_job(job: Job, retriever: ResumeRetriever) -> None:
    print(f"\n--- {job.title} @ {job.company} ---")

    requirements = extract_requirements(job.title, job.description)
    gap = has_requirement_gap(requirements, config.MY_TOPIK_LEVEL)
    if gap:
        print(f"  SKIPPED: {gap}")
        _log(job.title, job.company, "skipped", gap)
        return

    chunks = retriever.retrieve(job.description, top_k=4)
    draft = draft_cover_letter(job.title, job.company, job.description, chunks)

    check = check_grounding(draft, chunks)
    if not check.get("grounded", False):
        print(f"  Draft failed grounding check ({check.get('unsupported_claims')}), retrying once...")
        draft = draft_cover_letter(job.title, job.company, job.description, chunks)
        check = check_grounding(draft, chunks)

    status = "drafted" if check.get("grounded", False) else "drafted_unverified"
    safe_name = "".join(c if c.isalnum() else "_" for c in f"{job.company}_{job.title}")[:60]
    draft_path = os.path.join(config.APPLICATIONS_DIR, f"{safe_name}.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(f"# {job.title} @ {job.company}\n\n{draft}\n")

    print(f"  Draft saved: {draft_path} ({status})")
    _log(job.title, job.company, status, "", draft_path)


def main():
    parser = argparse.ArgumentParser(description="Korea Job-Search Copilot")
    parser.add_argument("--source", required=True, help="Path to JSON file or RSS feed URL")
    parser.add_argument("--source-type", choices=["json", "rss"], default="json")
    args = parser.parse_args()

    if not config.ANTHROPIC_API_KEY:
        print("ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.", file=sys.stderr)
        sys.exit(1)

    _ensure_log()

    jobs: list[Job] = (
        fetch_from_rss(args.source) if args.source_type == "rss" else fetch_from_json(args.source)
    )
    print(f"Fetched {len(jobs)} postings from {args.source_type}: {args.source}")

    retriever = ResumeRetriever()
    for job in jobs:
        process_job(job, retriever)


if __name__ == "__main__":
    main()
