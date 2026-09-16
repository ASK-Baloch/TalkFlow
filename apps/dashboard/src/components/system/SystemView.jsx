"use client";

import React from "react";
import { INITIAL_SYSTEM_SERVICES } from "@/data/system";
import { useSystemState } from "./hooks/useSystemState";
import SystemHealthView from "./components/SystemHealthView";
import SystemAlertsView from "./components/SystemAlertsView";
import SystemIntegrationsView from "./components/SystemIntegrationsView";
import SystemModals from "./components/SystemModals";

export default function SystemView({ initialAction, onActionChange }) {
  const state = useSystemState(initialAction, onActionChange);

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* ROUTE 1: /system (Health & Telemetry) */}
      {state.routeInfo.mode === "health" && (
        <SystemHealthView
          services={state.services}
          onRunDiagnostics={() => state.setServices([...INITIAL_SYSTEM_SERVICES])}
        />
      )}

      {/* ROUTE 2: /system/alerts */}
      {state.routeInfo.mode === "alerts" && (
        <SystemAlertsView
          filteredAlerts={state.filteredAlerts}
          severityFilter={state.severityFilter}
          alertStatusFilter={state.alertStatusFilter}
          onSeverityFilterChange={state.setSeverityFilter}
          onAlertStatusFilterChange={state.setAlertStatusFilter}
          onSelectAlert={(alert) => state.navigateToAction(null)}
          onAcknowledge={state.handleAcknowledgeAlert}
          onResolve={state.handleResolveAlert}
          onOpenDetails={(alert) => state.setSelectedAlert(alert)}
        />
      )}

      {/* ROUTE 3: /system/integrations */}
      {state.routeInfo.mode === "integrations" && (
        <SystemIntegrationsView
          integrations={state.integrations}
          onToggleIntegration={state.toggleIntegration}
          failureQueue={state.failureQueue}
          onRetryPush={state.handleRetryPush}
          webhooks={state.webhooks}
          onTestWebhook={state.openTestWebhook}
          onOpenCreateKey={() => state.setIsKeyModalOpen(true)}
        />
      )}

      {/* Shared Modals */}
      <SystemModals
        selectedAlert={state.selectedAlert}
        onCloseAlert={() => state.setSelectedAlert(null)}
        onAcknowledge={state.handleAcknowledgeAlert}
        onResolve={state.handleResolveAlert}
        isKeyModalOpen={state.isKeyModalOpen}
        onCloseKey={() => state.setIsKeyModalOpen(false)}
        newKeyName={state.newKeyName}
        onNewKeyName={state.setNewKeyName}
        newKeyRole={state.newKeyRole}
        onNewKeyRole={state.setNewKeyRole}
        onKeySubmit={state.handleCreateApiKey}
        isTestModalOpen={state.isTestModalOpen}
        onCloseTest={state.closeTestWebhook}
        testWebhook={state.testWebhook}
        testResponse={state.testResponse}
        isTesting={state.isTesting}
        onRunTest={state.executeWebhookTest}
      />
    </div>
  );
}