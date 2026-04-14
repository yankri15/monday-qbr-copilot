export type PlanType = "Enterprise" | "Pro" | "Basic";
export type PreferredChannel = "Email" | "Phone" | "Chat" | "In-app chat";
export type StepName = "quant_agent" | "qual_agent" | "strategist" | "editor";
export type StepStatus = "idle" | "running" | "completed";

export type Account = {
  account_name: string;
  plan_type: PlanType;
  active_users: number;
  usage_growth_qoq: number;
  automation_adoption_pct: number;
  tickets_last_quarter: number;
  avg_response_time: number;
  nps_score: number;
  preferred_channel: PreferredChannel;
  scat_score: number;
  risk_engine_score: number;
  crm_notes: string;
  feedback_summary: string;
};

export type QuantInsights = {
  health_status: string;
  key_metrics: string[];
  growth_trend: string;
  risk_flags: string[];
};

export type QualInsights = {
  overall_sentiment: string;
  core_themes: string[];
  key_quotes: string[];
  action_signals: string[];
};

export type Recommendation = {
  recommendation: string;
  evidence: string;
  grounding_metrics: string[];
};

export type StrategicSynthesis = {
  executive_summary: string;
  strengths: string[];
  concerns: string[];
  recommendations: Recommendation[];
  cross_sell_opportunities: string[];
  data_citations: string[];
};

export type WorkflowInsights = {
  quantitative_insights?: QuantInsights;
  qualitative_insights?: QualInsights;
  strategic_synthesis?: StrategicSynthesis;
  final_draft?: string;
};

export type GenerateQbrPayload = {
  account_name: string;
};

export type GenerateEvent =
  | { type: "RUN_STARTED"; threadId: string; runId: string }
  | { type: "STEP_STARTED"; stepName: StepName; message?: string }
  | { type: "STEP_FINISHED"; stepName: StepName }
  | { type: "STATE_DELTA"; delta: Array<{ op: "add" | "replace"; path: string; value: unknown }> }
  | { type: "TEXT_MESSAGE_START"; messageId: string }
  | { type: "TEXT_MESSAGE_CONTENT"; messageId: string; delta: string }
  | { type: "TEXT_MESSAGE_END"; messageId: string }
  | { type: "RUN_FINISHED"; threadId: string; runId: string }
  | { type: "RUN_ERROR"; message: string; code?: string };

export type GenerateQbrHandlers = {
  onEvent?: (event: GenerateEvent) => void;
  onDraftChunk?: (chunk: string) => void;
  onComplete?: () => void;
};

export type AccountCardTone = "success" | "warning" | "danger";
