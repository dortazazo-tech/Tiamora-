# report.json — structure

The top level must be a JSON **object**, and `sections` — if present — must be a **list**. Everything else is optional and degrades cleanly: a report with no `meta` renders with a default title, and every omitted block disappears from both the render and the nav.

One deliberate exception: the **Sources appendix always renders**, even with zero citations, where it states plainly that nothing was cited. That is a fact the reader needs, not an empty block worth hiding.

```jsonc
{
  "meta": {
    "title": "Where the next $100k/mo is actually blocked",   // the H1 — a finding, not a label
    "subject": "Acme Coaching",                              // sidebar + filename
    "kicker": "Citation-backed diagnosis",                    // small sidebar line
    "eyebrow": "Business diagnosis",                          // above the H1
    "lede": "One paragraph. The whole argument in ~40 words.",
    "date": "2026-08-04",
    "mode": "full",
    "corpus": { "videos": 2039, "segments": 9330 }
  },

  "verdict": {
    "headline": "One sentence. The call, stated plainly.",
    "summary": ["Paragraph.", "Paragraph."],                  // string or array
    "constraint": "Sales — closer capacity, not lead volume", // the #1, restated
    "confidence": "high"                                      // high | medium | low
  },

  // THE CONSTRAINT BOARD — the first thing the reader sees and clicks.
  // Exactly three, ranked. Each card jumps to the section that analyses it.
  "constraints": [
    {
      "rank": 1,
      "title": "Owner capacity",                  // short — it's a card heading
      "note": "One line on why this is the ceiling.",
      "target": "constraint",                     // id of the section to jump to
      "impact": 90,                               // 0-100, drives the meter
      "metric": "~70 hrs/wk"                      // optional figure on the card
    },
    { "rank": 2, "title": "...", "note": "...", "target": "pricing",   "impact": 65 },
    { "rank": 3, "title": "...", "note": "...", "target": "retention", "impact": 40 }
  ],

  "metrics": [
    { "label": "Demo → close", "value": "56%", "note": "Above Hormozi's 30–40% band." }
  ],

  "snapshot": [
    { "field": "Core offer", "value": "$5k / 6 months", "status": "verified" }
    // status: verified | inferred | missing  → drives the colour badge
  ],

  "sections": [
    {
      "id": "pricing",                    // optional; slugged from title if absent
      "title": "Offer and pricing",
      "summary": "One line under the section heading.",
      "subsections": [
        {
          "id": "pricing-close-rate",
          "title": "Close rate is a pricing signal",
          "plain": "Closing more than 4 in 10 usually means the price is too low.",
          "body": [
            "Paragraph of formal prose.",
            "Another paragraph."
          ],
          "evidence": [
            {
              "quote": "...",              // paste verbatim from search --format json
              "timestamp_url": "https://www.youtube.com/watch?v=5z5TOgxaV1c&t=90s",
              "title": "How to Raise Prices Based on Close Rate",
              "published": "2026-03-12",
              "episode_id": "5z5TOgxaV1c", // groups the sources appendix
              "start_seconds": 90
            }
          ],
          "synthesis": "Your interpretation. Renders in a separate labelled block.",
          "callout": { "type": "action", "text": "..." }   // action | risk | note
        }
      ]
    }
  ],

  "actions": [
    { "priority": 1, "action": "...", "why": "...", "owner": "Owner", "due": "Week 1" }
  ],

  "scorecard": [
    { "metric": "Demo → close", "baseline": "56%", "target": "40–45% at higher price",
      "owner": "Owner", "cadence": "Weekly" }
  ],

  "assumptions": ["Plain statements of what is unverified and what would change if wrong."]
}
```

## Rules the renderer will not enforce for you

- **`quote` must be verbatim** from a `search --format json` result. Never retype, tidy, or reconstruct one.
- **Trim the quote yourself.** Quotes render at most **480 characters**, then hard-truncate with `…`. Live search results routinely run 1,000+, so the default path always truncates — cut to the load-bearing sentence so the cut lands where *you* chose it, not mid-word.
- **`timestamp_url` must be copied whole**, `t=` intact. The renderer derives the visible `0:00` label from `start_seconds`; if `t=` and `start_seconds` disagree by more than two seconds it prints a `citation mismatch` warning to stderr. Treat that warning as a bug in the report, not noise.
- **Citation URLs must be YouTube over https.** Anything else is dropped, the link degrades to plain text, and a rejection warning goes to stderr. A rejected URL almost always means a hallucinated one.
- **`body` vs `synthesis`** is the integrity line of the whole document. Corpus claims go in `body` next to their evidence. Your reasoning goes in `synthesis`. The render styles them differently on purpose.
- **`episode_id`** is what groups the sources appendix. Drop it and every passage becomes its own card.
- **`callout.type` must be one of `action | risk | note`.** Anything else renders as an unstyled grey box — no error, just a silently meaningless signal.
- Paragraphs support `**bold**`, `*italic*`, `` `code` `` — nothing else. HTML in a string is escaped, not rendered. Emphasis markers must hug their text (`**like this**`, not `** like this **`), so a stray asterisk in prose stays literal.
- **Section and subsection `id`s are made unique automatically.** Two sections sharing a title will not collide, and a section titled "Sources" will not hijack the appendix anchor.

## Length

A full report runs 5–8 sections, 2–4 subsections each, 2–4 paragraphs per subsection. Under ~2,000 words it isn't a long-form report; over ~6,000 nobody reads it.
