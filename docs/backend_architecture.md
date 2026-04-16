# Flow Architecture Diagram

## 1. Product Flow Overview

```mermaid
flowchart TD
    S["Bundled sample account data"] --> L["Account data loader"]
    U["Optional uploaded customer file"] --> X["Upload flow"]
    X --> M["Session account store"]

    L --> A["Account library"]
    M --> A

    A --> D["CSM dashboard"]
    D --> W["QBR workspace"]

    W --> G["Generate draft request"]
    G --> B["QBR co-pilot service"]
    B --> H["AI workflow"]
    H --> E["Live draft stream"]
    E --> W

    W --> R["Refine draft request"]
    R --> B
    W --> P["Export as Markdown or PDF"]
```

This diagram shows the high-level product flow: account data is loaded, the CSM selects an account, the co-pilot generates a first draft, and the workspace supports refinement and export.

## 2. AI Reasoning Workflow

```mermaid
flowchart TD
    START([Start]) --> QA["Quant review<br/>structured signals"]
    QA --> QLA["Qual review<br/>CRM notes + feedback"]
    QLA --> STR["Strategy synthesis<br/>insights + recommendations"]
    STR --> J["Quality judge<br/>grounding check"]
    J -->|retry needed| STR
    J -->|approved or max retries| ED["Draft writer<br/>final QBR draft"]
    ED --> END([Draft ready])
```

This is the core AI workflow. Instead of relying on one large prompt, the co-pilot separates signal extraction, strategic synthesis, quality review, and final drafting so the result is easier to trust and easier to review.

## 3. CSM Journey Sequence

```mermaid
sequenceDiagram
    participant CSM as CSM
    participant UI as QBR Workspace
    participant COPILOT as QBR Co-Pilot
    participant AI as AI Workflow

    CSM->>UI: Select account and set optional controls
    UI->>COPILOT: Request first QBR draft
    COPILOT->>AI: Analyze metrics and CRM context
    AI-->>UI: Stream reasoning and draft sections
    CSM->>UI: Review and request refinements
    UI->>COPILOT: Send refinement instruction
    COPILOT-->>UI: Return updated draft
    CSM->>UI: Export final version
```

This sequence diagram shows the intended user journey: the CSM stays in control throughout the workflow, while the co-pilot accelerates drafting, explains its reasoning, and supports revision before export.
