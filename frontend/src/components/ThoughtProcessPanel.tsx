import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import type {
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
        {items.map((item) => (
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
  qualitativeInsights,
  quantitativeInsights,
  steps,
  strategicSynthesis,
}: ThoughtProcessPanelProps) {
  return (
    <Card eyebrow="Live Stream" title="Thought Process Panel">
      <div className="space-y-5">
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
            title="Quantitative insights"
            items={
              quantitativeInsights
                ? [
                    quantitativeInsights.health_status,
                    quantitativeInsights.growth_trend,
                    ...quantitativeInsights.key_metrics,
                    ...quantitativeInsights.risk_flags,
                  ]
                : []
            }
          />
          <InsightList
            title="Qualitative insights"
            items={
              qualitativeInsights
                ? [
                    qualitativeInsights.overall_sentiment,
                    ...qualitativeInsights.core_themes,
                    ...qualitativeInsights.action_signals,
                  ]
                : []
            }
          />
          <InsightList
            title="Strategic synthesis"
            items={
              strategicSynthesis
                ? [
                    strategicSynthesis.executive_summary,
                    ...strategicSynthesis.strengths,
                    ...strategicSynthesis.concerns,
                    ...strategicSynthesis.cross_sell_opportunities,
                  ]
                : []
            }
          />
        </div>
      </div>
    </Card>
  );
}
