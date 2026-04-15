"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AccountSnapshot } from "@/components/AccountSnapshot";
import { QBRControls } from "@/components/QBRControls";
import { QBREditor } from "@/components/QBREditor";
import { ThoughtProcessPanel } from "@/components/ThoughtProcessPanel";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { fetchAccounts, generateQBR, refineQBR } from "@/lib/api";
import type {
  Account,
  AudienceTone,
  FocusArea,
  GenerateEvent,
  JudgeVerdict,
  QualInsights,
  QuantInsights,
  StepName,
  StepStatus,
  StrategicSynthesis,
} from "@/lib/types";

const defaultStepMessages: Record<StepName, string> = {
  quant_agent: "Queued to read the structured account signals.",
  qual_agent: "Queued to read CRM context and feedback.",
  strategist: "Queued to shape the recommendation angle.",
  csm_judge: "Queued to review the draft strategy against CSM standards.",
  editor: "Queued to assemble the final QBR draft.",
};

function getPrimaryMotion(account: Account) {
  if (account.risk_engine_score >= 0.45 || account.usage_growth_qoq < 0) {
    return {
      label: "Retention",
      tone: "danger" as const,
      description: "Protect adoption and remove friction before the next review.",
    };
  }

  if (account.automation_adoption_pct < 0.35) {
    return {
      label: "Adoption",
      tone: "warning" as const,
      description: "Expand usage by moving more workflows into Automations.",
    };
  }

  return {
    label: "Expansion",
    tone: "success" as const,
    description: "Use healthy momentum to widen the account story.",
  };
}

function createSteps(): Array<{
  name: StepName;
  label: string;
  message: string;
  status: StepStatus;
}> {
  return [
    {
      name: "quant_agent",
      label: "Data Read",
      message: defaultStepMessages.quant_agent,
      status: "idle",
    },
    {
      name: "qual_agent",
      label: "Context Read",
      message: defaultStepMessages.qual_agent,
      status: "idle",
    },
    {
      name: "strategist",
      label: "Recommendation",
      message: defaultStepMessages.strategist,
      status: "idle",
    },
    {
      name: "csm_judge",
      label: "CSM Review",
      message: defaultStepMessages.csm_judge,
      status: "idle",
    },
    {
      name: "editor",
      label: "Draft Builder",
      message: defaultStepMessages.editor,
      status: "idle",
    },
  ];
}

