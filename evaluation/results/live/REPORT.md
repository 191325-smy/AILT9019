# Real model results

Model: `deepseek:deepseek-flash`. Application: `81886ac18511398f320b0e592828ea00c956d7cd`.

These calls use the actual API and synthetic fixtures, not simulated provider output. Explanations are composed by the application from structured evidence returned by the model.

| Call | Status | Seconds | AI roles / programmes | Fallback roles / programmes |
|---|---|---:|---|---|
| LIVE-01-1 | PASS | 2.953 | 4 / 3 | 4 / 3 |
| LIVE-01-2 | PASS | 2.406 | 4 / 3 | 4 / 3 |
| LIVE-07-1 | PASS | 2.625 | 4 / 2 | 4 / 3 |
| LIVE-07-2 | PASS | 2.484 | 4 / 2 | 4 / 3 |
| LIVE-16-1 | PASS | 2.719 | 4 / 4 | 4 / 4 |
| LIVE-16-2 | PASS | 2.468 | 4 / 4 | 4 / 4 |

Role coverage is the union of offered concrete roles (preferred + open roles), including the student. It does not solve one-person-one-role assignment. Programme coverage includes the student. The fallback is a comparison baseline, not labelled ground truth. In the two LIVE-07 samples the model covers two programmes while fallback covers three, so the data does not establish that the model always improves diversity.

Defined factual claims: 30/30 explanations without detected errors under the automated check. See factual-audit.json for every sentence and attribute check. This is not human sign-off or a general accuracy estimate.

## LIVE-01-1

Status: PASS; source: `deepseek:deepseek-flash`.
- ID 14: Nathan Zheng can cover Agentic Development, brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 6: Frank Zhou brings programming and web development experience and comes from a different programme (Applied AI).
- ID 2: Bob Liu can cover Backend, brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 12: Leo Gao brings programming and web development experience and comes from a different programme (Others).
- ID 4: David Zhao brings debugging experience and comes from a different programme (Others).

## LIVE-01-2

Status: PASS; source: `deepseek:deepseek-flash`.
- ID 14: Nathan Zheng can cover Agentic Development, brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 6: Frank Zhou brings programming and web development experience and comes from a different programme (Applied AI).
- ID 2: Bob Liu can cover Backend, brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 12: Leo Gao brings programming and web development experience and comes from a different programme (Others).
- ID 4: David Zhao comes from a different programme (Others).

## LIVE-07-1

Status: PASS; source: `deepseek:deepseek-flash`.
- ID 6: Frank Zhou can cover Frontend, brings programming and web development experience and comes from a different programme (Applied AI).
- ID 14: Nathan Zheng can cover Agentic Development, brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 2: Bob Liu brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 11: Karen He brings GitHub and AI-agent experience.
- ID 15: Olivia Liang brings programming and web development experience.

## LIVE-07-2

Status: PASS; source: `deepseek:deepseek-flash`.
- ID 6: Frank Zhou can cover Frontend, brings programming and web development experience and comes from a different programme (Applied AI).
- ID 14: Nathan Zheng can cover Agentic Development, brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 2: Bob Liu brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
- ID 11: Karen He brings GitHub and AI-agent experience.
- ID 15: Olivia Liang brings programming and web development experience.

## LIVE-16-1

Status: PASS; source: `deepseek:deepseek-flash`.
- ID 27: Aaron Deng can cover Backend, brings programming and web development experience and comes from a different programme (Computer Science).
- ID 29: Cody Lei brings GitHub and AI-agent experience and comes from a different programme (AI and Data Science).
- ID 28: Bella Ma can cover Database and brings debugging experience.
- ID 24: Xander Guo brings programming and web development experience.
- ID 26: Zoe Shi brings GitHub and AI-agent experience and comes from a different programme (Applied AI).

## LIVE-16-2

Status: PASS; source: `deepseek:deepseek-flash`.
- ID 27: Aaron Deng can cover Backend, brings programming and web development experience and comes from a different programme (Computer Science).
- ID 29: Cody Lei brings GitHub and AI-agent experience and comes from a different programme (AI and Data Science).
- ID 28: Bella Ma can cover Database and brings debugging experience.
- ID 24: Xander Guo brings programming and web development experience.
- ID 26: Zoe Shi brings GitHub and AI-agent experience and comes from a different programme (Applied AI).
