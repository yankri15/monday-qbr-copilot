import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "neutral" | "success" | "warning" | "danger" | "brand";
};

export function Badge({
  children,
  className,
  tone = "neutral",
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold tracking-[0.02em]",
        tone === "neutral" &&
          "bg-[color:var(--color-surface-muted)] text-[color:var(--color-text-subtle)]",
        tone === "success" &&
          "bg-[color:var(--color-accent-mint)]/12 text-[color:var(--color-accent-mint-strong)]",
        tone === "warning" &&
          "bg-[color:var(--color-accent-gold)]/18 text-[color:var(--color-accent-gold-strong)]",
        tone === "danger" &&
          "bg-[color:var(--color-danger)]/12 text-[color:var(--color-danger)]",
        tone === "brand" &&
          "bg-[color:var(--color-brand-blue)]/12 text-[color:var(--color-brand-blue)]",
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
