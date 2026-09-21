"""Second LLM pass: checks that every specific claim in a draft traces
back to a retrieved resume chunk. Catches plausible-sounding hallucinated
specifics that a keyword-overlap check missed in earlier versions (see
README design-decisions section).
"""
import json

from . import config

_SYSTEM = """You fact-check a cover letter draft against a candidate's \
actual background. List every specific, checkable claim in the draft \
(tools, companies, numbers, achievements) and whether it is supported by \
the provided background chunks.

Respond with ONLY JSON in this shape:
{
  "grounded": true | false,
  "unsupported_claims": ["..."]
}
"grounded" is true only if unsupported_claims is empty."""


def check_grounding(draft: str, resume_chunks: list[str]) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    background = "\n\n".join(resume_chunks) if resume_chunks else "(none)"
    user_msg = f"Draft:\n{draft}\n\nBackground chunks:\n{background}"
    response = client.messages.create(
        model=config.MODEL,
        max_tokens=400,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)
