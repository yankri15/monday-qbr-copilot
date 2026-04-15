"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { fetchAccounts } from "@/lib/api";
import type { Account, AccountCardTone } from "@/lib/types";
import { accountNameToSlug } from "@/lib/utils";

function riskTone(score: number): AccountCardTone {
  if (score >= 0.65) {
    return "danger";
  }
  if (score >= 0.3) {
    return "warning";
  }
  return "success";
}

const toneCopy: Record<AccountCardTone, string> = {
  success: "Low risk",
  warning: "Watch closely",
  danger: "High risk",
};

const skeletonCardIndices = Array.from({ length: 5 }, (_, index) => index);

export function AccountDashboard() {
  const router = useRouter();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        setIsLoading(true);
        setError(null);
        const nextAccounts = await fetchAccounts();
        if (!active) {
          return;
        }
        setAccounts(nextAccounts);
      } catch (loadError) {
        if (!active) {
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "Failed to load accounts.");
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <section className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <Card className="overflow-hidden bg-[linear-gradient(135deg,rgba(91,108,255,0.98),rgba(111,63,245,0.92))] text-white">
          <div className="grid gap-6 lg:grid-cols-[1fr_0.56fr]">
            <div className="space-y-4">
              <p className="text-[0.76rem] font-semibold uppercase tracking-[0.28em] text-white/72">
                Command Center
              </p>
              <h2 className="max-w-2xl text-4xl font-semibold tracking-[-0.06em] text-white sm:text-5xl">
                Draft evidence-grounded QBRs without turning the CSM into a data mule.
              </h2>
              <p className="max-w-xl text-sm leading-7 text-white/78 sm:text-base">
                Start with a live customer snapshot, stream the agent’s reasoning in real
                time, and keep the final narrative editable so the human stays in control.
              </p>
            </div>
            <div className="grid gap-3 rounded-[28px] bg-white/10 p-4 backdrop-blur-sm">
              {[
                ["4-stage workflow", "Quant, qual, strategy, editor"],
                ["Live AG-UI stream", "Step progress + intermediate insights"],
                ["Human-in-loop", "Editable markdown and natural-language refinement"],
              ].map(([title, body]) => (
                <div key={title} className="rounded-[22px] border border-white/14 bg-white/8 p-4">
                  <p className="text-sm font-semibold text-white">{title}</p>
                  <p className="mt-1 text-sm leading-6 text-white/72">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </Card>

        <Card eyebrow="Workspace Status" title="What this screen gives the CSM">
          <div className="space-y-4">
            {[
              "Pick any customer and inspect all 13 account fields in context.",
              "Spot risk fast with a color-coded health signal right from the grid.",
              "Launch a draft, review the reasoning, then edit or refine before sharing.",
            ].map((line) => (
              <div key={line} className="flex gap-3 rounded-[22px] bg-[color:var(--color-surface-muted)] p-4">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-[color:var(--color-brand-blue)]" />
                <p className="text-sm leading-6 text-[color:var(--color-text-subtle)]">{line}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-[color:var(--color-text-subtle)]">
              Accounts
            </p>
            <h2 className="text-2xl font-semibold tracking-[-0.05em] text-[color:var(--color-text-main)]">
              Choose a customer to prepare the next QBR
            </h2>
          </div>
          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-[color:var(--color-text-subtle)]">
              <Spinner className="border-[color:var(--color-brand-blue)]/25 border-t-[color:var(--color-brand-blue)]" />
              Loading account data
            </div>
          ) : (
            <Badge tone="brand">{accounts.length} accounts ready</Badge>
          )}
        </div>

        {error ? (
          <Card className="border-[color:var(--color-danger)]/20 bg-[color:var(--color-danger)]/7">
            <p className="text-sm text-[color:var(--color-danger)]">{error}</p>
          </Card>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-2 2xl:grid-cols-3">
          {isLoading
            ? skeletonCardIndices.map((index) => (
                <div
                  key={`skeleton-${index}`}
                  className="h-[250px] animate-pulse rounded-[28px] border border-[color:var(--color-border-soft)] bg-white/75"
                />
              ))
            : accounts.map((account) => {
                const tone = riskTone(account.risk_engine_score);
                return (
                  <button
                    key={account.account_name}
                    type="button"
                    onClick={() => router.push(`/account/${accountNameToSlug(account.account_name)}`)}
                    className="group text-left"
                  >
                    <Card className="h-full transition duration-200 group-hover:-translate-y-1 group-hover:border-[color:var(--color-brand-blue)]/25 group-hover:shadow-[0_28px_70px_rgba(34,45,84,0.12)]">
                      <div className="space-y-5">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[color:var(--color-text-subtle)]">
                              {account.plan_type}
                            </p>
                            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.05em] text-[color:var(--color-text-main)]">
                              {account.account_name}
                            </h3>
                          </div>
                          <Badge tone={tone}>{toneCopy[tone]}</Badge>
                        </div>

                        <div className="grid gap-3 sm:grid-cols-2">
                          {[
                            ["Active users", account.active_users.toString()],
                            ["NPS", account.nps_score.toFixed(1)],
                            ["SCAT", account.scat_score.toFixed(0)],
                            ["Risk", `${Math.round(account.risk_engine_score * 100)}%`],
                          ].map(([label, value]) => (
                            <div
                              key={label}
                              className="rounded-[20px] bg-[color:var(--color-surface-muted)] px-4 py-3"
                            >
                              <p className="text-xs uppercase tracking-[0.16em] text-[color:var(--color-text-subtle)]">
                                {label}
                              </p>
                              <p className="mt-2 text-lg font-semibold text-[color:var(--color-text-main)]">
                                {value}
                              </p>
                            </div>
                          ))}
                        </div>

                        <div className="flex items-center justify-between text-sm text-[color:var(--color-text-subtle)]">
                          <span>Usage growth {Math.round(account.usage_growth_qoq * 100)}%</span>
                          <span>{account.preferred_channel}</span>
                        </div>
                      </div>
                    </Card>
                  </button>
                );
              })}
        </div>
      </section>
    </div>
  );
}
