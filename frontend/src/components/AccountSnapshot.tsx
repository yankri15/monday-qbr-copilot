import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { Account } from "@/lib/types";

function metricTone(riskScore: number) {
  if (riskScore >= 0.65) {
    return "danger";
  }
  if (riskScore >= 0.3) {
    return "warning";
  }
  return "success";
}

function ProgressBar({
  label,
  value,
  displayValue,
  tone = "blue",
}: {
  label: string;
  value: number;
  displayValue: string;
  tone?: "blue" | "mint" | "gold";
}) {
  const width = `${Math.max(8, Math.min(100, value * 100))}%`;
  const colors = {
    blue: "from-[color:var(--color-brand-blue)] to-[color:var(--color-brand-purple)]",
    mint: "from-[color:var(--color-accent-mint)] to-[color:var(--color-accent-mint-strong)]",
    gold: "from-[color:var(--color-accent-gold)] to-[color:var(--color-accent-gold-strong)]",
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-[color:var(--color-text-subtle)]">{label}</span>
        <span className="font-semibold text-[color:var(--color-text-main)]">{displayValue}</span>
      </div>
      <div className="h-2.5 rounded-full bg-[color:var(--color-surface-muted)]">
        <div className={`h-full rounded-full bg-gradient-to-r ${colors[tone]}`} style={{ width }} />
      </div>
    </div>
  );
}

function getPriorityCards(account: Account) {
  return [
    {
      label: "QBR angle",
      value:
        account.risk_engine_score >= 0.45 || account.usage_growth_qoq < 0
          ? "Retention story"
          : account.automation_adoption_pct < 0.35
            ? "Adoption story"
            : "Expansion story",
    },
    {
      label: "Lead with",
      value:
        account.usage_growth_qoq >= 0
          ? `${Math.round(account.usage_growth_qoq * 100)}% QoQ usage growth`
          : `${Math.abs(Math.round(account.usage_growth_qoq * 100))}% QoQ usage drop`,
    },
    {
      label: "Follow-up via",
      value: account.preferred_channel,
    },
  ];
}

export function AccountSnapshot({ account }: { account: Account }) {
  const priorityCards = getPriorityCards(account);

  return (
    <div className="grid gap-5 xl:grid-cols-[1.2fr_0.9fr]">
      <Card eyebrow="QBR Brief" title={account.account_name}>
        <div className="space-y-5">
          <div className="flex flex-wrap items-center gap-3">
            <Badge tone="brand">{account.plan_type}</Badge>
            <Badge tone={metricTone(account.risk_engine_score)}>
              Risk score {Math.round(account.risk_engine_score * 100)}%
            </Badge>
            <Badge tone="neutral">{account.preferred_channel}</Badge>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-[22px] border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-muted)] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[color:var(--color-text-subtle)]">
                Adoption footprint
              </p>
              <p className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-[color:var(--color-text-main)]">
                {account.active_users}
              </p>
              <p className="mt-1 text-sm text-[color:var(--color-text-subtle)]">
                active users across teams
              </p>
            </div>
            <div className="rounded-[22px] border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-muted)] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[color:var(--color-text-subtle)]">
                Customer health
              </p>
              <p className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-[color:var(--color-text-main)]">
                {account.scat_score}
              </p>
              <p className="mt-1 text-sm text-[color:var(--color-text-subtle)]">
                SCAT score with NPS {account.nps_score.toFixed(1)}
              </p>
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <ProgressBar
              label="Automation adoption"
              value={account.automation_adoption_pct}
              displayValue={`${Math.round(account.automation_adoption_pct * 100)}%`}
            />
            <ProgressBar
              label="Usage growth QoQ"
              value={Math.max(0, Math.min(1, (account.usage_growth_qoq + 0.2) / 0.4))}
              displayValue={`${account.usage_growth_qoq >= 0 ? "+" : ""}${Math.round(account.usage_growth_qoq * 100)}%`}
              tone="mint"
            />
            <ProgressBar
              label="Response quality"
              value={Math.max(0, Math.min(1, 1 - account.avg_response_time / 10))}
              displayValue={`${account.avg_response_time.toFixed(1)} hrs avg`}
              tone="gold"
            />
            <ProgressBar
              label="Churn risk"
              value={account.risk_engine_score}
              displayValue={`${Math.round(account.risk_engine_score * 100)}%`}
              tone="gold"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {priorityCards.map((item) => (
              <div
                key={item.label}
                className="rounded-[22px] border border-[color:var(--color-border-soft)] bg-white/74 p-4"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[color:var(--color-text-subtle)]">
                  {item.label}
                </p>
                <p className="mt-3 text-base font-semibold text-[color:var(--color-text-main)]">
                  {item.value}
                </p>
              </div>
            ))}
          </div>

          <div className="rounded-[22px] border border-[color:var(--color-border-soft)] p-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-[color:var(--color-text-subtle)]">
              Operational metrics
            </p>
            <dl className="grid gap-3 text-sm sm:grid-cols-3">
              <div className="rounded-[18px] bg-[color:var(--color-surface-muted)] px-4 py-3">
                <dt className="text-[color:var(--color-text-subtle)]">Support tickets</dt>
                <dd className="mt-2 font-semibold text-[color:var(--color-text-main)]">
                  {account.tickets_last_quarter}
                </dd>
              </div>
              <div className="rounded-[18px] bg-[color:var(--color-surface-muted)] px-4 py-3">
                <dt className="text-[color:var(--color-text-subtle)]">Avg response time</dt>
                <dd className="mt-2 font-semibold text-[color:var(--color-text-main)]">
                  {account.avg_response_time.toFixed(1)} hours
                </dd>
              </div>
              <div className="rounded-[18px] bg-[color:var(--color-surface-muted)] px-4 py-3">
                <dt className="text-[color:var(--color-text-subtle)]">Preferred channel</dt>
                <dd className="mt-2 font-semibold text-[color:var(--color-text-main)]">
                  {account.preferred_channel}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </Card>

      <div className="grid gap-5">
        <Card eyebrow="CSM Notes" title="What the account team is hearing">
          <p className="rounded-[22px] bg-[color:var(--color-surface-muted)] px-4 py-4 text-sm leading-7 text-[color:var(--color-text-subtle)]">
            {account.crm_notes}
          </p>
        </Card>
        <Card eyebrow="Customer Signals" title="What should shape this QBR">
          <p className="rounded-[22px] bg-[color:var(--color-surface-muted)] px-4 py-4 text-sm leading-7 text-[color:var(--color-text-subtle)]">
            {account.feedback_summary}
          </p>
        </Card>
      </div>
    </div>
  );
}
