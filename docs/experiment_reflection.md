# QBR Co-Pilot: Experiment & Reflection

## 1. How I Would Measure and Prove the Solution

The real test is not whether the model writes fluent text. It is whether it helps a Customer Success Manager produce a stronger QBR faster, with more consistency and less missed account risk.

- **Time saved:** compare manual QBR preparation against co-pilot-assisted preparation. The target is to reduce prep from 5+ hours to roughly 10-15 minutes of review and refinement.
- **Draft quality:** ask CSMs and team leads to score the output on accuracy, business relevance, clarity, and usefulness of recommendations.
- **Revision load:** track how much the first draft needs to be rewritten. A strong system should produce drafts that are refined, not rebuilt from scratch.
- **Adoption and trust:** measure whether CSMs return to the tool, whether they use the live reasoning panel, and whether they accept or reject the draft recommendations.

I would also run a side-by-side evaluation:

1. Human-only QBR draft
2. Co-pilot-assisted draft
3. Future agent-generated draft reviewed by a human

This would make it possible to compare speed, edit distance, recommendation quality, and leadership approval rate across increasing levels of automation.

## 2. What Worked in the PoC

- The multi-step reasoning pipeline worked better than a single-prompt approach because it separated metric analysis, qualitative context analysis, strategic synthesis, and final drafting.
- The live thought-process panel improved trust because the CSM can see how the draft is being built instead of receiving a black-box answer.
- The focus controls and audience-tone controls made the output feel meaningfully steerable. The same account can be framed around churn risk, expansion, or automation adoption, and the final narrative can shift by audience.
- The judge layer improved quality by checking whether the synthesis was grounded and aligned before the final draft was written.

The PoC therefore validated the core product hypothesis: there is real value in a QBR co-pilot that creates a strong first draft while keeping the human in control of the final narrative.

## 3. What Did Not Work Yet

- The current version relies on sample accounts and optional CSV / Excel uploads, which is enough for a prototype but not enough for a production-quality QBR system.
- It uses summarized support and CRM context rather than the full underlying records. In reality, the quality of the QBR will depend on seeing the actual tickets, notes, account events, feature adoption details, and historical context.
- The system currently reasons over a single-quarter snapshot. A real QBR should compare multiple quarters and detect meaningful trends over time.
- The upload flow is session-based rather than truly persistent, which is acceptable for a demo but not for a durable product.

In other words, the main bottleneck is no longer “can the LLM draft a QBR?” but “how rich, trustworthy, and longitudinal is the input context?”

## 4. What’s Next

First, I would connect the pipeline to real monday.com data rather than static sample files. That means not only pulling summary metrics, but also ingesting the underlying operational signals: ticket records, CRM notes, board activity, adoption events, escalation context, and historical quarter-over-quarter patterns. A preprocessing layer should normalize that context before it reaches the QBR co-pilot.

Second, I would build a true evaluation loop against expert-written QBRs. The goal would be to measure how closely the generated draft resembles the structure, priorities, and judgment of a strong CSM. That would create a benchmark for improvement instead of relying only on subjective impressions.

Third, I would evolve the system from a drafting co-pilot into a more agentic workflow. In the near term, it remains human-supervised. Over time, the judge component could become a stronger domain evaluator, additional agents could gather and prepare account context automatically, and the system could proactively surface QBR assessments for stakeholders before a human even opens the dashboard.

The long-term vision is not just “QBR writing with AI.” It is an end-to-end customer intelligence workflow in which monday.com data, historical performance, qualitative account context, and agent-based reasoning work together to produce QBRs that increasingly resemble what a strong CSM would have created manually.
