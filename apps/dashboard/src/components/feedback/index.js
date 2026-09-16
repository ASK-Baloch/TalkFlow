"use client";

import React, { useState } from "react";
import { AlertCircle, AlertTriangle, ShieldAlert, CheckCircle2, Lock, X } from "lucide-react";

// EmptyState Component
export function EmptyState({ title = "No data found", description = "There are no records matching your current filter.", actionLabel, onAction }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center border border-dashed border-neutral-300 dark:border-neutral-800 rounded-xl">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-neutral-100 text-neutral-400 dark:bg-neutral-800 mb-3">
        <AlertCircle className="h-6 w-6" />
      </div>
      <h3 className="text-sm font-bold text-neutral-900 dark:text-white">{title}</h3>
      <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="mt-4 rounded-md bg-blue-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

// ErrorState Component
export function ErrorState({ title = "Failed to load resource", message = "An error occurred while fetching data from backend API.", onRetry }) {
  return (
    <div className="rounded-xl border border-rose-200 bg-rose-50/60 p-6 dark:border-rose-900/40 dark:bg-rose-950/40 text-center space-y-3">
      <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-rose-100 text-rose-600 dark:bg-rose-900/60 dark:text-rose-300">
        <AlertTriangle className="h-5 w-5" />
      </div>
      <h3 className="text-sm font-bold text-rose-900 dark:text-rose-200">{title}</h3>
      <p className="text-xs text-rose-700 dark:text-rose-300 max-w-md mx-auto">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-md bg-rose-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-rose-700 transition-colors"
        >
          Retry Request
        </button>
      )}
    </div>
  );
}

// PermissionDenied Component
export function PermissionDenied({ roleName = "Your current role" }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-neutral-200 dark:border-neutral-800 rounded-xl bg-white dark:bg-[#09090b]">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400 mb-3">
        <Lock className="h-6 w-6" />
      </div>
      <h3 className="text-sm font-bold text-neutral-900 dark:text-white">Access Restricted</h3>
      <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-sm">
        {roleName} does not have authorized permissions to view or edit this resource per PRD §4.
      </p>
    </div>
  );
}

// DestructiveConfirmation Primitive (requires typed confirmation for irreversible actions per §10)
export function DestructiveConfirmation({ isOpen, title = "Confirm Destructive Action", description, expectedText = "DELETE", onConfirm, onClose }) {
  const [typedText, setTypedText] = useState("");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="w-full max-w-md rounded-xl border border-rose-200 bg-white p-6 shadow-2xl dark:border-rose-900/40 dark:bg-[#0d0d0f] space-y-4">
        <div className="flex items-center justify-between border-b border-neutral-100 pb-3 dark:border-neutral-800">
          <h3 className="text-sm font-bold text-rose-900 dark:text-rose-300 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-rose-600" /> {title}
          </h3>
          <button onClick={onClose} className="text-neutral-400 hover:text-neutral-600">
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className="text-xs text-neutral-600 dark:text-neutral-400">{description}</p>

        <div className="space-y-1.5 text-xs">
          <label className="block font-semibold text-neutral-800 dark:text-neutral-200">
            Type <span className="font-mono font-bold text-rose-600">{expectedText}</span> to confirm:
          </label>
          <input
            type="text"
            value={typedText}
            onChange={(e) => setTypedText(e.target.value)}
            placeholder={`Type ${expectedText}`}
            className="w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-xs font-mono font-bold text-neutral-900 dark:border-neutral-800 dark:bg-[#121215] dark:text-white focus:outline-none focus:ring-2 focus:ring-rose-500"
          />
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-neutral-300 px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-100 dark:border-neutral-800 dark:text-neutral-300"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={typedText.trim() !== expectedText}
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className="rounded-md bg-rose-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-rose-700 disabled:opacity-40 transition-colors"
          >
            Confirm Permanent Action
          </button>
        </div>
      </div>
    </div>
  );
}
