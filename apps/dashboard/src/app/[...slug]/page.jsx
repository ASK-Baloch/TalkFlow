import React from "react";
import { MainShell } from "@/components/layout";

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams?.slug || ["dashboard"];
  const rawTab = slug[0] === "dashboard" && slug[1] ? slug[1] : slug[0] || "dashboard";
  const action = slug[0] === "dashboard" && slug[2] ? slug[2] : (slug[1] || null);

  const tabName = rawTab.replace("_", " ").toUpperCase();
  const title = action
    ? `CREATE NEW | ${tabName} | TalkFlow Analytics`
    : `${tabName} | TalkFlow Analytics`;

  return {
    title,
  };
}

export default async function TopLevelSlugRoutePage({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams?.slug || ["dashboard"];

  let currentTab = "dashboard";
  let currentAction = null;

  if (slug[0] === "dashboard") {
    currentTab = slug[1] || "dashboard";
    currentAction = slug.length > 2 ? slug.slice(2).join("/") : null;
  } else {
    currentTab = slug[0] || "dashboard";
    currentAction = slug.length > 1 ? slug.slice(1).join("/") : null;
  }

  return (
    <main className="w-full min-h-screen">
      <MainShell initialTab={currentTab} initialAction={currentAction} />
    </main>
  );
}
