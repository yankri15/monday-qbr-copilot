import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  title?: string;
  eyebrow?: string;
  actions?: ReactNode;
};

export function Card({
  actions,
  children,
  className,
  eyebrow,
  title,
  ...props
}: CardProps) {
  return (
    <section
      className={cn(
        "rounded-[28px] border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface)] shadow-[0_24px_70px_rgba(21,30,61,0.08)]",
        className,
      )}
      {...props}
    >
      {(title || eyebrow || actions) && (
        <div className="flex items-start justify-between gap-4 border-b border-[color:var(--color-border-soft)] px-6 py-5">
          <div className="space-y-1">
            {eyebrow ? (
              <p className="text-[0.72rem] font-semibold uppercase tracking-[0.24em] text-[color:var(--color-text-subtle)]">
                {eyebrow}
              </p>
            ) : null}
            {title ? (
              <h2 className="text-lg font-semibold tracking-[-0.03em] text-[color:var(--color-text-main)]">
                {title}
              </h2>
            ) : null}
          </div>
          {actions}
        </div>
      )}
      <div className="px-6 py-5">{children}</div>
    </section>
  );
}
