"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export function LoadingSpinner({ size = "md", className, ...props }) {
  const sizeClasses = {
    sm: "h-3.5 w-3.5 border-2",
    md: "h-5 w-5 border-2",
    lg: "h-8 w-8 border-3",
  };

  return (
    <div
      role="status"
      className={cn(
        "inline-block animate-spin rounded-full border-current border-t-transparent text-emerald-500 dark:text-emerald-400",
        sizeClasses[size] || sizeClasses.md,
        className
      )}
      {...props}
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}
