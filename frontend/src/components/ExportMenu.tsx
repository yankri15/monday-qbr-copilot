"use client";

import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { downloadMarkdown } from "@/lib/export";

type ExportMenuProps = {
  accountName: string;
  draft: string;
  onExportPdf: () => Promise<void>;
  isExportingPdf: boolean;
  onFeedback: (message: string) => void;
};

export function ExportMenu({
  accountName,
  draft,
  isExportingPdf,
  onExportPdf,
  onFeedback,
}: ExportMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (!menuRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
    };
  }, []);

  async function handlePdfExport() {
    await onExportPdf();
    onFeedback(`${accountName} QBR downloaded as PDF.`);
    setIsOpen(false);
  }

  function handleMarkdownExport() {
    downloadMarkdown(draft, accountName);
    onFeedback(`${accountName} QBR downloaded as Markdown.`);
    setIsOpen(false);
  }

  return (
    <div className="relative" ref={menuRef}>
      <Button
        variant="secondary"
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        disabled={!draft.trim() || isExportingPdf}
      >
        {isExportingPdf ? "Rendering PDF..." : "Export"}
      </Button>

      {isOpen ? (
        <div className="absolute bottom-[calc(100%+0.75rem)] right-0 z-30 w-64 rounded-[24px] border border-[color:var(--color-border-soft)] bg-white p-2 shadow-[0_28px_70px_rgba(21,30,61,0.18)]">
          <button
            type="button"
            onClick={handleMarkdownExport}
            className="flex w-full items-start gap-3 rounded-[18px] px-3 py-3 text-left transition hover:bg-[color:var(--color-surface-muted)]"
          >
            <span className="mt-1 h-2.5 w-2.5 rounded-full bg-[color:var(--color-brand-blue)]" />
            <span>
              <span className="block text-sm font-semibold text-[color:var(--color-text-main)]">
                Download as Markdown
              </span>
              <span className="mt-1 block text-sm text-[color:var(--color-text-subtle)]">
                Save the draft as an editable `.md` file.
              </span>
            </span>
          </button>
          <button
            type="button"
            onClick={() => {
              void handlePdfExport();
            }}
            className="flex w-full items-start gap-3 rounded-[18px] px-3 py-3 text-left transition hover:bg-[color:var(--color-surface-muted)]"
          >
            <span className="mt-1 h-2.5 w-2.5 rounded-full bg-[color:var(--color-accent-mint-strong)]" />
            <span>
              <span className="block text-sm font-semibold text-[color:var(--color-text-main)]">
                Download as PDF
              </span>
              <span className="mt-1 block text-sm text-[color:var(--color-text-subtle)]">
                Download a shareable PDF copy of the current draft.
              </span>
            </span>
          </button>
          <div
            className="flex w-full items-start gap-3 rounded-[18px] px-3 py-3 opacity-55"
            title="Coming soon"
          >
            <span className="mt-1 h-2.5 w-2.5 rounded-full bg-[color:var(--color-text-subtle)]" />
            <span>
              <span className="block text-sm font-semibold text-[color:var(--color-text-main)]">
                Send via Email
              </span>
              <span className="mt-1 block text-sm text-[color:var(--color-text-subtle)]">
                Coming soon for the next iteration.
              </span>
            </span>
          </div>
        </div>
      ) : null}
    </div>
  );
}
