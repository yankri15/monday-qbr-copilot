"use client";

import { useMemo, useState } from "react";
import Markdown from "react-markdown";

import { ExportMenu } from "@/components/ExportMenu";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { exportPdf } from "@/lib/api";

type QBREditorProps = {
  accountName: string;
  draft: string;
  onDraftChange: (nextDraft: string) => void;
  onRefine: (instruction: string) => Promise<void>;
  isRefining: boolean;
};

export function QBREditor({
  accountName,
  draft,
  isRefining,
  onDraftChange,
  onRefine,
}: QBREditorProps) {
  const [mode, setMode] = useState<"preview" | "edit">("preview");
  const [instruction, setInstruction] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isExportingPdf, setIsExportingPdf] = useState(false);

  const canRefine = instruction.trim().length > 0 && draft.trim().length > 0 && !isRefining;
  const wordCount = useMemo(() => {
    return draft.trim() ? draft.trim().split(/\s+/).length : 0;
  }, [draft]);

  async function handleRefine() {
    const trimmed = instruction.trim();
    if (!trimmed) {
      return;
    }

    try {
      await onRefine(trimmed);
      setInstruction("");
      setFeedback("Draft refreshed.");
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "Refinement failed.");
    }
  }

  async function handleExportPdf() {
    try {
      setIsExportingPdf(true);
      await exportPdf(draft, accountName);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "PDF export failed.");
      throw error;
    } finally {
      setIsExportingPdf(false);
    }
  }

  return (
    <Card
      eyebrow="Final Deliverable"
      title="QBR Draft"
      actions={
        <div className="flex items-center gap-2">
          <Button
            variant={mode === "preview" ? "primary" : "secondary"}
            size="sm"
            onClick={() => setMode("preview")}
          >
            Preview
          </Button>
          <Button
            variant={mode === "edit" ? "primary" : "secondary"}
            size="sm"
            onClick={() => setMode("edit")}
          >
            Edit
          </Button>
        </div>
      }
      className="overflow-visible"
    >
      <div className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-[24px] bg-[color:var(--color-surface-muted)] px-4 py-3">
          <div className="text-sm text-[color:var(--color-text-subtle)]">
            Editable draft for the CSM to review, polish, and share.
          </div>
          <div className="font-mono text-xs text-[color:var(--color-text-subtle)]">
            {wordCount} words
          </div>
        </div>

        {mode === "preview" ? (
          <article className="prose prose-neutral max-w-none rounded-[24px] border border-[color:var(--color-border-soft)] bg-white px-5 py-6 text-sm leading-7 text-[color:var(--color-text-main)] shadow-[inset_0_1px_0_rgba(255,255,255,0.8)] prose-headings:tracking-[-0.03em] prose-headings:text-[color:var(--color-text-main)] prose-p:text-[color:var(--color-text-main)] prose-strong:text-[color:var(--color-text-main)] prose-li:text-[color:var(--color-text-main)]">
            <Markdown>{draft || "_No draft yet. Generate a QBR to start._"}</Markdown>
          </article>
        ) : (
          <textarea
            value={draft}
            onChange={(event) => onDraftChange(event.target.value)}
            className="min-h-[420px] w-full resize-y rounded-[24px] border border-[color:var(--color-border-strong)] bg-white px-5 py-4 font-mono text-sm leading-7 text-[color:var(--color-text-main)] shadow-[inset_0_1px_0_rgba(255,255,255,0.8)] outline-none transition focus:border-[color:var(--color-brand-blue)] focus:ring-4 focus:ring-[color:var(--color-brand-blue)]/12"
            placeholder="Generated markdown will appear here."
          />
        )}

        <div className="rounded-[24px] border border-[color:var(--color-border-soft)] bg-[linear-gradient(180deg,rgba(255,255,255,0.92),rgba(241,244,255,0.95))] p-4">
          <label
            htmlFor="refine-instruction"
            className="mb-3 block text-sm font-semibold text-[color:var(--color-text-main)]"
          >
            Ask the co-pilot to revise the draft
          </label>
          <div className="flex flex-col gap-3 lg:flex-row">
            <input
              id="refine-instruction"
              value={instruction}
              onChange={(event) => setInstruction(event.target.value)}
              placeholder='Examples: "Make this more executive" or "Lean harder into expansion."'
              className="h-12 flex-1 rounded-full border border-[color:var(--color-border-strong)] bg-white px-4 text-sm text-[color:var(--color-text-main)] outline-none transition placeholder:text-[color:var(--color-text-subtle)] focus:border-[color:var(--color-brand-blue)] focus:ring-4 focus:ring-[color:var(--color-brand-blue)]/12"
            />
            <div className="flex gap-2">
              <Button onClick={handleRefine} disabled={!canRefine}>
                {isRefining ? "Refining..." : "Refine"}
              </Button>
              <ExportMenu
                accountName={accountName}
                draft={draft}
                onExportPdf={handleExportPdf}
                isExportingPdf={isExportingPdf}
                onFeedback={setFeedback}
              />
            </div>
          </div>
          {feedback ? (
            <p className="mt-3 text-sm text-[color:var(--color-text-subtle)]">{feedback}</p>
          ) : null}
        </div>
      </div>
    </Card>
  );
}
