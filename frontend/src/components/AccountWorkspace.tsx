"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AccountSnapshot } from "@/components/AccountSnapshot";
import { QBREditor } from "@/components/QBREditor";
import { ThoughtProcessPanel } from "@/components/ThoughtProcessPanel";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { fetchAccounts, generateQBR, refineQBR } from "@/lib/api";
import type {
  Account,
  GenerateEvent,
  QualInsights,
  QuantInsights,
  StepName,
  StepStatus,
  StrategicSynthesis,
} from "@/lib/types";

const defaultStepMessages: Record<StepName, string> = {
  quant_agent: "Waiting to analyze structured account metrics.",
  qual_agent: "Waiting to extract qualitative themes from notes.",
  strategist: "Waiting to synthesize the account story.",
  editor: "Waiting to format the final markdown draft.",
};

function createSteps(): Array<{
  name: StepName;
  label: string;
  message: string;
  status: StepStatus;
}> {
  return [
    {
      name: "quant_agent",
      label: "Quant Agent",
      message: defaultStepMessages.quant_agent,
      status: "idle",
    },
    {
      name: "qual_agent",
      label: "Qual Agent",
      message: defaultStepMessages.qual_agent,
      status: "idle",
    },
    {
      name: "strategist",
      label: "Strategist",
      message: defaultStepMessages.strategist,
      status: "idle",
    },
    {
      name: "editor",
      label: "Editor",
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

  const headerCopy = useMemo(() => {
    if (!account) {
      return {
        title: accountName,
        subtitle: "Load the account snapshot, then draft and refine the QBR in one workspace.",
      };
    }

    return {
      title: account.account_name,
      subtitle: `Prepare the next ${account.plan_type.toLowerCase()} QBR with live agent reasoning, editable markdown, and a refinement loop.`,
    };
  }, [account, accountName]);

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

    try {
      await generateQBR(account.account_name, {
        onEvent: applyEvent,
      });
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
          <h1 className="text-4xl font-semibold tracking-[-0.06em] text-[color:var(--color-text-main)]">
            {headerCopy.title}
          </h1>
          <p className="max-w-3xl text-sm leading-7 text-[color:var(--color-text-subtle)] sm:text-base">
            {headerCopy.subtitle}
          </p>
        </div>

        <Button onClick={handleGenerate} disabled={isGenerating} className="min-w-[170px]">
          {isGenerating ? "Drafting..." : "Draft QBR"}
        </Button>
      </div>

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
        />
        <QBREditor
          draft={draft}
          onDraftChange={setDraft}
          onRefine={handleRefine}
          isRefining={isRefining}
        />
      </div>
    </div>
  );
}
