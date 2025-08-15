import React from "react";

export function Card({ className = "", ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={
        "rounded-lg border border-[#E0F7F7] bg-white shadow-sm " + className
      }
      {...props}
    />
  );
}

export function CardHeader({ className = "", ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={"px-4 py-3 border-b border-[#E0F7F7] " + className} {...props} />;
}

export function CardTitle({ className = "", ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={"text-base font-semibold text-[#008B8B] " + className} {...props} />;
}

export function CardContent({ className = "", ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={"px-4 py-3 text-sm text-gray-700 " + className} {...props} />;
}


