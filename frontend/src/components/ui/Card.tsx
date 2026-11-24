import React from "react";
import clsx from "clsx";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
  hoverable?: boolean;
  variant?: "default" | "glow" | "gradient" | "stat";
  glowColor?: "blue" | "violet" | "teal" | "emerald" | "rose";
}

const glowMap: Record<string, string> = {
  blue:    "glow-blue",
  violet:  "glow-violet",
  teal:    "glow-teal",
  emerald: "glow-emerald",
  rose:    "glow-rose",
};

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    { className, glass = true, hoverable = true, variant = "default", glowColor = "blue", children, ...props },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={clsx(
          // Base — rounded-2xl for a more modern premium look; relative required for gradient-border ::before
          "relative rounded-2xl border border-border p-5 shadow-sm",
          {
            "glass-panel": glass,
            "bg-card":     !glass,
            "premium-card": hoverable,
            "gradient-border": variant === "gradient",
            [glowMap[glowColor]]: variant === "glow",
          },
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";

