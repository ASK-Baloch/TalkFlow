"use client";

import { Users, User, UserPlus, X } from "lucide-react";

export default function TeamAssignmentPanel({
  teamAssignments,
  selectedTeamCampaign,
  newAgentName,
  onOpenAssign,
  onCloseAssign,
  onNewAgentNameChange,
  onSubmitAssign,
}) {
  return (
    <>
      <div className="flex flex-col gap-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {teamAssignments.map((team) => (
            <div key={team.id} className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col justify-between gap-4">
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between border-b border-neutral-100 dark:border-neutral-800 pb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800/60 text-blue-600">
                      <Users className="h-4 w-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-neutral-900 dark:text-white">{team.campaignName}</h4>
                      <span className="text-xs text-neutral-500">{team.shift}</span>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-200">
                    {team.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-neutral-500 font-medium">Manager</span>
                    <p className="font-bold text-neutral-800 dark:text-neutral-200 mt-0.5">{team.manager}</p>
                  </div>
                  <div>
                    <span className="text-neutral-500 font-medium">Licensed Agents</span>
                    <p className="font-bold text-blue-600 mt-0.5">{team.agentsCount} Agents Assigned</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mt-2 bg-neutral-50 dark:bg-[#121215] p-3 rounded-lg border border-neutral-200 dark:border-neutral-800">
                  {team.agentsList.map((ag, idx) => (
                    <div key={idx} className="flex items-center gap-1.5 rounded-md border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-[#1a1a1e] px-2.5 py-1 text-xs">
                      <User className="h-3 w-3 text-neutral-400" />
                      <span className="font-semibold">{ag.name}</span>
                      <span className={`h-1.5 w-1.5 rounded-full ${ag.status === "In Call" ? "bg-emerald-500" : "bg-blue-500"}`} />
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end pt-2 border-t border-neutral-100 dark:border-neutral-800">
                <button
                  type="button"
                  onClick={() => onOpenAssign(team)}
                  className="inline-flex items-center gap-1.5 rounded-md border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-600 hover:bg-blue-100"
                >
                  <UserPlus className="h-3.5 w-3.5" />
                  <span>Assign Agent</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedTeamCampaign && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <h3 className="text-base font-bold">Assign Agent to {selectedTeamCampaign.campaignName}</h3>
              <button onClick={onCloseAssign} className="text-neutral-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>
            <form onSubmit={onSubmitAssign} className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-bold mb-1">Agent Full Name</label>
                <input
                  type="text"
                  required
                  value={newAgentName}
                  onChange={(e) => onNewAgentNameChange(e.target.value)}
                  placeholder="e.g. Alex Johnson"
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-2 text-xs outline-none"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-neutral-200 dark:border-neutral-800">
                <button type="button" onClick={onCloseAssign} className="px-3 py-1.5 text-xs text-neutral-500">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-1.5 text-xs font-bold bg-blue-600 text-white rounded-md">
                  Add Agent
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}