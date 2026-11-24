import React from "react";
import clsx from "clsx";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "success" | "warning" | "danger" | "info" | "neutral";
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = "neutral",
  children,
  ...props
}) => {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold select-none",
        {
          "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20": variant === "success",
          "bg-amber-500/15 text-amber-400 border border-amber-500/20": variant === "warning",
          "bg-rose-500/15 text-rose-400 border border-rose-500/20": variant === "danger",
          "bg-blue-500/15 text-blue-400 border border-blue-500/20": variant === "info",
          "bg-muted/30 text-muted-foreground border border-border": variant === "neutral",
        },
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
