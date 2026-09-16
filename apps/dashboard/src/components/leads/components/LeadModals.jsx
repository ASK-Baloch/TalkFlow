"use client";

import { X } from "lucide-react";

export default function LeadModals({
  isAddModalOpen,
  onCloseAddModal,
  newFirstName,
  onNewFirstName,
  newLastName,
  onNewLastName,
  newPhone,
  onNewPhone,
  newEmail,
  onNewEmail,
  newCampaign,
  onNewCampaign,
  newStatus,
  onNewStatus,
  newState,
  onNewState,
  onAddLeadSubmit,
  isDncModalOpen,
  onCloseDncModal,
  newDncPhone,
  onNewDncPhone,
  newDncReason,
  onNewDncReason,
  onAddDncSubmit,
}) {
  return (
    <>
      {/* Add Lead Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl text-neutral-900 dark:text-neutral-100">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                Add New Lead
              </h3>
              <button
                onClick={onCloseAddModal}
                className="text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={onAddLeadSubmit} className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    required
                    value={newFirstName}
                    onChange={(e) => onNewFirstName(e.target.value)}
                    placeholder="e.g. Alex"
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={newLastName}
                    onChange={(e) => onNewLastName(e.target.value)}
                    placeholder="e.g. Johnson"
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Phone Number
                </label>
                <input
                  type="text"
                  required
                  value={newPhone}
                  onChange={(e) => onNewPhone(e.target.value)}
                  placeholder="+1 (555) 000-0000"
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={newEmail}
                  onChange={(e) => onNewEmail(e.target.value)}
                  placeholder="alex.johnson@example.com"
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Campaign
                  </label>
                  <select
                    value={newCampaign}
                    onChange={(e) => onNewCampaign(e.target.value)}
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                  >
                    <option value="Med Fronter">Med Fronter</option>
                    <option value="Solar Outreach East">Solar Outreach East</option>
                    <option value="Insurance Renewals">Insurance Renewals</option>
                    <option value="Data Campaign">Data Campaign</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                    Status
                  </label>
                  <select
                    value={newStatus}
                    onChange={(e) => onNewStatus(e.target.value)}
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                  >
                    <option value="New">New</option>
                    <option value="Contacted">Contacted</option>
                    <option value="Qualified">Qualified</option>
                    <option value="Converted">Converted</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-800 mt-2">
                <button
                  type="button"
                  onClick={onCloseAddModal}
                  className="rounded-md px-3 py-1.5 text-xs text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-md bg-blue-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-blue-700"
                >
                  Save Lead
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add DNC Modal */}
      {isDncModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl text-neutral-900 dark:text-neutral-100">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                Add Phone Number to DNC List
              </h3>
              <button
                onClick={onCloseDncModal}
                className="text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={onAddDncSubmit} className="flex flex-col gap-3">
              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Phone Number to Block
                </label>
                <input
                  type="text"
                  required
                  value={newDncPhone}
                  onChange={(e) => onNewDncPhone(e.target.value)}
                  placeholder="+1 (555) 000-0000"
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Suppression Reason
                </label>
                <select
                  value={newDncReason}
                  onChange={(e) => onNewDncReason(e.target.value)}
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-1.5 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                >
                  <option value="Customer Request">Verbal Customer Opt-Out</option>
                  <option value="National DNC Match">National DNC Registry Match</option>
                  <option value="Litigation Risk">TCPA Attorney Litigation Risk</option>
                  <option value="Disconnected">Wrong Number / Disconnected</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-800 mt-2">
                <button
                  type="button"
                  onClick={onCloseDncModal}
                  className="rounded-md px-3 py-1.5 text-xs text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-md bg-rose-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-rose-700"
                >
                  Add to DNC List
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}