"use client";

import { useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { uploadAccountsFile } from "@/lib/api";
import type { UploadDataResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

type UploadZoneProps = {
  onUploadSuccess: (payload: UploadDataResponse) => void;
};

const acceptedExtensions = ".xlsx,.csv";

export function UploadZone({ onUploadSuccess }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File | null) {
    if (!file) {
      return;
    }

    const lowerName = file.name.toLowerCase();
    if (!lowerName.endsWith(".xlsx") && !lowerName.endsWith(".csv")) {
      setError("Please upload an .xlsx or .csv customer file.");
      setStatus(null);
      return;
    }

    try {
      setIsUploading(true);
      setError(null);
      setStatus("Uploading and validating account data...");
      const payload = await uploadAccountsFile(file);
      onUploadSuccess(payload);
      setStatus(
        `${payload.accounts.length} account${payload.accounts.length === 1 ? "" : "s"} added from ${file.name}.`,
      );
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed.");
      setStatus(null);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <Card
      eyebrow="Optional Upload"
      title="Add customer data for the demo"
      className="bg-[linear-gradient(180deg,rgba(255,255,255,0.94),rgba(245,247,255,0.92))]"
    >
      <div className="space-y-4">
        <div
          className={cn(
            "rounded-[28px] border border-dashed px-6 py-7 transition",
            isDragging
              ? "border-[color:var(--color-brand-blue)] bg-[color:var(--color-brand-blue)]/6"
              : "border-[color:var(--color-border-strong)] bg-white/78",
          )}
          onDragEnter={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={(event) => {
            event.preventDefault();
            if (event.currentTarget.contains(event.relatedTarget as Node | null)) {
              return;
            }
            setIsDragging(false);
          }}
          onDrop={(event) => {
            event.preventDefault();
            setIsDragging(false);
            void handleFile(event.dataTransfer.files[0] ?? null);
          }}
        >
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="space-y-2">
              <p className="text-lg font-semibold tracking-[-0.03em] text-[color:var(--color-text-main)]">
                Drop a `.xlsx` or `.csv` customer sheet here
              </p>
              <p className="max-w-2xl text-sm leading-6 text-[color:var(--color-text-subtle)]">
                Use the same 13-column schema as the sample file. Uploaded accounts appear
                alongside the bundled demo accounts and can be used immediately in the QBR
                workspace.
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-3">
              {isUploading ? (
                <div className="flex items-center gap-2 text-sm text-[color:var(--color-text-subtle)]">
                  <Spinner className="border-[color:var(--color-brand-blue)]/25 border-t-[color:var(--color-brand-blue)]" />
                  Validating
                </div>
              ) : null}
              <input
                ref={inputRef}
                type="file"
                accept={acceptedExtensions}
                className="hidden"
                onChange={(event) => {
                  void handleFile(event.target.files?.[0] ?? null);
                  event.currentTarget.value = "";
                }}
              />
              <Button
                type="button"
                variant="secondary"
                onClick={() => inputRef.current?.click()}
                disabled={isUploading}
              >
                Choose file
              </Button>
            </div>
          </div>
        </div>

        {status ? (
          <p className="text-sm text-[color:var(--color-text-subtle)]">{status}</p>
        ) : null}
        {error ? <p className="text-sm text-[color:var(--color-danger)]">{error}</p> : null}
      </div>
    </Card>
  );
}
