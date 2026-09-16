"use client";

import React from "react";
import { useLeadsState } from "./hooks/useLeadsState";
import LeadsHeader from "./components/LeadsHeader";
import LeadsSubtabsBar from "./components/LeadsSubtabsBar";
import LeadListTable from "./components/LeadListTable";
import LeadImportWizard from "./components/LeadImportWizard";
import LeadDetailView from "./components/LeadDetailView";
import SuppressionListView from "./components/SuppressionListView";
import LeadModals from "./components/LeadModals";

export default function LeadsView({ initialAction, onActionChange }) {
  const state = useLeadsState(initialAction, onActionChange);

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* 1. Header Title & Actions */}
      <LeadsHeader
        totalCount={state.totalCount}
        qualifiedCount={state.qualifiedCount}
        convertedCount={state.convertedCount}
        contactedCount={state.contactedCount}
        onImportClick={() => state.navigateToAction("import")}
        onAddClick={() => state.setIsAddModalOpen(true)}
      />

      {/* 2. Top Segmented Subtabs Bar */}
      <LeadsSubtabsBar viewMode={state.viewMode} onNavigate={state.navigateToAction} />

      {/* ========================================================================= */}
      {/* ROUTE 1: MAIN LEAD LIST TABLE (/leads) */}
      {/* ========================================================================= */}
      {state.viewMode === "list" && (
        <LeadListTable
          searchQuery={state.searchQuery}
          onSearchChange={state.setSearchQuery}
          statusFilter={state.statusFilter}
          onStatusFilterChange={state.setStatusFilter}
          onSort={state.handleSort}
          filteredLeads={state.filteredLeads}
          leads={state.leads}
          onSelectLead={state.navigateToAction}
        />
      )}

      {/* ========================================================================= */}
      {/* ROUTE 2: IMPORT WIZARD (/leads/import) */}
      {/* ========================================================================= */}
      {state.viewMode === "import" && (
        <LeadImportWizard
          onBack={() => state.navigateToAction(null)}
          importStep={state.importStep}
          onSetImportStep={state.setImportStep}
          uploadedFileName={state.uploadedFileName}
          onFileUpload={state.handleFileUpload}
          onStartImport={state.handleStartImport}
          importProgress={state.importProgress}
          onViewList={() => state.navigateToAction(null)}
        />
      )}

      {/* ========================================================================= */}
      {/* ROUTE 3: LEAD DETAIL + CALL HISTORY (/leads/[leadId]) */}
      {/* ========================================================================= */}
      {state.viewMode === "detail" && state.selectedLead && (
        <LeadDetailView
          lead={state.selectedLead}
          onBack={() => state.navigateToAction(null)}
        />
      )}

      {/* ========================================================================= */}
      {/* ROUTE 4: SUPPRESSION LIST / DNC (/leads/suppression) */}
      {/* ========================================================================= */}
      {state.viewMode === "suppression" && (
        <SuppressionListView
          suppressionList={state.suppressionList}
          onAddDnc={() => state.setIsDncModalOpen(true)}
        />
      )}

      {/* ========================================================================= */}
      {/* MODALS */}
      {/* ========================================================================= */}
      <LeadModals
        isAddModalOpen={state.isAddModalOpen}
        onCloseAddModal={() => state.setIsAddModalOpen(false)}
        newFirstName={state.newFirstName}
        onNewFirstName={state.setNewFirstName}
        newLastName={state.newLastName}
        onNewLastName={state.setNewLastName}
        newPhone={state.newPhone}
        onNewPhone={state.setNewPhone}
        newEmail={state.newEmail}
        onNewEmail={state.setNewEmail}
        newCampaign={state.newCampaign}
        onNewCampaign={state.setNewCampaign}
        newStatus={state.newStatus}
        onNewStatus={state.setNewStatus}
        onAddLeadSubmit={state.handleAddLead}
        isDncModalOpen={state.isDncModalOpen}
        onCloseDncModal={() => state.setIsDncModalOpen(false)}
        newDncPhone={state.newDncPhone}
        onNewDncPhone={state.setNewDncPhone}
        newDncReason={state.newDncReason}
        onNewDncReason={state.setNewDncReason}
        onAddDncSubmit={state.handleAddDnc}
      />
    </div>
  );
}