"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/context";
import { Clock, CheckCircle2, Headphones, LogIn } from "lucide-react";

export default function PendingApprovalPage() {
  const { isAuthenticated, status } = useAuth();

  const isRejected = status === "REJECTED";

  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center bg-neutral-950 px-4 py-8 text-neutral-100 font-sans selection:bg-emerald-500 selection:text-white overflow-y-auto">
      {/* Background Decorative Gradients */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.12),transparent_50%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(59,130,246,0.1),transparent_50%)]" />

      <div className="relative z-10 w-full max-w-md rounded-2xl border border-neutral-800 bg-[#0d0d0f]/90 p-6 sm:p-8 shadow-2xl backdrop-blur-xl text-center my-auto">
        {/* Brand Header */}
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg shadow-emerald-500/20 mx-auto">
          <Headphones className="h-6 w-6" />
        </div>

        {/* Status Icon */}
        <div className="mt-6 flex h-16 w-16 items-center justify-center rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 mx-auto animate-pulse">
          <Clock className="h-8 w-8" />
        </div>

        <h1 className="mt-5 text-xl font-bold tracking-tight text-white">
          Pending Approval
        </h1>
        <p className="mt-2 text-xs leading-relaxed text-neutral-400">
          Your account request has been submitted and is awaiting review. An administrator
          will approve your account and assign your system role. You will be able to sign in
          once your account is approved.
        </p>

        {/* Status Timeline */}
        <div className="mt-6 flex flex-col gap-3 text-left">
          <div className="flex items-start gap-3 rounded-lg border border-emerald-900/50 bg-emerald-950/40 p-3">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-emerald-300">Step 1 — Request Submitted</p>
              <p className="text-[11px] text-neutral-400 mt-0.5">Your account request was received successfully.</p>
            </div>
          </div>
          <div className="flex items-start gap-3 rounded-lg border border-amber-900/50 bg-amber-950/40 p-3 animate-pulse">
            <Clock className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-amber-300">Step 2 — Administrator Review</p>
              <p className="text-[11px] text-neutral-400 mt-0.5">
                An administrator (MASTER_ADMIN or IT/DevOps) is reviewing your request and
                will assign your role.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 rounded-lg border border-neutral-800 bg-[#141417] p-3 opacity-60">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-neutral-500 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-neutral-400">Step 3 — Sign In With Your Role</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">
                Once approved, sign in and you will only see the modules granted to your role.
              </p>
            </div>
          </div>
        </div>

        <Link
          href={isAuthenticated && isRejected ? "/login" : "/login"}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-xs font-bold text-white hover:bg-emerald-700 transition-colors"
        >
          <LogIn className="h-4 w-4" />
          <span>{isRejected ? "Back to Sign In" : "Go to Sign In"}</span>
        </Link>

        <div className="mt-4 text-center text-xs text-neutral-400">
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="font-bold text-emerald-400 hover:text-emerald-300 hover:underline transition-colors"
          >
            Create Account
          </Link>
        </div>
      </div>

      {/* Footer copyright */}
      <p className="mt-6 text-[11px] text-neutral-500">
        TalkFlow BPO System © 2026 SmartBrains IT Ops
      </p>
    </div>
  );
}