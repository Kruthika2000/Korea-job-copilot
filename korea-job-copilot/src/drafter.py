"""Drafts a cover letter grounded ONLY in retrieved resume chunks, using
a few-shot example of my own writing voice so it doesn't read like
generic LLM boilerplate.
"""
from . import config

_VOICE_EXAMPLE = """Example of my own writing voice (do not copy content, \
match tone/register only):

"I'm not the most experienced person you'll interview for this, but I've \
shipped the parts of the stack that usually get skipped in a portfolio \
project: the eval harness, the retry logic, the part where it breaks at \
3am and you have to know why." """

_SYSTEM = f"""You draft cover letters for a candidate applying to remote \
AI Engineer roles targeting Korea. Rules:
- Use ONLY the facts given in the "Candidate background" section below. \
Never invent skills, companies, tools, or achievements not present there.
- Keep it under 200 words.
- Match a direct, slightly understated tone — not "I am thrilled to apply."
- End with one concrete, specific sentence about the role, not a generic \
closing line.

{_VOICE_EXAMPLE}"""


def draft_cover_letter(job_title: str, company: str, job_description: str, resume_chunks: list[str]) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    background = "\n\n".join(resume_chunks) if resume_chunks else "(no matching background found)"
    user_msg = (
        f"Job: {job_title} at {company}\n\n"
        f"Job description:\n{job_description}\n\n"
        f"Candidate background (only source of truth for claims):\n{background}"
    )
    response = client.messages.create(
        model=config.MODEL,
        max_tokens=400,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()
