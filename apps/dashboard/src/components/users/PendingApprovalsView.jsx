"use client";

import React, { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { LoadingSpinner } from "@/components/ui";
import {
  Clock,
  CheckCircle2,
  X,
  UserPlus,
  RefreshCw,
  AlertCircle,
  UserCheck,
  ShieldCheck,
} from "lucide-react";

const APPROVABLE_ROLES = [
  { name: "DEVOPS_IT", label: "IT / DevOps", color: "text-blue-600 dark:text-blue-400 border-blue-300 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/60" },
  { name: "CAMPAIGN_MANAGER", label: "Campaign Manager", color: "text-indigo-600 dark:text-indigo-400 border-indigo-300 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-950/60" },
  { name: "QA", label: "QA Manager", color: "text-purple-600 dark:text-purple-400 border-purple-300 dark:border-purple-800 bg-purple-50 dark:bg-purple-950/60" },
  { name: "VIEWER", label: "Verifier / Licensed Agent", color: "text-emerald-600 dark:text-emerald-400 border-emerald-300 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/60" },
];

export default function PendingApprovalsView() {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [selectedRoles, setSelectedRoles] = useState({});
  const [isApproving, setIsApproving] = useState(null);

  const fetchRoles = useCallback(async () => {
    try {
      const response = await apiFetch("/roles");
      if (response.ok) {
        const data = await response.json();
        setRoles(data);
      }
    } catch {
      // Roles endpoint failure is non-fatal; fall back to static list
      setRoles([]);
    }
  }, []);

  const fetchPendingUsers = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg("");
    try {
      const response = await apiFetch("/admin/users?status=PENDING");
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to load pending approvals.");
      }
      const data = await response.json();
      setPendingUsers(data);
    } catch (err) {
      setErrorMsg(err.message || "Failed to load pending approvals.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Data fetch on mount: fetchPendingUsers/fetchRoles set loading/error
    // state before their awaits, which the rule can't distinguish from a
    // derived-state anti-pattern.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchPendingUsers();
    fetchRoles();
  }, [fetchPendingUsers, fetchRoles]);

  const handleRoleToggle = (userId, roleName) => {
    setSelectedRoles((prev) => {
      const current = prev[userId] || [];
      const exists = current.includes(roleName);
      return {
        ...prev,
        [userId]: exists
          ? current.filter((r) => r !== roleName)
          : [...current, roleName],
      };
    });
  };

  const handleApprove = async (user) => {
    const roleNameList = selectedRoles[user.id] || [];
    if (roleNameList.length === 0) {
      setErrorMsg(`Select at least one role for ${user.full_name || user.email}.`);
      return;
    }

    // Resolve role names -> ids from fetched roles
    const roleIds = roles
      .filter((r) => roleNameList.includes(r.name))
      .map((r) => r.id);

    if (roleIds.length === 0) {
      setErrorMsg("Could not resolve selected roles. Refresh and try again.");
      return;
    }

    setIsApproving(user.id);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const response = await apiFetch(`/admin/users/${user.id}/approve`, {
        method: "PATCH",
        body: JSON.stringify({ role_ids: roleIds }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to approve user.");
      }

      setSuccessMsg(`${user.full_name || user.email} approved & assigned: ${roleNameList.join(", ")}`);
      setPendingUsers((prev) => prev.filter((u) => u.id !== user.id));
      setSelectedRoles((prev) => ({ ...prev, [user.id]: undefined }));
    } catch (err) {
      setErrorMsg(err.message || "Failed to approve user.");
    } finally {
      setIsApproving(null);
    }
  };

  const handleReject = async (user) => {
    if (!confirm(`Reject the approval request for ${user.full_name || user.email}?`)) return;

    setErrorMsg("");
    setSuccessMsg("");
    try {
      const response = await apiFetch(`/admin/users/${user.id}/reject`, {
        method: "PATCH",
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to reject user.");
      }

      setSuccessMsg(`Rejected account request for ${user.full_name || user.email}.`);
      setPendingUsers((prev) => prev.filter((u) => u.id !== user.id));
      setSelectedRoles((prev) => ({ ...prev, [user.id]: undefined }));
    } catch (err) {
      setErrorMsg(err.message || "Failed to reject user.");
    }
  };

  if (isLoading) {
    return (
      <div className="flex w-full items-center justify-center py-16">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Header Row */}
      <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3">
        <div>
          <h2 className="text-lg font-bold text-neutral-900 dark:text-white flex items-center gap-2">
            <Clock className="h-5 w-5 text-amber-500" />
            <span>Pending Approvals Queue</span>
          </h2>
          <p className="text-xs text-neutral-500">
            Review signup requests and assign roles to grant dashboard access.
          </p>
        </div>

        <button
          type="button"
          onClick={fetchPendingUsers}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-neutral-700 dark:text-neutral-300 bg-white dark:bg-[#0d0d0d] border border-neutral-300 dark:border-neutral-800 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Notification Banners */}
      {errorMsg && (
        <div className="flex items-start gap-2.5 rounded-lg border border-rose-900/50 bg-rose-950/40 p-3 text-xs font-medium text-rose-400">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="flex items-start gap-2.5 rounded-lg border border-emerald-900/50 bg-emerald-950/40 p-3 text-xs font-medium text-emerald-400">
          <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Empty State */}
      {pendingUsers.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] py-14 text-center px-6">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <h3 className="mt-3 text-sm font-bold text-neutral-900 dark:text-white">
            No Pending Approvals
          </h3>
          <p className="mt-1 text-xs text-neutral-500 max-w-sm">
            All registration requests have been processed. New signups will appear here once submitted.
          </p>
        </div>
      )}

      {/* Pending Users Cards */}
      <div className="flex flex-col gap-3">
        {pendingUsers.map((user) => (
          <div
            key={user.id}
            className="rounded-xl border border-amber-200 dark:border-amber-900/40 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400">
                  <UserPlus className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-bold text-neutral-900 dark:text-white">
                    {user.full_name || user.username || user.email}
                  </p>
                  <p className="mt-0.5 font-mono text-[11px] text-neutral-500">{user.email}</p>
                  <div className="mt-1.5 flex items-center gap-2">
                    <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-800 px-2 py-0.5 text-[10px] font-extrabold text-amber-700 dark:text-amber-400 uppercase">
                      <Clock className="h-3 w-3" />
                      PENDING
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Role Selector */}
            <div className="mt-4">
              <p className="text-[11px] font-bold text-neutral-600 dark:text-neutral-300 mb-2 flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-blue-500" />
                Select Role(s) to Assign
              </p>
              <div className="flex flex-wrap gap-2">
                {APPROVABLE_ROLES.map((role) => {
                  const isSelected = (selectedRoles[user.id] || []).includes(role.name);
                  return (
                    <button
                      key={role.name}
                      type="button"
                      onClick={() => handleRoleToggle(user.id, role.name)}
                      className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[11px] font-bold transition-all ${
                        isSelected
                          ? `${role.color} ring-2 ring-offset-1 ring-blue-500/50 dark:ring-blue-500/40`
                          : "border-neutral-300 dark:border-neutral-800 text-neutral-500 dark:text-neutral-400 hover:border-neutral-500 dark:hover:border-neutral-600"
                      }`}
                    >
                      {isSelected && <CheckCircle2 className="h-3.5 w-3.5" />}
                      {role.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Actions */}
            <div className="mt-4 flex items-center justify-end gap-2 border-t border-neutral-200 dark:border-neutral-800/70 pt-3">
              <button
                type="button"
                onClick={() => handleReject(user)}
                disabled={isApproving === user.id}
                className="inline-flex items-center gap-1.5 rounded-lg border border-rose-300 dark:border-rose-900/50 bg-rose-50 dark:bg-rose-950/40 px-3.5 py-2 text-[11px] font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-100 dark:hover:bg-rose-950 transition-colors disabled:opacity-50"
              >
                <X className="h-3.5 w-3.5" />
                <span>Reject</span>
              </button>
              <button
                type="button"
                onClick={() => handleApprove(user)}
                disabled={isApproving === user.id}
                className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-[11px] font-bold text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {isApproving === user.id ? (
                  <>
                    <LoadingSpinner size="sm" className="text-white" />
                    <span>Approving...</span>
                  </>
                ) : (
                  <>
                    <UserCheck className="h-4 w-4" />
                    <span>Approve & Assign Roles</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}