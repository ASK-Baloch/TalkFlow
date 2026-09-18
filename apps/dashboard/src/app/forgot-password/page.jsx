"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Button, Input, LoadingSpinner } from "@/components/ui";
import { validateForgotPasswordForm } from "@/lib/validations/auth";
import {
  Mail,
  ArrowLeft,
  ArrowRight,
  Headphones,
  CheckCircle2,
  AlertCircle,
  Info,
  KeyRound,
} from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    setFieldErrors({});

    const validation = validateForgotPasswordForm({ email });
    if (!validation.success) {
      setFieldErrors(validation.errors);
      setErrorMsg("Please enter a valid email address.");
      return;
    }

    try {
      setIsSubmitting(true);
      // Simulate backend reset request delay
      await new Promise((resolve) => setTimeout(resolve, 500));
      setSuccessMsg(
        `Password reset link sent! Check ${email.trim()} for instructions to reset your password.`
      );
    } catch (err) {
      setErrorMsg(err.message || "Failed to send reset link. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center bg-neutral-950 px-4 py-8 text-neutral-100 font-sans selection:bg-emerald-500 selection:text-white overflow-hidden">
      {/* Background Decorative Gradients */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.12),transparent_50%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(59,130,246,0.1),transparent_50%)]" />

      {/* Main Forgot Password Card */}
      <div className="relative z-10 w-full max-w-md rounded-2xl border border-neutral-800 bg-[#0d0d0f]/90 p-6 sm:p-8 shadow-2xl backdrop-blur-xl transition-all my-auto">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg shadow-emerald-500/20">
            <KeyRound className="h-6 w-6" />
          </div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight text-white">
            Reset Your Password
          </h1>
          <p className="mt-1.5 text-xs text-neutral-400 max-w-xs">
            Enter your registered email address and we&apos;ll send you instructions to reset your password.
          </p>
        </div>



        {/* Banners */}
        {errorMsg && (
          <div className="mt-4 flex items-center gap-2.5 rounded-lg border border-rose-900/50 bg-rose-950/40 p-3 text-xs font-medium text-rose-400 animate-in fade-in-0">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="mt-4 flex items-start gap-2.5 rounded-lg border border-emerald-900/50 bg-emerald-950/40 p-3 text-xs font-medium text-emerald-400 animate-in fade-in-0">
            <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Form */}
        {!successMsg ? (
          <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-4" noValidate>
            <div>
              <label className="mb-1.5 block text-xs font-semibold text-neutral-300">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-neutral-500" />
                <Input
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (fieldErrors.email) setFieldErrors((prev) => ({ ...prev, email: undefined }));
                  }}
                  className={`pl-9 !bg-[#121215] !text-white caret-emerald-400 placeholder:text-neutral-500 focus:!border-emerald-500 ${
                    fieldErrors.email ? "border-rose-500 focus:border-rose-500" : "border-neutral-800"
                  }`}
                />
              </div>
              {fieldErrors.email && (
                <p className="mt-1 text-[11px] font-medium text-rose-400">{fieldErrors.email}</p>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={isSubmitting}
              className="mt-2 w-full font-bold shadow-lg shadow-emerald-600/20"
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="sm" className="text-white" />
                  <span>Sending Instructions...</span>
                </>
              ) : (
                <>
                  <span>Send Reset Link</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </Button>
          </form>
        ) : (
          <div className="mt-5 flex flex-col gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setSuccessMsg("");
                setEmail("");
              }}
              className="w-full text-xs font-semibold"
            >
              Send to another email
            </Button>
          </div>
        )}

        {/* Back to Sign In */}
        <div className="mt-5 text-center text-xs text-neutral-400">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 font-bold text-emerald-400 hover:text-emerald-300 hover:underline transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Return to Sign In</span>
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
