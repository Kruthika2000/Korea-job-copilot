"""First agent step: turn a free-text job posting into structured
requirements, so the pipeline can decide whether to bother drafting a
cover letter at all before spending more API calls on it.
"""
import json

from . import config

_SYSTEM = """You extract structured requirements from job postings for a \
candidate evaluating remote AI Engineer roles based in or hiring into Korea.

Respond with ONLY a JSON object, no preamble, no markdown fences, in this \
exact shape:
{
  "required_skills": ["..."],
  "korean_language_requirement": "none" | "conversational" | "TOPIK 2" | "TOPIK 3" | "TOPIK 4+" | "fluent",
  "visa_sponsorship_mentioned": true | false,
  "remote_ok": true | false,
  "seniority": "intern" | "junior" | "mid" | "senior" | "unclear"
}
If a field isn't mentioned, make the most reasonable inference and note \
uncertainty by choosing the most conservative option (e.g. assume \
sponsorship is NOT mentioned unless stated)."""


def extract_requirements(job_title: str, job_description: str) -> dict:
    import anthropic  # imported lazily so gap-check logic is testable without the SDK installed

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=config.MODEL,
        max_tokens=500,
        system=_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Title: {job_title}\n\nDescription:\n{job_description}",
            }
        ],
    )
    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def has_requirement_gap(requirements: dict, my_topik_level: str) -> str | None:
    """Returns a human-readable gap reason, or None if there's no blocking gap."""
    topik_rank = {"none": 0, "conversational": 1, "TOPIK 2": 2, "TOPIK 3": 3, "TOPIK 4+": 4, "fluent": 5}
    required = requirements.get("korean_language_requirement", "none")
    mine = my_topik_level if my_topik_level in topik_rank else "TOPIK 2"
    if topik_rank.get(required, 0) > topik_rank.get(mine, 0):
        return f"Requires {required}, I'm at {mine}"
    if not requirements.get("remote_ok", True):
        return "Not remote-friendly"
    return None
