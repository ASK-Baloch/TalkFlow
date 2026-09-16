"use client";

import { useState, useMemo } from "react";
import {
  INITIAL_SYSTEM_SERVICES,
  INITIAL_SYSTEM_ALERTS,
  INITIAL_INTEGRATION_FAILURES,
} from "@/data/system";
import { INITIAL_INTEGRATIONS, INITIAL_WEBHOOKS, INITIAL_API_KEYS } from "@/data";

// Central state + route parsing for SystemView.
// initialAction maps to /system sub-routes e.g. 'alerts', 'integrations', or 'health'/'overview' (default).
export function useSystemState(initialAction, onActionChange) {
  const [services, setServices] = useState(INITIAL_SYSTEM_SERVICES);
  const [alerts, setAlerts] = useState(INITIAL_SYSTEM_ALERTS);
  const [failureQueue, setFailureQueue] = useState(INITIAL_INTEGRATION_FAILURES);

  // Integrations State
  const [integrations, setIntegrations] = useState(INITIAL_INTEGRATIONS);
  const [webhooks, setWebhooks] = useState(INITIAL_WEBHOOKS);
  const [apiKeys, setApiKeys] = useState(INITIAL_API_KEYS);

  // Alert Filters & Modals
  const [severityFilter, setSeverityFilter] = useState("all");
  const [alertStatusFilter, setAlertStatusFilter] = useState("all");
  const [selectedAlert, setSelectedAlert] = useState(null);

  // Modals for Integrations
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyRole, setNewKeyRole] = useState("Lead Import Only");

  const [isTestModalOpen, setIsTestModalOpen] = useState(false);
  const [testWebhook, setTestWebhook] = useState(null);
  const [testResponse, setTestResponse] = useState(null);
  const [isTesting, setIsTesting] = useState(false);

  // Parse Sub-route Mode from initialAction (e.g. /system/alerts -> 'alerts')
  const routeInfo = useMemo(() => {
    if (!initialAction || initialAction === "health" || initialAction === "overview") {
      return { mode: "health" };
    }
    const parts = initialAction.split("/");
    return { mode: parts[0] };
  }, [initialAction]);

  const navigateToAction = (actionStr) => {
    if (onActionChange) {
      onActionChange(actionStr);
    }
  };

  // Toggle Integration Status
  const toggleIntegration = (id) => {
    setIntegrations((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              status: item.status === "connected" ? "disconnected" : "connected",
            }
          : item
      )
    );
  };

  // Alert Actions
  const handleAcknowledgeAlert = (id) => {
    setAlerts((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, status: "ACKNOWLEDGED", acknowledgedBy: "it_ops_user" } : item
      )
    );
    if (selectedAlert && selectedAlert.id === id) {
      setSelectedAlert((prev) => ({ ...prev, status: "ACKNOWLEDGED", acknowledgedBy: "it_ops_user" }));
    }
  };

  const handleResolveAlert = (id) => {
    setAlerts((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, status: "RESOLVED", resolvedAt: new Date().toISOString() } : item
      )
    );
    if (selectedAlert && selectedAlert.id === id) {
      setSelectedAlert((prev) => ({ ...prev, status: "RESOLVED", resolvedAt: new Date().toISOString() }));
    }
  };

  // Filtered Alerts List
  const filteredAlerts = useMemo(() => {
    return alerts.filter((item) => {
      if (severityFilter !== "all" && item.severity !== severityFilter) return false;
      if (alertStatusFilter !== "all" && item.status !== alertStatusFilter) return false;
      return true;
    });
  }, [alerts, severityFilter, alertStatusFilter]);

  // Integration Failure Retry Action
  const handleRetryPush = (id) => {
    setFailureQueue((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              attempts: item.attempts + 1,
              lastAttemptAt: "Just now",
              status: "RESOLVED_RETRIED",
            }
          : item
      )
    );
  };

  // Create API Key
  const handleCreateApiKey = (e) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;

    const created = {
      id: `key-${Date.now()}`,
      name: newKeyName.trim(),
      prefix: `sb_live_${Math.floor(1000 + Math.random() * 9000)}...`,
      role: newKeyRole,
      created: "Just now",
      lastUsed: "Never",
    };

    setApiKeys((prev) => [created, ...prev]);
    setNewKeyName("");
    setIsKeyModalOpen(false);
  };

  // Webhook Test
  const executeWebhookTest = () => {
    setIsTesting(true);
    setTimeout(() => {
      setIsTesting(false);
      setTestResponse({
        status: 200,
        statusText: "OK",
        latency: "22ms",
        payload: {
          event: "system.health_ping",
          timestamp: new Date().toISOString(),
          subsystem: "AudioSocket RTP Gateway",
          status: "healthy",
        },
      });
    }, 600);
  };

  const openTestWebhook = (webhook) => {
    setTestWebhook(webhook);
    setTestResponse(null);
    setIsTestModalOpen(true);
  };

  const closeTestWebhook = () => {
    setIsTestModalOpen(false);
  };

  return {
    services,
    setServices,
    alerts,
    failureQueue,
    integrations,
    apiKeys,
    severityFilter,
    setSeverityFilter,
    alertStatusFilter,
    setAlertStatusFilter,
    selectedAlert,
    setSelectedAlert,
    isKeyModalOpen,
    setIsKeyModalOpen,
    newKeyName,
    setNewKeyName,
    newKeyRole,
    setNewKeyRole,
    isTestModalOpen,
    testWebhook,
    testResponse,
    isTesting,
    routeInfo,
    filteredAlerts,
    navigateToAction,
    toggleIntegration,
    handleAcknowledgeAlert,
    handleResolveAlert,
    handleRetryPush,
    handleCreateApiKey,
    executeWebhookTest,
    openTestWebhook,
    closeTestWebhook,
  };
}