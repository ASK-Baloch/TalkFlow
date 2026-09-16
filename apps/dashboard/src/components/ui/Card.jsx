"use client";

import React from "react";

export function Card({ children, className = "", ...props }) {
  return (
    <div
      className={`rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition-colors duration-200 dark:border-[#1e1e1e] dark:bg-[#0d0d0d] ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = "", ...props }) {
  return (
    <div className={`mb-4 flex items-center justify-between ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = "", ...props }) {
  return (
    <h3 className={`text-sm font-bold text-neutral-800 dark:text-neutral-200 ${className}`} {...props}>
      {children}
    </h3>
  );
}
