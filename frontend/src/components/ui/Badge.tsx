import React from "react";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  color?: "teal" | "gray" | "red" | "amber";
};

const palette: Record<NonNullable<BadgeProps["color"]>, string> = {
  teal: "bg-[#E0F7F7] text-[#008B8B]",
  gray: "bg-gray-100 text-gray-700",
  red: "bg-red-100 text-red-700",
  amber: "bg-amber-100 text-amber-800",
};

export function Badge({ color = "teal", className = "", ...props }: BadgeProps) {
  return (
    <span
      className={[
        "inline-flex items-center rounded px-2 py-0.5 text-xs font-medium",
        palette[color],
        className,
      ].join(" ")}
      {...props}
    />
  );
}


