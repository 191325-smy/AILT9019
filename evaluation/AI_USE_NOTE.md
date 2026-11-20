# AI assistance and team verification

This is a factual note for the team to adapt into the final report's seven disclosure fields, not a completed human contribution statement.

- Tool: Codex assistant. The evaluated application's model is DeepSeek Flash through LangChain; exact installed packages are recorded in requirements-tested.txt and result metadata.
- Tasks supported: inspection of requirements and repository code; creation of acceptance cases, synthetic preference variants, evidence runners, a test-only app adapter, result summaries and proposed report text.
- Representative interaction: evaluate the team's latest code against final-submission requirements; preserve failures and distinguish simulated outputs from actual API execution.
- Material retained: files under evaluation/, generated fixtures, recorded test/live/browser evidence, and report excerpts. No runtime application files were modified.
- Verification actually performed: immutable GitHub blob comparison for 35 source files; 55 offline cases in the recorded environment; dependency installation/pip check; six direct live-model calls; seven browser scenarios including one more live-model call; automatic claim checks and visual inspection of the AI and empty-result evidence. These activities were conducted by the assistant using tools, not attributed to a human team member.
- Known limitations: four failing product tests; simulated cache transport; no shared PostgreSQL or deployed-service verification; synthetic and small model sample; automatic explanation checking is restricted to defined claims and does not establish human usefulness/fairness.
- Responsible human team members: **to be supplied by the team after actual review**. Confirm who inspected the cases/results, reproduced the run and approved any text included in the final report. Do not claim human verification until it occurred.
