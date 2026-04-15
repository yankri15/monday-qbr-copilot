"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { UploadZone } from "@/components/UploadZone";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { fetchAccounts } from "@/lib/api";
import type { Account, AccountCardTone, UploadDataResponse } from "@/lib/types";
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
const workspaceTips = [
  "Start with the account that matters most for Monday's conversation.",
  "Use the co-pilot activity panel to explain why the draft is taking a given direction.",
  "Refine the final draft so it matches the audience and story you want to present.",
];

function formatPercent(value: number) {
  return `${value >= 0 ? "+" : ""}${Math.round(value * 100)}%`;
}

function getAccountMotion(account: Account): {
  tone: AccountCardTone;
  label: string;
  summary: string;
} {
  if (account.risk_engine_score >= 0.45 || account.usage_growth_qoq < 0) {
    return {
      tone: "danger",
      label: "Retention focus",
      summary: "Stabilize adoption and resolve friction before the next review.",
    };
  }

  if (account.automation_adoption_pct < 0.35) {
    return {
      tone: "warning",
      label: "Adoption push",
      summary: "Expand Work OS usage by moving teams toward Automations.",
    };
  }

  return {
    tone: "success",
    label: "Expansion angle",
    summary: "Turn healthy usage momentum into a stronger strategic narrative.",
  };
}

function mergeAccounts(currentAccounts: Account[], nextAccounts: Account[]) {
  const byName = new Map<string, Account>();

  for (const account of currentAccounts) {
    byName.set(account.account_name.toLowerCase(), account);
  }

  for (const account of nextAccounts) {
    byName.set(account.account_name.toLowerCase(), account);
  }

  return Array.from(byName.values()).sort((left, right) =>
    left.account_name.localeCompare(right.account_name),
  );
}

export function AccountDashboard() {
  const router = useRouter();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const uploadedCount = accounts.filter((account) => account.account_source === "uploaded").length;

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

  function handleUploadSuccess(payload: UploadDataResponse) {
    setAccounts((current) => mergeAccounts(current, payload.accounts));
    setError(null);
  }

  return (
    <div className="space-y-6">
      <section>
        <Card className="overflow-hidden bg-[linear-gradient(135deg,rgba(91,108,255,0.98),rgba(111,63,245,0.92))] text-white">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <Badge className="bg-white/16 text-white" tone="neutral">
                  Customer Success
                </Badge>
                <Badge className="bg-white/16 text-white" tone="neutral">
                  QBR preparation
                </Badge>
                <Badge className="bg-white/16 text-white" tone="neutral">
                  Human review
                </Badge>
              </div>

              <div className="group relative">
                <button
                  type="button"
                  className="inline-flex items-center gap-2 rounded-full border border-white/18 bg-white/12 px-3 py-2 text-sm font-medium text-white/92 transition hover:bg-white/18 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50"
                  aria-label="Show workspace tips"
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white/14 text-base leading-none">
                    *
                  </span>
                  Tips
                </button>

                <div className="pointer-events-none absolute right-0 top-[calc(100%+0.75rem)] z-20 w-[320px] rounded-[24px] border border-white/16 bg-[rgba(38,31,96,0.82)] p-4 opacity-0 shadow-[0_24px_60px_rgba(17,13,54,0.38)] backdrop-blur-xl transition duration-200 group-hover:pointer-events-auto group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:opacity-100">
                  <p className="text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-white/62">
                    Quick Tips
                  </p>
                  <div className="mt-3 space-y-3">
                    {workspaceTips.map((tip) => (
                      <div
                        key={tip}
                        className="flex gap-3 rounded-[18px] border border-white/10 bg-white/6 px-3 py-3"
                      >
                        <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-[#ffcb4d]" />
                        <p className="text-sm leading-6 text-white/84">{tip}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-[1fr_0.62fr]">
              <div className="space-y-4">
                <p className="text-[0.76rem] font-semibold uppercase tracking-[0.28em] text-white/72">
                  QBR Prep Workspace
                </p>
                <h2 className="max-w-3xl text-4xl font-semibold tracking-[-0.06em] text-white sm:text-5xl">
                  Pick an account, review the context, and let the co-pilot assemble the
                  first draft.
                </h2>
                <p className="max-w-2xl text-sm leading-7 text-white/78 sm:text-base">
                  Review the signals, shape the narrative, and refine the final QBR before
                  it goes out.
                </p>
              </div>

              <div className="grid gap-3 rounded-[28px] border border-white/14 bg-white/10 p-4 backdrop-blur-sm">
                {[
                  ["Pick the account", "Structured metrics and CRM notes in one place"],
                  ["Generate the draft", "Live co-pilot reasoning stays visible"],
                  ["Finalize with confidence", "Edit, refine, and export the final QBR"],
                ].map(([title, body], index) => (
                  <div
                    key={title}
                    className="flex items-start gap-3 rounded-[22px] border border-white/14 bg-white/8 p-4"
                  >
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/14 text-xs font-semibold text-white">
                      0{index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">{title}</p>
                      <p className="mt-1 text-sm leading-6 text-white/72">{body}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </Card>
      </section>

      <section className="space-y-4">
        <UploadZone onUploadSuccess={handleUploadSuccess} />

        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-[color:var(--color-text-subtle)]">
              Accounts
            </p>
            <h2 className="text-2xl font-semibold tracking-[-0.05em] text-[color:var(--color-text-main)]">
              Choose the account and start building the next QBR
            </h2>
          </div>
          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-[color:var(--color-text-subtle)]">
              <Spinner className="border-[color:var(--color-brand-blue)]/25 border-t-[color:var(--color-brand-blue)]" />
              Loading account data
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              {uploadedCount ? <Badge tone="success">{uploadedCount} uploaded</Badge> : null}
              <Badge tone="brand">{accounts.length} accounts ready</Badge>
            </div>
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
                const motion = getAccountMotion(account);
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
                            <div className="flex flex-wrap items-center gap-2">
                              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[color:var(--color-text-subtle)]">
                                {account.plan_type}
                              </p>
                              <Badge tone={motion.tone}>{motion.label}</Badge>
                              {account.account_source === "uploaded" ? (
                                <Badge tone="brand">Uploaded</Badge>
                              ) : null}
                            </div>
                            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.05em] text-[color:var(--color-text-main)]">
                              {account.account_name}
                            </h3>
                            <p className="mt-2 max-w-[28rem] text-sm leading-6 text-[color:var(--color-text-subtle)]">
                              {motion.summary}
                            </p>
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

                        <div className="grid gap-3 rounded-[22px] border border-[color:var(--color-border-soft)] bg-white/70 p-4 sm:grid-cols-2">
                          <div>
                            <p className="text-xs uppercase tracking-[0.16em] text-[color:var(--color-text-subtle)]">
                              Growth signal
                            </p>
                            <p className="mt-2 text-sm font-semibold text-[color:var(--color-text-main)]">
                              {formatPercent(account.usage_growth_qoq)} usage growth QoQ
                            </p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-[0.16em] text-[color:var(--color-text-subtle)]">
                              Best follow-up channel
                            </p>
                            <p className="mt-2 text-sm font-semibold text-[color:var(--color-text-main)]">
                              {account.preferred_channel}
                            </p>
                          </div>
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
