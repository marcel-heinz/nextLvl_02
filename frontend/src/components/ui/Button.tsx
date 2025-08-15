import React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
};

const base =
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-[#20B2AA] text-white hover:bg-[#1aa39b] focus-visible:ring-[#20B2AA]",
  secondary:
    "bg-white text-[#008B8B] border border-[#AFEEEE] hover:bg-[#F0FFFF]",
  ghost: "bg-transparent text-[#008B8B] hover:bg-[#F0FFFF]",
  outline: "bg-transparent text-[#008B8B] border border-[#008B8B] hover:bg-[#F0FFFF]",
};

const sizes: Record<NonNullable<ButtonProps["size"]>, string> = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-base",
};

export function Button({ variant = "primary", size = "md", className = "", ...props }: ButtonProps) {
  return (
    <button className={[base, variants[variant], sizes[size], className].join(" ")} {...props} />
  );
}


