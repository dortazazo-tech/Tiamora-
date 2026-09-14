# Vendored skills — attribution

`ask-hormozi/` and `hormozi-report/` are vendored from
**https://github.com/viclaranja/hormozi-ai-skill** (MIT).

They are copied in rather than installed into `~/.claude/skills/` because this
project is worked on from ephemeral containers, where anything outside the repo
is gone at the end of the session. The skill files are small and live here; the
~300 MB engine they drive does not, and is built on first use by
`.claude/scripts/hormozi`.

Local changes against upstream:

- `{{HORMOZI_COMMAND}}`, `{{HORMOZI_PYTHON}}` and `{{HORMOZI_REPORT_SCRIPT}}`
  resolved to `.claude/scripts/hormozi`, `python3`, and the vendored renderer
  path — the substitution upstream's installer performs at install time.
- `hormozi-report/scripts/build_report.py` looks for `brand.config.json` beside
  the skill before falling back to upstream's `~/.claude/skills/...` path.

## Source material

The transcript corpus is drawn from public **MoreMozi** YouTube videos. Rights
in that material stay with **Alex Hormozi**, the MoreMozi channel, and the
applicable video owners and guests. The corpus was assembled by **Jacob Posel
and upstream contributors** — https://github.com/poseljacob/ask-hormozi

MIT covers the code only. It does not relicense the transcript material.

Independent community tooling. Not affiliated with, endorsed by, sponsored by,
or operated by Alex Hormozi, Acquisition.com, or MoreMozi. Educational source
retrieval and business analysis — not legal, financial, medical, or
individualised professional advice.
