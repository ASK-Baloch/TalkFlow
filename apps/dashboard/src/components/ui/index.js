"use client";

import React from "react";

// Re-export modular UI components
export { LoadingSpinner } from "./LoadingSpinner";
export { Card, CardHeader, CardTitle } from "./Card";
export { Modal, ModalFooter } from "./Modal";
export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
} from "./Table";

// Button Primitive
export function Button({ children, variant = "primary", size = "md", className = "", ...props }) {
  const base = "inline-flex items-center justify-center font-semibold rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800",
    secondary: "bg-neutral-100 text-neutral-800 hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700",
    outline: "border border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:bg-[#121215] dark:text-neutral-200 dark:hover:bg-neutral-800",
    danger: "bg-rose-600 text-white hover:bg-rose-700",
    ghost: "bg-transparent text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800",
  };
  const sizes = {
    sm: "px-2.5 py-1 text-xs",
    md: "px-3.5 py-2 text-xs",
    lg: "px-4 py-2.5 text-sm",
  };

  return (
    <button className={`${base} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`} {...props}>
      {children}
    </button>
  );
}

// Input Primitive
export function Input({ className = "", error, ...props }) {
  return (
    <input
      className={`w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-xs text-neutral-900 placeholder-neutral-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-neutral-800 dark:bg-[#121215] dark:text-white dark:placeholder-neutral-500 ${
        error ? "border-rose-500 focus:ring-rose-500/20" : ""
      } ${className}`}
      {...props}
    />
  );
}

// Textarea Primitive
export function Textarea({ className = "", ...props }) {
  return (
    <textarea
      className={`w-full rounded-md border border-neutral-300 bg-white p-3 text-xs text-neutral-900 placeholder-neutral-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-neutral-800 dark:bg-[#121215] dark:text-white ${className}`}
      {...props}
    />
  );
}

// Select Primitive
export function Select({ children, className = "", ...props }) {
  return (
    <select
      className={`w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-xs font-medium text-neutral-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-neutral-800 dark:bg-[#121215] dark:text-white ${className}`}
      {...props}
    >
      {children}
    </select>
  );
}

// Checkbox Primitive
export function Checkbox({ label, className = "", ...props }) {
  return (
    <label className="inline-flex items-center gap-2 text-xs font-medium text-neutral-700 dark:text-neutral-300 cursor-pointer">
      <input
        type="checkbox"
        className={`h-4 w-4 rounded border-neutral-300 text-blue-600 focus:ring-blue-500 dark:border-neutral-700 dark:bg-neutral-800 ${className}`}
        {...props}
      />
      {label && <span>{label}</span>}
    </label>
  );
}

// Switch Primitive
export function Switch({ checked, onChange, label, className = "" }) {
  return (
    <label className="inline-flex items-center gap-3 cursor-pointer">
      <div
        onClick={() => onChange && onChange(!checked)}
        className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${
          checked ? "bg-blue-600" : "bg-neutral-300 dark:bg-neutral-700"
        } ${className}`}
      >
        <span
          className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
            checked ? "translate-x-4.5" : "translate-x-1"
          }`}
        />
      </div>
      {label && <span className="text-xs font-medium text-neutral-700 dark:text-neutral-300">{label}</span>}
    </label>
  );
}

// Badge Primitive
export function Badge({ children, variant = "neutral", className = "" }) {
  const variants = {
    success: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-900/40",
    danger: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-900/40",
    warning: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-900/40",
    info: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-900/40",
    neutral: "bg-neutral-100 text-neutral-700 border-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:border-neutral-700",
  };

  return (
    <span className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-semibold ${variants[variant] || variants.neutral} ${className}`}>
      {children}
    </span>
  );
}

// Separator Primitive
export function Separator({ className = "" }) {
  return <div className={`h-px w-full bg-neutral-200 dark:bg-neutral-800 ${className}`} />;
}

// Skeleton Primitive
export function Skeleton({ className = "" }) {
  return <div className={`animate-pulse rounded bg-neutral-200 dark:bg-neutral-800 ${className}`} />;
}
