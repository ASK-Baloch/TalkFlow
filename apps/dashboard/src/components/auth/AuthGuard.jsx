"use client";

import React, { useEffect } from "react";
import { useAuth } from "@/context";
import { LoadingSpinner, Button } from "@/components/ui";
import { ShieldAlert, Lock, ArrowLeft, Clock } from "lucide-react";

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading, isPending } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  }, [loading, isAuthenticated]);

  if (loading) {
    return (
      <div className="flex min-h-screen w-full flex-col items-center justify-center bg-neutral-100 dark:bg-[#050505] text-neutral-900 dark:text-neutral-100">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return children;
}

export function PendingGuard({ children }) {
  const { isAuthenticated, isPending, loading } = useAuth();

  useEffect(() => {
    if (!loading && isAuthenticated && isPending) {
      if (typeof window !== "undefined") {
        const path = window.location.pathname;
        if (path !== "/pending-approval") {
          window.location.href = "/pending-approval";
        }
      }
    }
  }, [loading, isAuthenticated, isPending]);

  if (loading) return null;

  if (isPending) {
    const path = typeof window !== "undefined" ? window.location.pathname : "";
    if (path === "/pending-approval") {
      return children;
    }
    return null;
  }

  return children;
}

export function AdminGuard({ children, fallback }) {
  const { is_admin, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (!is_admin) {
    if (fallback) return fallback;

    return (
      <div className="flex min-h-[400px] w-full flex-col items-center justify-center rounded-xl border border-rose-200 bg-rose-50/40 p-8 text-center transition-colors dark:border-rose-900/30 dark:bg-rose-950/20">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-rose-100 text-rose-600 dark:bg-rose-900/40 dark:text-rose-400">
          <ShieldAlert className="h-7 w-7" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-neutral-900 dark:text-white">
          Access Restricted — Administrator Only
        </h2>
        <p className="mt-1 max-w-md text-xs text-neutral-600 dark:text-neutral-400">
          You do not have administrative privileges (`is_admin: true`) to view or modify this section. Please log in as a Master Admin or IT Admin.
        </p>
        <Button
          variant="secondary"
          size="sm"
          className="mt-6"
          onClick={() => {
            if (typeof window !== "undefined") window.location.href = "/dashboard";
          }}
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Return to Dashboard</span>
        </Button>
      </div>
    );
  }

  return children;
}

export function RoleGuard({ allowedRoles = [], children, fallback }) {
  const { role, roles: userRoles, loading } = useAuth();

  if (loading) return null;

  const hasRole =
    allowedRoles.length === 0 ||
    allowedRoles.some((r) => userRoles.includes(r) || role === r);

  if (!hasRole) {
    if (fallback) return fallback;

    return (
      <div className="flex min-h-[300px] w-full flex-col items-center justify-center rounded-xl border border-amber-200 bg-amber-50/40 p-6 text-center dark:border-amber-900/30 dark:bg-amber-950/20">
        <Lock className="h-8 w-8 text-amber-500" />
        <h3 className="mt-3 text-sm font-bold text-neutral-900 dark:text-white">
          Role Permission Required
        </h3>
        <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
          Required Roles: {allowedRoles.join(", ")} | Your Current Roles: {userRoles.join(", ") || role}
        </p>
      </div>
    );
  }

  return children;
}
