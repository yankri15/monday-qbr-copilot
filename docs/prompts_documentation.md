# QBR Co-Pilot: Prompts & Components Documentation

## 1. Prompt Strategy

The PoC does not rely on a single prompt. It splits the workflow into specialized steps so each model sees only the context it needs:

- **Insight extraction:** separate structured and unstructured analysis
- **Summarization and recommendations:** combine both views into one account strategy
- **Drafting:** turn the synthesis into a final QBR narrative
- **Refinement:** let the CSM revise the draft without rerunning the entire pipeline

This structure improves grounding and makes failures easier to detect and correct.

## 2. Key Prompts

### A. Insight Extraction

**Quant Agent**

Purpose: interpret already-structured metrics such as usage growth, automation adoption, support burden, NPS, SCAT, and churn risk into a compact business readout.

Key instructions:

> Analyze only the provided structured account metrics.
> Call out usage growth as the main conversation driver.
> Flag low automation adoption as a risk signal.
> Do not invent values.

This node is intentionally modular. It is not raw rule logic; it is an interpretation layer over structured signals that pre-shapes the quantitative picture into business-relevant outputs and creates a clean place to absorb richer or noisier quantitative inputs later.

**Qual Agent**

Purpose: analyze CRM notes and customer feedback.

Key instructions:

> Analyze only the CRM notes and feedback summary.
> Extract themes, sentiment, and actionable signals.
> Detect churn-risk language and champion signals.
> Keep the draft centered on monday.com value without erasing meaningful references to external tools, competitors, or integration needs when they are part of the account story.

### B. Summarization and Recommendations

**Strategist**

Purpose: combine quantitative and qualitative findings into a strategic account view.

Key instructions:

> Every key insight must support either retention or expansion.
> Every recommendation must be evidence-grounded.
> Use monday.com Work OS vocabulary.
> Do not invent product capabilities, roadmap promises, or account history.

This stage is also where the CSM’s selected **focus area** is applied. For example, `churn_risk` pushes the synthesis toward retention and mitigation, while `upsell_opportunity` pushes it toward expansion.

### C. Final Drafting

**Editor**

Purpose: convert the strategic synthesis into the QBR draft.

Key instructions:

> Turn the strategic synthesis into a polished Markdown draft.
> Keep the writing evidence-grounded and presentation-ready.
> Adapt to the requested audience tone.
> Do not mention that an AI wrote the draft.

This is where the selected **audience tone** is applied:

- `executive` -> strategic, high-level, ROI-oriented
- `team_lead` -> operational, workflow-specific
- `technical` -> implementation-oriented

## 3. Structured Outputs

Structured outputs are central to the design because they force the analytical steps to return known fields instead of free-form text.

### QuantInsights

- `health_status`
- `key_metrics`
- `growth_trend`
- `risk_flags`

### QualInsights

- `overall_sentiment`
- `core_themes`
- `key_quotes`
- `action_signals`

### StrategicSynthesis

- `executive_summary`
- `strengths`
- `concerns`
- `recommendations`
- `cross_sell_opportunities`
- `data_citations`

### Recommendation

Each recommendation also carries:

- `recommendation`
- `evidence`
- `grounding_metrics`

This is important because the system is not only asked to produce advice, but to show why that advice is justified.

## 4. Hallucination Prevention and Grounding

The PoC uses several layers to reduce hallucinations:

1. **Separation of concerns**
   - Quant only sees structured metrics and turns them into a compact business readout.
   - Qual only sees CRM notes and feedback.
   - Strategist combines both.

2. **Strict structured outputs**
   - Analytical agents use Pydantic schemas with extra fields forbidden.
   - JSON-schema output mode keeps results in a known format.

3. **Evidence grounding**
   - Recommendations must include `evidence` and `grounding_metrics`.
   - The Strategist is explicitly instructed not to invent claims.

4. **Judge step**
   - A CSM Judge reviews the synthesis for actionability, grounding, retention/expansion framing, and monday.com language.
   - If needed, the Strategist retries before the draft reaches the Editor.

5. **Brand guardrails**
   - Brand guardrails keep the report centered on monday.com value and next steps without erasing meaningful source evidence such as competitor mentions, integration requests, or switching-risk signals when they matter to the account story.

## 5. Temperature and Format Choices

| Component | Output Type | Temperature | Why |
|----------|-------------|-------------|-----|
| Quant Agent | Structured JSON | `0.0` | Stable interpretation of structured signals into a compact business readout |
| Qual Agent | Structured JSON | `0.0` | Stable extraction of themes and sentiment from notes |
| Strategist | Structured JSON | `0.3` | Some flexibility, still grounded |
| CSM Judge | Structured JSON | `0.0` | Stable quality scoring |
| Editor | Markdown | `0.2` | Natural but controlled prose |
| Refiner | Markdown | `0.3` | Flexible instruction-following |

## 6. Awareness of Model Limits

This PoC assumes the model is good at synthesis but not automatically trustworthy. That is why the design avoids asking one prompt to do everything and why the final output remains editable. The co-pilot’s role is to draft a strong first version for the CSM, not to replace judgment, approval, or customer-facing accountability.
