# QBR Co-Pilot: Design Brief

## 1. Problem Framing

Customer Success Managers at monday.com often spend more than 5 hours preparing a Quarterly Business Review for a single account. The work is repetitive but cognitively heavy: they need to combine structured account signals such as usage growth, automation adoption, support volume, NPS, and health scores with unstructured CRM notes and customer feedback. The result is slow preparation, inconsistent storytelling across accounts, and a higher chance of missing retention or expansion signals.

The QBR Co-Pilot addresses this by generating a strong first draft rather than replacing the CSM. The system analyzes the account, explains its reasoning, proposes evidence-grounded recommendations, and leaves the final narrative and sign-off in human hands.

## 2. User Persona

**Primary user: Customer Success Manager**

- Owns a portfolio of accounts and needs to prepare QBRs quickly without losing account-specific nuance.
- Wants a draft that is grounded in data, presentation-ready, and easy to refine.
- Needs to trust the output, so transparency matters as much as speed.

**Secondary user: CS Team Lead**

- Reviews QBR quality and consistency across the team.
- Wants every QBR to include clear account health signals, actionable next steps, and consistent structure.

## 3. What Success Looks Like

- **Time reduction:** move from 5+ hours of manual prep to roughly 10-15 minutes of review and refinement.
- **Better consistency:** every QBR follows a clear structure and includes grounded recommendations.
- **Higher trust:** the CSM can see the co-pilot’s reasoning and challenge or refine the draft before using it.
- **Business usefulness:** outputs help the CSM act on churn risk, adoption friction, or expansion opportunity, not just summarize the quarter.

## 4. Assumptions and Limitations

**Assumptions**

- The 13-field assignment dataset contains enough signal to draft a useful QBR.
- A multi-step workflow performs better than a single monolithic prompt because extraction, synthesis, and editing are separated.
- The CSM is willing to review and refine a generated draft rather than expect a final ready-to-send artifact with no edits.

**Limitations**

- The PoC uses a **simulated 5-account dataset**, not live monday.com, CRM, or support system data.
- It reflects a **single-quarter snapshot**, so there is no real multi-quarter trend analysis.
- The uploaded-data flow is useful for demoing the experience, but it is **not durable storage** yet.
- The current version is a **single-user PoC** with no authentication, tenancy, or production data governance.

## 5. Prioritization

- Generate a usable QBR draft from both structured and unstructured customer data.
- Keep recommendations evidence-grounded.
- Preserve human review and editing in the workflow.
- Stream the co-pilot reasoning live in the UI.
- Let the CSM steer the draft before generation with focus areas and audience tone.
- Support refine and export actions for the final draft.

## 6. Validation Approach

The most useful way to validate the product would be with real CSM usage rather than offline prompt scoring alone.

1. **Time saved:** compare manual QBR prep time against co-pilot-assisted prep time.
2. **Draft usefulness:** ask CSMs whether the first draft is strong enough to refine instead of rewrite.
3. **Leadership review:** have CS leaders score business relevance, actionability, and consistency across QBRs.
4. **Behavioral adoption:** track whether users come back to the workflow and how much revision is needed before a draft becomes usable.
