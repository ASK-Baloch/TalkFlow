import React from "react";
import DashboardView from "../../components/dashboard/DashboardView";

export const metadata = {
  title: "Dashboard Overview | EsperBots Analytics",
};

export default function DashboardRoutePage() {
  return (
    <main className="w-full">
      <DashboardView />
    </main>
  );
}