export function AccountWorkspace({ accountName }: { accountName: string }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [steps, setSteps] = useState(createSteps);
  const [quantitativeInsights, setQuantitativeInsights] = useState<QuantInsights>();
  const [qualitativeInsights, setQualitativeInsights] = useState<QualInsights>();
  const [strategicSynthesis, setStrategicSynthesis] = useState<StrategicSynthesis>();
  const [judgeVerdict, setJudgeVerdict] = useState<JudgeVerdict>();
  const [focusAreas, setFocusAreas] = useState<FocusArea[]>([]);
  const [tone, setTone] = useState<AudienceTone>("executive");

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        setIsLoading(true);
        setError(null);
        const accounts = await fetchAccounts();
        if (!active) {
          return;
        }
        const nextAccount = accounts.find(
          (entry) => entry.account_name.toLowerCase() === accountName.toLowerCase(),
        );

        if (!nextAccount) {
          setError(`We could not find an account named "${accountName}".`);
          setAccount(null);
          return;
        }

        setAccount(nextAccount);
      } catch (loadError) {
        if (!active) {
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "Failed to load account.");
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
  }, [accountName]);

  useEffect(() => {
    setFocusAreas([]);
    setTone("executive");
  }, [accountName]);

  const headerCopy = useMemo(() => {
    if (!account) {
      return {
        title: accountName,
        subtitle: "Review the account brief, generate the draft, then refine it in one place.",
      };
    }

    return {
      title: account.account_name,
      subtitle: `Prepare the next ${account.plan_type.toLowerCase()} QBR draft with clear account context, visible co-pilot support, and final human review.`,
    };
  }, [account, accountName]);

  const workspaceSummary = useMemo(() => {
    if (!account) {
      return [];
    }

    const motion = getPrimaryMotion(account);
    const topSignal =
      account.usage_growth_qoq < 0
        ? `${Math.round(account.usage_growth_qoq * 100)}% usage decline needs attention`
        : `${Math.round(account.usage_growth_qoq * 100)}% usage growth can support the story`;

    return [
      {
        label: "Primary motion",
        value: motion.label,
        supporting: motion.description,
        tone: motion.tone,
      },
      {
        label: "Top signal",
        value: topSignal,
        supporting: `${Math.round(account.automation_adoption_pct * 100)}% automation adoption`,
        tone: "brand" as const,
      },
      {
        label: "Preferred delivery",
        value: account.preferred_channel,
        supporting: "Use this channel for follow-up and next steps.",
        tone: "neutral" as const,
      },
    ];
  }, [account]);

  function applyEvent(event: GenerateEvent) {
    if (event.type === "STEP_STARTED") {
      setSteps((current) =>
        current.map((step) =>
          step.name === event.stepName
            ? {
                ...step,
                status: "running",
                message: event.message ?? step.message,
              }
            : step,
        ),
      );
      return;
    }

    if (event.type === "STEP_FINISHED") {
      setSteps((current) =>
        current.map((step) =>
          step.name === event.stepName ? { ...step, status: "completed" } : step,
        ),
      );
      return;
    }

    if (event.type === "STATE_DELTA") {
      for (const patch of event.delta) {
        if (patch.path === "/quantitative_insights") {
          setQuantitativeInsights(patch.value as QuantInsights);
        }
        if (patch.path === "/qualitative_insights") {
          setQualitativeInsights(patch.value as QualInsights);
        }
        if (patch.path === "/strategic_synthesis") {
          setStrategicSynthesis(patch.value as StrategicSynthesis);
        }
        if (patch.path === "/judge_verdict") {
          setJudgeVerdict(patch.value as JudgeVerdict);
        }
      }
      return;
    }

    if (event.type === "TEXT_MESSAGE_CONTENT") {
      setDraft(event.delta);
      return;
    }

    if (event.type === "RUN_ERROR") {
      setError(event.message);
    }
  }

  async function handleGenerate() {
    if (!account) {
      return;
    }

    setError(null);
    setIsGenerating(true);
    setDraft("");
    setSteps(createSteps());
    setQuantitativeInsights(undefined);
    setQualitativeInsights(undefined);
    setStrategicSynthesis(undefined);
    setJudgeVerdict(undefined);

    try {
      await generateQBR(
        {
          account_name: account.account_name,
          focus_areas: focusAreas,
          tone,
        },
        {
        onEvent: applyEvent,
        },
      );
    } catch (generationError) {
      setError(
        generationError instanceof Error
          ? generationError.message
          : "QBR generation failed.",
      );
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleRefine(instruction: string) {
    try {
      setError(null);
      setIsRefining(true);
      const refinedDraft = await refineQBR(draft, instruction);
      setDraft(refinedDraft);
    } catch (refinementError) {
      setError(
        refinementError instanceof Error
          ? refinementError.message
          : "Refinement failed.",
      );
      throw refinementError;
    } finally {
      setIsRefining(false);
    }
  }

  if (isLoading) {
    return <div className="h-[520px] animate-pulse rounded-[32px] bg-white/75" />;
  }

  if (!account) {
    return (
      <Card eyebrow="Account Not Found" title={accountName}>
        <div className="space-y-4">
          <p className="text-sm text-[color:var(--color-text-subtle)]">
            {error ?? "This account is unavailable right now."}
          </p>
          <Link href="/">
            <Button variant="secondary">Back to accounts</Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-[32px] border border-[color:var(--color-border-soft)] bg-white/78 px-6 py-6 shadow-[0_20px_64px_rgba(21,30,61,0.08)] backdrop-blur-sm lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-2">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm text-[color:var(--color-text-subtle)] transition hover:text-[color:var(--color-brand-blue)]"
          >
            <span aria-hidden="true">←</span>
            Back to accounts
          </Link>
          {account.account_source === "uploaded" ? (
            <Badge tone="brand">Uploaded account context</Badge>
          ) : null}
          <h1 className="text-4xl font-semibold tracking-[-0.06em] text-[color:var(--color-text-main)]">
            {headerCopy.title}
          </h1>
          <p className="max-w-3xl text-sm leading-7 text-[color:var(--color-text-subtle)] sm:text-base">
            {headerCopy.subtitle}
          </p>
        </div>

        <Button onClick={handleGenerate} disabled={isGenerating} className="min-w-[170px]">
          {isGenerating ? "Building draft..." : "Generate QBR draft"}
        </Button>
      </div>

      {workspaceSummary.length ? (
        <div className="grid gap-4 lg:grid-cols-3">
          {workspaceSummary.map((item) => (
            <Card key={item.label} className="bg-white/70">
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[0.72rem] font-semibold uppercase tracking-[0.22em] text-[color:var(--color-text-subtle)]">
                    {item.label}
                  </p>
                  <Badge tone={item.tone}>{item.value}</Badge>
                </div>
                <p className="text-sm leading-6 text-[color:var(--color-text-subtle)]">
                  {item.supporting}
                </p>
              </div>
            </Card>
          ))}
        </div>
      ) : null}

      <QBRControls
        focusAreas={focusAreas}
        tone={tone}
        onFocusAreasChange={setFocusAreas}
        onToneChange={setTone}
      />

      {error ? (
        <Card className="border-[color:var(--color-danger)]/18 bg-[color:var(--color-danger)]/7">
          <p className="text-sm text-[color:var(--color-danger)]">{error}</p>
        </Card>
      ) : null}

      <AccountSnapshot account={account} />

      <div className="grid gap-5 2xl:grid-cols-[0.95fr_1.05fr]">
        <ThoughtProcessPanel
          steps={steps}
          quantitativeInsights={quantitativeInsights}
          qualitativeInsights={qualitativeInsights}
          strategicSynthesis={strategicSynthesis}
          judgeVerdict={judgeVerdict}
        />
        <QBREditor
          accountName={account.account_name}
          draft={draft}
          onDraftChange={setDraft}
          onRefine={handleRefine}
          isRefining={isRefining}
        />
      </div>
    </div>
  );
}
