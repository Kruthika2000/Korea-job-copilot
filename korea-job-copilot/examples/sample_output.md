# Example run against `data/jobs/sample_postings.json`

```
Fetched 3 postings from json: data/jobs/sample_postings.json

--- Junior AI Engineer (Remote) @ Hanul Labs ---
  Draft saved: data/applications/Hanul_Labs_Junior_AI_Engineer__Remote_.md (drafted)

--- AI Platform Engineer @ Seoul FinTech Co ---
  SKIPPED: Requires TOPIK 4+, I'm at TOPIK 2

--- AI Tools Engineer (Remote, Korea-based team) @ Nomad AI ---
  Draft saved: data/applications/Nomad_AI_AI_Tools_Engineer__Remote__Korea_based_team_.md (drafted)
```

`data/applications/log.csv` after the run:

| title | company | status | reason | draft_file |
|---|---|---|---|---|
| Junior AI Engineer (Remote) | Hanul Labs | drafted | | .../Hanul_Labs_...md |
| AI Platform Engineer | Seoul FinTech Co | skipped | Requires TOPIK 4+, I'm at TOPIK 2 | |
| AI Tools Engineer (Remote, Korea-based team) | Nomad AI | drafted | | .../Nomad_AI_...md |

The second posting never reaches the drafting step at all — the
requirement-gap check catches it right after extraction, which is the
behavior described in the README's design-decisions section (catching
this earlier cut wasted drafting calls by about a third in my own runs).
