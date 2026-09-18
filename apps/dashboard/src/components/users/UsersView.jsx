"use client";

import React, { useState, useEffect, useMemo } from "react";
import { apiFetch } from "@/lib/api";
import {
  Search,
  X,
  Shield,
  UserCheck,
  Server,
  BarChart3,
  ClipboardCheck,
  Megaphone,
  ArrowLeft,
  ArrowRight,
  Pencil,
  Trash2,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { LoadingSpinner } from "@/components/ui";

const ROLE_SLUG_MAP = {
  masterAdmin: "MASTER_ADMIN",
  verifierAgent: "VIEWER",
  itDevOps: "DEVOPS_IT",
  reportingUser: "REPORTING_USER",
  qaManager: "QA",
  campaignManager: "CAMPAIGN_MANAGER",
};

const EDITABLE_ROLES = [
  "MASTER_ADMIN",
  "DEVOPS_IT",
  "CAMPAIGN_MANAGER",
  "QA",
  "VIEWER",
  "REPORTING_USER",
];

const ROLE_CARDS = [
  {
    id: "master_admin",
    slug: "masterAdmin",
    name: "Master Admin",
    roleKey: "MASTER_ADMIN",
    description: "System administration, global settings, & full administrative privileges.",
    icon: Shield,
    badgeColor: "bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400 border-rose-500/20",
    iconBg: "bg-rose-500/15 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400",
    gradient: "hover:border-rose-500/50 hover:shadow-rose-500/5",
  },
  {
    id: "viewer",
    slug: "verifierAgent",
    name: "Viewer / Licensed Agent",
    roleKey: "VIEWER",
    description: "Medicare verifiers, licensed call agents & customer verification.",
    icon: UserCheck,
    badgeColor: "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400 border-emerald-500/20",
    iconBg: "bg-emerald-500/15 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400",
    gradient: "hover:border-emerald-500/50 hover:shadow-emerald-500/5",
  },
  {
    id: "devops_it",
    slug: "itDevOps",
    name: "IT / DevOps",
    roleKey: "DEVOPS_IT",
    description: "Technical infrastructure, telephony integrations & developer operations.",
    icon: Server,
    badgeColor: "bg-blue-500/10 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400 border-blue-500/20",
    iconBg: "bg-blue-500/15 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400",
    gradient: "hover:border-blue-500/50 hover:shadow-blue-500/5",
  },
  {
    id: "reporting_user",
    slug: "reportingUser",
    name: "Reporting User",
    roleKey: "REPORTING_USER",
    description: "Call performance metrics, report generation & analytics access.",
    icon: BarChart3,
    badgeColor: "bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400 border-amber-500/20",
    iconBg: "bg-amber-500/15 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400",
    gradient: "hover:border-amber-500/50 hover:shadow-amber-500/5",
  },
  {
    id: "qa",
    slug: "qaManager",
    name: "QA Manager",
    roleKey: "QA",
    description: "Quality assurance audits, call evaluation & compliance scoring.",
    icon: ClipboardCheck,
    badgeColor: "bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400 border-purple-500/20",
    iconBg: "bg-purple-500/15 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400",
    gradient: "hover:border-purple-500/50 hover:shadow-purple-500/5",
  },
  {
    id: "campaign_manager",
    slug: "campaignManager",
    name: "Campaign Manager",
    roleKey: "CAMPAIGN_MANAGER",
    description: "Dialer campaigns, lead routing, schedules & outbound lists.",
    icon: Megaphone,
    badgeColor: "bg-indigo-500/10 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400 border-indigo-500/20",
    iconBg: "bg-indigo-500/15 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400",
    gradient: "hover:border-indigo-500/50 hover:shadow-indigo-500/5",
  },
];

export default function UsersView({ initialAction, onActionChange }) {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [isAddModalOpen, setIsAddModalOpen] = useState(initialAction === "new");

  // Edit User Modal State
  const [editingUser, setEditingUser] = useState(null);
  const [editUsername, setEditUsername] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editFirstName, setEditFirstName] = useState("");
  const [editLastName, setEditLastName] = useState("");
  const [editRoles, setEditRoles] = useState([]);
  const [editError, setEditError] = useState("");
  const [editSuccess, setEditSuccess] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // Fetch approved users from the API
  const refreshUsers = async () => {
    try {
      const response = await apiFetch("/admin/users?status=APPROVED");
      if (response.ok) setUsers(await response.json());
    } catch {
      // API unreachable — leave existing state
    }
  };

  useEffect(() => {
    (async () => {
      setIsLoading(true);
      try {
        const response = await apiFetch("/admin/users?status=APPROVED");
        if (response.ok) setUsers(await response.json());
      } catch {
        // API unreachable — leave empty
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  // Derive selectedRole from URL action (e.g. /users/masterAdmin -> "MASTER_ADMIN")
  const selectedRole = useMemo(() => {
    if (!initialAction || initialAction === "new") return null;
    return ROLE_SLUG_MAP[initialAction] || null;
  }, [initialAction]);

  // Sync modal with URL action (/users/new), adjusting state during render
  // instead of in an effect to avoid an extra, visible render pass.
  const [prevInitialAction, setPrevInitialAction] = useState(initialAction);
  if (initialAction !== prevInitialAction) {
    setPrevInitialAction(initialAction);
    if (initialAction === "new") {
      setIsAddModalOpen(true);
    }
  }

  const handleRoleCardClick = (slug) => {
    if (onActionChange) {
      onActionChange(slug);
    }
  };

  const handleBackToRoles = () => {
    if (onActionChange) {
      onActionChange(null);
    }
    setSearchQuery("");
  };

  const handleOpenAddModal = () => {
    setIsAddModalOpen(true);
    if (onActionChange) onActionChange("new");
  };

  const handleCloseAddModal = () => {
    setIsAddModalOpen(false);
    if (onActionChange) onActionChange(null);
  };

  // Edit User handlers
  const handleOpenEditModal = (userToEdit) => {
    setEditingUser(userToEdit);
    setEditUsername(userToEdit.username || "");
    setEditEmail(userToEdit.email);
    setEditFirstName(userToEdit.firstName || "");
    setEditLastName(userToEdit.lastName || "");
    setEditRoles(userToEdit.roles || (userToEdit.role ? [userToEdit.role] : []));
    setEditError("");
    setEditSuccess("");
  };

  const handleSaveEditUser = async () => {
    setEditError("");
    setEditSuccess("");
    setIsSaving(true);
    try {
      const res = await apiFetch(`/admin/users/${editingUser.id}/update`, {
        method: "PATCH",
        body: JSON.stringify({
          username: editUsername.trim() || undefined,
          email: editEmail.trim() || undefined,
          first_name: editFirstName.trim() || undefined,
          last_name: editLastName.trim() || undefined,
          role_names: editRoles,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setEditError(data.detail || "Failed to update user");
        return;
      }
      setEditSuccess("User updated successfully");
      setEditingUser(null);
      await refreshUsers();
    } catch {
      setEditError("Network error — could not save");
    } finally {
      setIsSaving(false);
    }
  };

  // Delete User handler
  const handleDeleteUser = async (userId, userName) => {
    if (!confirm(`Delete user "${userName || "this user"}"? This cannot be undone.`)) return;
    try {
      const res = await apiFetch(`/admin/users/${userId}`, { method: "DELETE" });
      const data = await res.json();
      if (!res.ok) {
        alert(data.detail || "Failed to delete user");
        return;
      }
      await refreshUsers();
    } catch {
      alert("Network error — could not delete user");
    }
  };

  // Stats calculation
  const totalCount = users.length;
  const activeCount = users.filter((u) => u.status === "active").length;

  // Count users per role (check roles array then legacy role field)
  const getRoleUserCount = (roleKey) => {
    return users.filter((u) =>
      (u.roles || []).includes(roleKey) ||
      String(u.role || "").toUpperCase() === roleKey
    ).length;
  };

  // Filtered Users for Selected Role Table View
  const filteredUsers = useMemo(() => {
    let result = users;
    if (selectedRole) {
      result = result.filter(
        (u) =>
          (u.roles || []).includes(selectedRole) ||
          String(u.role || "").toUpperCase() === selectedRole
      );
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (u) =>
          String(u.username || "").toLowerCase().includes(q) ||
          String(u.email || "").toLowerCase().includes(q) ||
          String(u.firstName || "").toLowerCase().includes(q) ||
          String(u.lastName || "").toLowerCase().includes(q) ||
          String(u.type || "").toLowerCase().includes(q) ||
          String(u.role || "").toLowerCase().includes(q)
      );
    }
    return result;
  }, [users, selectedRole, searchQuery]);

  // New User Form State
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newFirstName, setNewFirstName] = useState("");
  const [newLastName, setNewLastName] = useState("");

  const handleCreateUser = (e) => {
    e.preventDefault();
    if (!newUsername.trim()) return;
    // Direct admin-created users bypass the pending queue (legacy /auth/register path)
    handleCloseAddModal();
    setNewUsername("");
    setNewPassword("");
    setNewEmail("");
    setNewFirstName("");
    setNewLastName("");
  };

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* 1. Header & Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            {selectedRole && (
              <button
                type="button"
                onClick={handleBackToRoles}
                className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] px-2.5 py-1 text-xs font-bold text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors mr-2"
                title="Back to All Role Cards"
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Back to Roles</span>
              </button>
            )}
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
              {selectedRole ? `Users — ${selectedRole}` : "User Role Directories"}
            </h1>
          </div>
          <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400 font-medium">
            {selectedRole
              ? `Showing ${filteredUsers.length} assigned user${filteredUsers.length === 1 ? "" : "s"} in ${selectedRole}`
              : `${totalCount} total approved users · Select a role card below to view users`}
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex w-full items-center justify-center py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          {/* 2. VIEW MODE 1: 6 ROLE CARDS OVERVIEW GRID */}
          {!selectedRole && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mt-2">
              {ROLE_CARDS.map((card) => {
                const Icon = card.icon;
                const userCount = getRoleUserCount(card.roleKey);

                return (
                  <div
                    key={card.id}
                    onClick={() => handleRoleCardClick(card.slug)}
                    className={`group relative flex flex-col justify-between rounded-xl border border-neutral-200 dark:border-neutral-800/90 bg-white dark:bg-[#0d0d0f] p-6 shadow-xs transition-all duration-200 hover:-translate-y-1 hover:shadow-xl cursor-pointer ${card.gradient}`}
                  >
                    <div>
                      {/* Top Bar inside Card */}
                      <div className="flex items-center justify-between">
                        <div
                          className={`flex h-11 w-11 items-center justify-center rounded-xl font-bold transition-transform duration-200 group-hover:scale-105 ${card.iconBg}`}
                        >
                          <Icon className="h-5 w-5" />
                        </div>
                        <span
                          className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-extrabold ${card.badgeColor}`}
                        >
                          {userCount} {userCount === 1 ? "User" : "Users"}
                        </span>
                      </div>

                      {/* Card Title & Description */}
                      <h3 className="mt-4 text-base font-bold text-neutral-900 dark:text-white tracking-tight group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        {card.name}
                      </h3>
                      <p className="mt-1.5 text-xs text-neutral-500 dark:text-neutral-400 leading-relaxed">
                        {card.description}
                      </p>
                    </div>

                    {/* Card Footer Link */}
                    <div className="mt-6 flex items-center justify-between pt-4 border-t border-neutral-100 dark:border-neutral-800/60">
                      <span className="text-xs font-bold text-neutral-700 dark:text-neutral-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        View Assigned Users
                      </span>
                      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 group-hover:bg-blue-600 group-hover:text-white dark:group-hover:bg-blue-500 transition-colors">
                        <ArrowRight className="h-3.5 w-3.5" />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* 3. VIEW MODE 2: FILTERED USERS TABLE VIEW */}
          {selectedRole && (
            <div className="flex flex-col gap-4">
              {/* Search Users Bar */}
              <div className="relative w-full max-w-md">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-neutral-400 dark:text-neutral-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={`Search within ${selectedRole}...`}
                  className="w-full rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] pl-9 pr-4 py-2 text-xs text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 outline-none focus:border-blue-500 dark:focus:border-neutral-700 transition-colors"
                />
              </div>

              {/* Users Table */}
              <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
                <div className="w-full overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
                  <table className="w-full min-w-[700px] border-collapse text-xs text-left">
                    <thead>
                      <tr className="border-b border-neutral-200 dark:border-neutral-800/80 bg-neutral-50 dark:bg-[#0a0a0c] text-neutral-600 dark:text-neutral-400 font-semibold text-[11px]">
                        <th className="px-4 py-3">Username</th>
                        <th className="px-4 py-3">Email</th>
                        <th className="px-4 py-3">Name</th>
                        <th className="px-4 py-3">ROLES</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="w-24 px-4 py-3 text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/70 bg-white dark:bg-[#0d0d0d]">
                      {filteredUsers.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="px-4 py-8 text-center text-neutral-500 dark:text-neutral-400 text-xs">
                            No users currently assigned to <strong>{selectedRole}</strong>.
                          </td>
                        </tr>
                      ) : (
                        filteredUsers.map((u) => (
                          <tr
                            key={u.id}
                            className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                          >
                            <td className="px-4 py-3.5 font-bold text-neutral-900 dark:text-white">
                              {u.username}
                            </td>
                            <td className="px-4 py-3.5 text-neutral-600 dark:text-neutral-300 font-mono">
                              {u.email}
                            </td>
                            <td className="px-4 py-3.5 text-neutral-800 dark:text-neutral-200">
                              {u.full_name || `${u.firstName || ""} ${u.lastName || ""}`.trim() || "—"}
                            </td>
                            <td className="px-4 py-3.5">
                              <div className="flex flex-wrap gap-1">
                                {(u.roles || (u.role ? [u.role] : [])).map((role) => (
                                  <span
                                    key={role}
                                    className="inline-block rounded-md bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800/50 px-2 py-0.5 text-[10px] font-bold text-blue-700 dark:text-blue-300"
                                  >
                                    {role}
                                  </span>
                                ))}
                              </div>
                            </td>
                            <td className="px-4 py-3.5">
                              <span className="inline-block rounded-full bg-emerald-100 dark:bg-emerald-950/80 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800">
                                {u.status || u.account_status || "APPROVED"}
                              </span>
                            </td>
                            <td className="px-4 py-3.5 text-center">
                              <div className="flex items-center justify-center gap-1.5">
                                <button
                                  type="button"
                                  onClick={() => handleOpenEditModal(u)}
                                  className="rounded-md p-1.5 text-neutral-400 hover:bg-neutral-100 hover:text-blue-600 dark:hover:bg-neutral-800 dark:hover:text-blue-400 transition-colors"
                                  title="Edit User"
                                >
                                  <Pencil className="h-3.5 w-3.5" />
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleDeleteUser(u.id, u.username || u.email)}
                                  className="rounded-md p-1.5 text-neutral-400 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/40 dark:hover:text-rose-400 transition-colors"
                                  title="Delete User"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* 4. EDIT USER MODAL */}
      {editingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <div>
                <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                  Edit User Profile
                </h3>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Update account details and assigned system role.
                </p>
              </div>
              <button
                onClick={() => setEditingUser(null)}
                className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {editError && (
              <div className="mb-4 flex items-center gap-2 rounded-lg border border-rose-900/50 bg-rose-950/40 p-3 text-xs font-medium text-rose-400">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{editError}</span>
              </div>
            )}

            {editSuccess && (
              <div className="mb-4 flex items-center gap-2 rounded-lg border border-emerald-900/50 bg-emerald-950/40 p-3 text-xs font-medium text-emerald-400">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>{editSuccess}</span>
              </div>
            )}

            <form onSubmit={(e) => { e.preventDefault(); handleSaveEditUser(); }} className="flex flex-col gap-4 text-xs">
              <div>
                <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={editUsername}
                  onChange={(e) => setEditUsername(e.target.value)}
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-2 text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                />
              </div>

              <div>
                <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={editEmail}
                  onChange={(e) => setEditEmail(e.target.value)}
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-2 text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={editFirstName}
                    onChange={(e) => setEditFirstName(e.target.value)}
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-2 text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                  />
                </div>

                <div>
                  <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={editLastName}
                    onChange={(e) => setEditLastName(e.target.value)}
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-2 text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Assigned Roles
                </label>
                <div className="flex flex-col gap-1.5 rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] p-2.5">
                  {EDITABLE_ROLES.map((roleName) => {
                    const checked = editRoles.includes(roleName);
                    if (roleName === "MASTER_ADMIN") {
                      return (
                        <label
                          key={roleName}
                          className="flex items-center gap-2 cursor-not-allowed opacity-70"
                          title="Reserved for the single system administrator account"
                        >
                          <input
                            type="checkbox"
                            checked={checked}
                            disabled
                            className="h-3.5 w-3.5 accent-blue-600"
                          />
                          <span className="font-semibold text-neutral-800 dark:text-neutral-200">
                            {roleName}
                            <span className="ml-1.5 text-[10px] font-bold text-neutral-500 dark:text-neutral-400">
                              (Reserved — single account)
                            </span>
                          </span>
                        </label>
                      );
                    }
                    return (
                      <label
                        key={roleName}
                        className="flex items-center gap-2 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={(e) => {
                            const updated = e.target.checked
                              ? [...editRoles, roleName]
                              : editRoles.filter((r) => r !== roleName);
                            setEditRoles(updated);
                          }}
                          className="h-3.5 w-3.5 accent-blue-600"
                        />
                        <span className="font-semibold text-neutral-800 dark:text-neutral-200">
                          {roleName}
                        </span>
                      </label>
                    );
                  })}
                </div>
                <p className="mt-1 text-[11px] text-neutral-500 dark:text-neutral-400">
                  MASTER_ADMIN is reserved for the single system administrator and cannot be assigned to other accounts.
                </p>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-800 mt-2">
                <button
                  type="button"
                  onClick={() => setEditingUser(null)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-800 px-4 py-2 font-bold text-neutral-700 dark:text-white hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="rounded-md bg-blue-600 text-white px-5 py-2 font-bold hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50"
                >
                  {isSaving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}