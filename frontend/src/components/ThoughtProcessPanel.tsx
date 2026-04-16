import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import type {
  JudgeVerdict,
  QualInsights,
  QuantInsights,
  StepName,
  StepStatus,
  StrategicSynthesis,
} from "@/lib/types";

type StepState = {
  name: StepName;
  label: string;
  message: string;
  status: StepStatus;
};

type ThoughtProcessPanelProps = {
  steps: StepState[];
  quantitativeInsights?: QuantInsights;
  qualitativeInsights?: QualInsights;
  strategicSynthesis?: StrategicSynthesis;
  judgeVerdict?: JudgeVerdict;
};

function InsightList({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  if (!items.length) {
    return null;
  }

  return (
    <div className="space-y-3 rounded-[22px] border border-[color:var(--color-border-soft)] bg-white/88 p-4">
      <h4 className="text-sm font-semibold text-[color:var(--color-text-main)]">{title}</h4>
      <ul className="space-y-2 text-sm text-[color:var(--color-text-subtle)]">
        {items.slice(0, 4).map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-1.5 h-2 w-2 rounded-full bg-[color:var(--color-brand-blue)]" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ThoughtProcessPanel({
  judgeVerdict,
  qualitativeInsights,
  quantitativeInsights,
  steps,
  strategicSynthesis,
}: ThoughtProcessPanelProps) {
  return (
    <Card eyebrow="Co-Pilot Activity" title="How the draft is being built">
      <div className="space-y-5">
        <div className="rounded-[22px] bg-[color:var(--color-surface-muted)] px-4 py-3 text-sm leading-6 text-[color:var(--color-text-subtle)]">
          The co-pilot stays visible so the CSM can trust the draft, challenge it, and
          keep the final call.
        </div>

        <div className="grid gap-3">
          {steps.map((step, index) => (
            <div
              key={step.name}
              className={cn(
                "relative overflow-hidden rounded-[22px] border px-4 py-4 transition",
                step.status === "running" &&
                  "border-[color:var(--color-brand-blue)]/30 bg-[linear-gradient(135deg,rgba(91,108,255,0.12),rgba(111,63,245,0.08))]",
                step.status === "completed" &&
                  "border-[color:var(--color-accent-mint)]/20 bg-[color:var(--color-accent-mint)]/7",
                step.status === "idle" &&
                  "border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-muted)]",
              )}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="mb-2 flex items-center gap-3">
                    <span className="font-mono text-xs text-[color:var(--color-text-subtle)]">
                      0{index + 1}
                    </span>
                    <h3 className="text-sm font-semibold text-[color:var(--color-text-main)]">
                      {step.label}
                    </h3>
                  </div>
                  <p className="text-sm leading-6 text-[color:var(--color-text-subtle)]">
                    {step.message}
                  </p>
                </div>
                <Badge
                  tone={
                    step.status === "completed"
                      ? "success"
                      : step.status === "running"
                        ? "brand"
                        : "neutral"
                  }
                >
                  {step.status === "completed"
                    ? "Done"
                    : step.status === "running"
                      ? "Running"
                      : "Queued"}
                </Badge>
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <InsightList
            title="Account signals"
            items={
              quantitativeInsights
                ? [
                    quantitativeInsights.health_status,
                    quantitativeInsights.growth_trend,
                    ...quantitativeInsights.key_metrics.slice(0, 2),
                    ...quantitativeInsights.risk_flags.slice(0, 1),
                  ]
                : []
            }
          />
          <InsightList
            title="CSM context"
            items={
              qualitativeInsights
                ? [
                    ...qualitativeInsights.retention_risks.slice(0, 2),
                    qualitativeInsights.overall_sentiment,
                    ...qualitativeInsights.core_themes.slice(0, 1),
                    ...qualitativeInsights.action_signals.slice(0, 1),
                  ]
                : []
            }
          />
          <InsightList
            title="Draft direction"
            items={
              strategicSynthesis
                ? [
                    ...strategicSynthesis.recommendations
                      .slice(0, 2)
                      .map((recommendation) => recommendation.recommendation),
                    ...strategicSynthesis.concerns.slice(0, 1),
                    ...strategicSynthesis.cross_sell_opportunities.slice(0, 1),
                  ]
                : []
            }
          />
        </div>

        {judgeVerdict ? (
          <div className="rounded-[22px] border border-[color:var(--color-border-soft)] bg-white/88 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h4 className="text-sm font-semibold text-[color:var(--color-text-main)]">
                  CSM quality gate
                </h4>
                <p className="mt-1 text-sm leading-6 text-[color:var(--color-text-subtle)]">
                  {judgeVerdict.critique}
                </p>
              </div>
              <Badge tone={judgeVerdict.passed ? "success" : "warning"}>
                {judgeVerdict.passed ? "Passed" : "Needs revision"}
              </Badge>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              {Object.entries(judgeVerdict.scores).map(([criterion, score]) => (
                <div
                  key={criterion}
                  className="rounded-[18px] bg-[color:var(--color-surface-muted)] px-3 py-3"
                >
                  <p className="text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-[color:var(--color-text-subtle)]">
                    {criterion.replaceAll("_", " ")}
                  </p>
                  <p className="mt-2 text-lg font-semibold text-[color:var(--color-text-main)]">
                    {score}/10
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </Card>
  );
}
