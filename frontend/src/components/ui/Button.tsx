"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md";
  leadingIcon?: ReactNode;
};

export function Button({
  children,
  className,
  disabled,
  leadingIcon,
  size = "md",
  variant = "primary",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-full font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--color-brand-blue)]/40 disabled:cursor-not-allowed disabled:opacity-55",
        size === "md" ? "h-12 px-5 text-sm" : "h-10 px-4 text-sm",
        variant === "primary" &&
          "bg-[linear-gradient(135deg,var(--color-brand-blue),var(--color-brand-purple))] text-white shadow-[0_18px_30px_rgba(91,108,255,0.22)] hover:-translate-y-0.5 hover:shadow-[0_22px_38px_rgba(91,108,255,0.28)]",
        variant === "secondary" &&
          "border border-[color:var(--color-border-strong)] bg-white/90 text-[color:var(--color-text-main)] shadow-[0_14px_26px_rgba(30,37,66,0.08)] hover:border-[color:var(--color-brand-blue)]/30 hover:text-[color:var(--color-brand-blue)]",
        variant === "ghost" &&
          "text-[color:var(--color-text-subtle)] hover:bg-[color:var(--color-surface-muted)] hover:text-[color:var(--color-text-main)]",
        variant === "danger" &&
          "border border-[color:var(--color-danger)]/25 bg-[color:var(--color-danger)]/8 text-[color:var(--color-danger)] hover:bg-[color:var(--color-danger)]/14",
        className,
      )}
      disabled={disabled}
      {...props}
    >
      {leadingIcon}
      {children}
    </button>
  );
}
