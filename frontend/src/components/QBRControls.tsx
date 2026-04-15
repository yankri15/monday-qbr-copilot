"use client";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { AudienceTone, FocusArea } from "@/lib/types";
import { cn } from "@/lib/utils";

const focusOptions: Array<{ value: FocusArea; label: string }> = [
  { value: "upsell_opportunity", label: "Upsell Opportunity" },
  { value: "churn_risk", label: "Churn Risk" },
  { value: "automation_adoption", label: "Automation Adoption" },
];

const toneOptions: Array<{ value: AudienceTone; label: string }> = [
  { value: "executive", label: "Executive" },
  { value: "team_lead", label: "Team Lead" },
  { value: "technical", label: "Technical" },
];

type QBRControlsProps = {
  focusAreas: FocusArea[];
  tone: AudienceTone;
  onFocusAreasChange: (nextFocusAreas: FocusArea[]) => void;
  onToneChange: (nextTone: AudienceTone) => void;
};

export function QBRControls({
  focusAreas,
  tone,
  onFocusAreasChange,
  onToneChange,
}: QBRControlsProps) {
  function toggleFocusArea(area: FocusArea) {
    if (focusAreas.includes(area)) {
      onFocusAreasChange(focusAreas.filter((entry) => entry !== area));
      return;
    }
    onFocusAreasChange([...focusAreas, area]);
  }

  return (
    <Card eyebrow="Draft Controls" title="Steer the QBR before generation">
      <div className="grid gap-5 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <p className="text-sm font-semibold text-[color:var(--color-text-main)]">
              Focus areas
            </p>
            {focusAreas.length ? (
              <Badge tone="brand">{focusAreas.length} selected</Badge>
            ) : (
              <Badge tone="neutral">Optional</Badge>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {focusOptions.map((option) => {
              const active = focusAreas.includes(option.value);
              return (
                <Button
                  key={option.value}
                  type="button"
                  variant={active ? "primary" : "secondary"}
                  size="sm"
                  onClick={() => toggleFocusArea(option.value)}
                  className={cn(
                    "rounded-full",
                    active && "shadow-[0_16px_28px_rgba(91,108,255,0.2)]",
                  )}
                >
                  {option.label}
                </Button>
              );
            })}
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-semibold text-[color:var(--color-text-main)]">
            Audience tone
          </p>
          <div className="flex flex-wrap gap-2">
            {toneOptions.map((option) => (
              <Button
                key={option.value}
                type="button"
                variant={tone === option.value ? "primary" : "secondary"}
                size="sm"
                onClick={() => onToneChange(option.value)}
                className="rounded-full"
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
