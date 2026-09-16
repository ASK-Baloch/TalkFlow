"use client";

import { Search, X, ArrowUpDown, Phone, Mail, CheckCircle, ShieldAlert } from "lucide-react";

export default function LeadListTable({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  onSort,
  filteredLeads,
  leads,
  onSelectLead,
}) {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-neutral-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by lead name, phone, email..."
            className="w-full rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] py-1.5 pl-9 pr-3 text-xs text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 outline-none transition-colors focus:border-blue-500 dark:focus:border-neutral-600"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-2.5 top-2.5 text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center overflow-x-auto rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-1 text-xs shadow-xs">
          {["all", "new", "contacted", "qualified", "converted", "unreachable", "dnc"].map(
            (st) => (
              <button
                key={st}
                type="button"
                onClick={() => onStatusFilterChange(st)}
                className={`capitalize rounded-md px-3 py-1 font-semibold transition-colors ${
                  statusFilter === st
                    ? "bg-blue-600 dark:bg-[#253246] text-white shadow-xs"
                    : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
                }`}
              >
                {st}
              </button>
            )
          )}
        </div>
      </div>

      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <div className="w-full overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-xs text-left">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800/80 text-neutral-600 dark:text-neutral-400 font-semibold uppercase tracking-wider text-[11px]">
                <th
                  onClick={() => onSort("id")}
                  className="px-4 py-3 cursor-pointer select-none hover:text-neutral-900 dark:hover:text-white"
                >
                  <div className="flex items-center gap-1">
                    <span>Lead ID</span>
                    <ArrowUpDown className="h-3 w-3 opacity-60" />
                  </div>
                </th>
                <th
                  onClick={() => onSort("firstName")}
                  className="px-4 py-3 cursor-pointer select-none hover:text-neutral-900 dark:hover:text-white"
                >
                  <div className="flex items-center gap-1">
                    <span>Name</span>
                    <ArrowUpDown className="h-3 w-3 opacity-60" />
                  </div>
                </th>
                <th className="px-4 py-3">Phone & Email</th>
                <th className="px-4 py-3">Campaign</th>
                <th
                  onClick={() => onSort("score")}
                  className="px-4 py-3 cursor-pointer select-none hover:text-neutral-900 dark:hover:text-white"
                >
                  <div className="flex items-center gap-1">
                    <span>Score</span>
                    <ArrowUpDown className="h-3 w-3 opacity-60" />
                  </div>
                </th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3">Last Contact</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {filteredLeads.map((lead) => (
                <tr
                  key={lead.id}
                  onClick={() => onSelectLead(lead.id)}
                  className="cursor-pointer transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                >
                  <td className="px-4 py-4 font-mono font-bold text-blue-600 dark:text-blue-400 hover:underline">
                    {lead.id}
                  </td>
                  <td className="px-4 py-4 font-bold text-neutral-900 dark:text-white">
                    {lead.firstName} {lead.lastName}
                    <span className="ml-1 text-[10px] font-normal text-neutral-400 dark:text-neutral-500">
                      ({lead.state})
                    </span>
                  </td>
                  <td className="px-4 py-4 font-mono text-[11px]">
                    <div className="flex items-center gap-1.5 text-neutral-800 dark:text-neutral-200">
                      <Phone className="h-3 w-3 text-neutral-400 shrink-0" />
                      <span>{lead.phone}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-neutral-500 dark:text-neutral-400 mt-0.5">
                      <Mail className="h-3 w-3 text-neutral-400 shrink-0" />
                      <span>{lead.email}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 font-semibold text-neutral-700 dark:text-neutral-300">
                    {lead.campaign}
                  </td>
                  <td className="px-4 py-4">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-bold ${
                        lead.score >= 80
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60"
                          : lead.score >= 50
                          ? "bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-blue-400 border border-blue-200 dark:border-blue-800/60"
                          : "bg-rose-50 text-rose-700 dark:bg-rose-950/80 dark:text-rose-400 border border-rose-200 dark:border-rose-800/60"
                      }`}
                    >
                      {lead.score} / 100
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    {lead.status === "Qualified" && (
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-300 dark:border-emerald-800/60 bg-emerald-50 dark:bg-emerald-950/70 px-2.5 py-0.5 text-xs font-bold text-emerald-700 dark:text-emerald-400">
                        <CheckCircle className="h-3 w-3" />
                        Qualified
                      </span>
                    )}
                    {lead.status === "Converted" && (
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-blue-300 dark:border-blue-800/60 bg-blue-50 dark:bg-blue-950/70 px-2.5 py-0.5 text-xs font-bold text-blue-700 dark:text-blue-400">
                        Converted
                      </span>
                    )}
                    {lead.status === "Contacted" && (
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-300 dark:border-amber-800/60 bg-amber-50 dark:bg-amber-950/70 px-2.5 py-0.5 text-xs font-bold text-amber-700 dark:text-amber-400">
                        Contacted
                      </span>
                    )}
                    {lead.status === "New" && (
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-800/90 px-2.5 py-0.5 text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                        New
                      </span>
                    )}
                    {lead.status === "Unreachable" && (
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-purple-300 dark:border-purple-800/60 bg-purple-50 dark:bg-purple-950/70 px-2.5 py-0.5 text-xs font-bold text-purple-700 dark:text-purple-400">
                        Unreachable
                      </span>
                    )}
                    {lead.status === "DNC" && (
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-rose-300 dark:border-rose-800/60 bg-rose-50 dark:bg-rose-950/70 px-2.5 py-0.5 text-xs font-bold text-rose-700 dark:text-rose-400">
                        <ShieldAlert className="h-3 w-3" />
                        DNC
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4 text-neutral-500 dark:text-neutral-400">
                    {lead.createdAt}
                  </td>
                  <td className="px-4 py-4 text-neutral-500 dark:text-neutral-400">
                    {lead.lastContacted}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectLead(lead.id);
                      }}
                      className="inline-flex items-center gap-1 rounded-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-2.5 py-1 text-xs font-semibold text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                    >
                      <span>View History</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 pt-4 border-t border-neutral-200 dark:border-neutral-800/60 text-center text-xs font-medium text-neutral-500 dark:text-neutral-400">
          Showing {filteredLeads.length} of {leads.length} leads
        </div>
      </div>
    </div>
  );
}